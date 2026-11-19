package edu.campus.recycle.integration;

import edu.campus.recycle.dto.ItemQuery;
import edu.campus.recycle.entity.Category;
import edu.campus.recycle.entity.Item;
import edu.campus.recycle.entity.TradeFlow;
import edu.campus.recycle.entity.User;
import edu.campus.recycle.exception.BusinessRuleException;
import edu.campus.recycle.exception.DuplicateEntityException;
import edu.campus.recycle.exception.PermissionDeniedException;
import edu.campus.recycle.exception.ValidationException;
import edu.campus.recycle.support.TestDatabase;
import edu.campus.recycle.util.DaoFactory;
import edu.campus.recycle.util.ItemEvent;
import edu.campus.recycle.util.ItemEventBus;
import edu.campus.recycle.util.ItemEventListener;
import edu.campus.recycle.util.ServiceFactory;
import org.junit.jupiter.api.AfterEach;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.io.TempDir;
import org.junit.jupiter.api.parallel.Isolated;

import java.math.BigDecimal;
import java.nio.file.Path;
import java.time.LocalDateTime;
import java.util.List;

import static org.junit.jupiter.api.Assertions.*;

@Isolated
class BusinessFlowTest {
    private final ServiceFactory services = ServiceFactory.getInstance();
    private final DaoFactory dao = DaoFactory.getInstance();
    @TempDir Path temp;
    private TestDatabase database;
    private int seller;
    private int buyer;
    private int admin;
    private int categoryId;

    @BeforeEach
    void initializeDatabase() {
        database = new TestDatabase(temp);
        seller = register("test_seller", "20260001").getId();
        buyer = register("test_buyer", "20260002").getId();
        User adminAccount = register("test_admin", "20260003");
        adminAccount.setRole("ADMIN");
        dao.getUserDao().update(adminAccount);
        admin = adminAccount.getId();

        Category category = new Category(null, "教材书籍", null, 0, true, LocalDateTime.now());
        dao.getCategoryDao().insert(category);
        categoryId = category.getId();
    }

    @AfterEach
    void restoreDatabase() {
        if (database != null) {
            database.close();
        }
    }

    @Test
    void credit59CannotPublishAnd60CanPublish() {
        services.getUserService().updateCredit(seller, -41, null, "测试发布阈值");
        var error = assertThrows(BusinessRuleException.class, () -> publish());
        assertEquals("BR-04", error.getCode());
        assertTrue(dao.getItemDao().findAll().isEmpty());

        services.getUserService().updateCredit(seller, 1, null, "到达发布阈值");
        assertEquals("PENDING", publish().getStatus());
    }

    @Test
    void publishedItemAppearsInSearchAfterAdminApproval() {
        Item item = publish();
        assertEquals("PENDING", storedItem(item.getId()).getStatus());
        assertNull(storedItem(item.getId()).getPublishedAt());

        ItemQuery query = new ItemQuery();
        query.setKeyword("集成测试");
        var before = services.getItemService().search(query);
        assertTrue(before.getRecords().isEmpty());
        assertEquals(0, before.getTotal());
        ItemQuery pending = new ItemQuery();
        pending.setStatus("PENDING");
        assertEquals(1, services.getItemService().search(pending).getTotal());
        services.getItemService().audit(admin, item.getId(), true, "验收通过");

        assertEquals("ON_SALE", storedItem(item.getId()).getStatus());
        assertNotNull(storedItem(item.getId()).getPublishedAt());
        assertEquals(List.of(item.getId()), services.getItemService().search(query).getRecords()
                .stream().map(Item::getId).toList());
    }

    @Test
    void sixImagesAreRejectedWithoutCreatingItem() {
        assertThrows(ValidationException.class, () -> services.getItemService().publish(item(),
                List.of("a.jpg", "b.jpg", "c.jpg", "d.jpg", "e.jpg", "f.jpg")));
        assertTrue(dao.getItemDao().findAll().isEmpty());
        assertTrue(dao.getItemImageDao().findAll().isEmpty());
    }

    @Test
    void publishAndAuditAppendDistinctOperationLogEntries() {
        var operationLogDao = dao.getOperationLogDao();
        int before = operationLogDao.findAll().size();
        Item item = onSale();
        var logs = operationLogDao.findAll();
        assertEquals(before + 2, logs.size());
        assertTrue(logs.stream().anyMatch(log -> "ITEM_PUBLISHED".equals(log.getOperation())
                && item.getId().equals(log.getTargetId()) && log.getOperatorId() == seller));
        assertTrue(logs.stream().anyMatch(log -> "ITEM_AUDITED".equals(log.getOperation())
                && item.getId().equals(log.getTargetId()) && log.getOperatorId() == admin));
    }

    @Test
    void favoriteToggleKeepsListAndCountInSync() {
        int itemId = onSale().getId();
        var favorites = services.getFavoriteService();
        assertTrue(favorites.toggle(buyer, itemId));
        assertEquals(List.of(itemId), favorites.listByUser(buyer).stream().map(Item::getId).toList());
        assertEquals(1, storedItem(itemId).getFavoriteCount());

        assertFalse(favorites.toggle(buyer, itemId));
        assertTrue(favorites.listByUser(buyer).isEmpty());
        assertEquals(0, storedItem(itemId).getFavoriteCount());
    }

    @Test
    void secondApplyIsRejectedWhileFirstFlowIsActive() {
        int itemId = onSale().getId();
        var trades = services.getTradeService();
        trades.apply(itemId, buyer, "希望流转");
        var error = assertThrows(BusinessRuleException.class,
                () -> trades.apply(itemId, buyer, "重复申请"));
        assertEquals("BR-05", error.getCode());
        assertEquals(1, dao.getTradeFlowDao().findAll().size());
    }

    @Test
    void buyerCannotAgreeAndCannotConfirmBeforeSellerAgrees() {
        var trades = services.getTradeService();
        TradeFlow flow = trades.apply(onSale().getId(), buyer, "希望流转");
        assertThrows(PermissionDeniedException.class, () -> trades.agree(flow.getId(), buyer));
        var error = assertThrows(BusinessRuleException.class, () -> trades.confirm(flow.getId(), buyer));
        assertEquals("BR-06", error.getCode());
        assertEquals("APPLYING", storedFlow(flow).getStatus());
        assertEquals("ON_SALE", storedItem(flow.getItemId()).getStatus());
    }

    @Test
    void buyerCanCancelAgreedFlowAndUnlockItem() {
        TradeFlow flow = agreedFlow();
        services.getTradeService().cancel(flow.getId(), buyer, "临时取消");
        assertEquals("CANCELLED", storedFlow(flow).getStatus());
        assertEquals("临时取消", storedFlow(flow).getCancelReason());
        assertEquals("ON_SALE", storedItem(flow.getItemId()).getStatus());
    }

    @Test
    void confirmCommitsFlowItemCreditAndOperationLog() {
        TradeFlow flow = agreedFlow();
        int before = dao.getOperationLogDao().findAll().size();
        services.getTradeService().confirm(flow.getId(), buyer);

        assertEquals("DONE", storedFlow(flow).getStatus());
        assertEquals("SOLD", storedItem(flow.getItemId()).getStatus());
        assertEquals(102, creditOf(seller));
        assertEquals(102, creditOf(buyer));
        assertEquals(2, dao.getCreditLogDao().findAll().size());
        var operationLogs = dao.getOperationLogDao().findAll();
        assertEquals(before + 1, operationLogs.size());
        assertTrue(operationLogs.stream().anyMatch(log -> "FLOW_DONE".equals(log.getOperation())
                && log.getOperatorId() == buyer));
    }

    @Test
    void confirmRollsBackFlowItemCreditAndOperationLogAfterListenerFails() {
        TradeFlow flow = agreedFlow();
        int before = dao.getOperationLogDao().findAll().size();
        RuntimeException failure = new IllegalStateException("成交事务测试注入故障");
        ItemEventListener listener = event -> {
            if (event.getType() == ItemEvent.Type.FLOW_DONE) {
                throw failure;
            }
        };

        var bus = ItemEventBus.getInstance();
        bus.register(listener);
        try {
            RuntimeException result = assertThrows(RuntimeException.class,
                    () -> services.getTradeService().confirm(flow.getId(), buyer));
            assertTrue(result == failure || result.getCause() == failure);
        } finally {
            bus.unregister(listener);
        }
        assertEquals("AGREED", storedFlow(flow).getStatus());
        assertNull(storedFlow(flow).getFinishedAt());
        assertEquals("LOCKED", storedItem(flow.getItemId()).getStatus());
        assertEquals(100, creditOf(seller));
        assertEquals(100, creditOf(buyer));
        assertTrue(dao.getCreditLogDao().findAll().isEmpty());
        assertEquals(before, dao.getOperationLogDao().findAll().size());
    }

    @Test
    void reviewRequiresDoneAndOnlyFirstLowScoreDeductsCredit() {
        TradeFlow flow = agreedFlow();
        var reviews = services.getReviewService();
        var error = assertThrows(BusinessRuleException.class,
                () -> reviews.review(flow.getId(), buyer, 2, "交接反馈"));
        assertEquals("BR-08", error.getCode());

        services.getTradeService().confirm(flow.getId(), buyer);
        reviews.review(flow.getId(), buyer, 2, "交接反馈");
        reviews.review(flow.getId(), seller, 5, "交接顺利");
        assertThrows(DuplicateEntityException.class,
                () -> reviews.review(flow.getId(), buyer, 1, "重复评价"));
        assertEquals(97, creditOf(seller));
        assertEquals(102, creditOf(buyer));
        assertEquals(2, dao.getReviewDao().findByFlowId(flow.getId()).size());
    }

    @Test
    void administratorOffShelfCancelsActiveFlow() {
        TradeFlow flow = agreedFlow();
        services.getItemService().offShelf(flow.getItemId(), admin);
        assertEquals("OFF_SHELF", storedItem(flow.getItemId()).getStatus());
        assertEquals("CANCELLED", storedFlow(flow).getStatus());
        assertFalse(storedFlow(flow).getCancelReason().isBlank());
    }

    @Test
    void statisticsCountOnlyCompletedFlowsAndUseConfiguredFactor() {
        TradeFlow completed = agreedFlow();
        services.getTradeService().confirm(completed.getId(), buyer);
        agreedFlow();
        dao.getSystemConfigDao().upsert("carbon.factor.book", "0.8", "测试减排系数");

        var stats = services.getStatisticService();
        LocalDateTime finishedAt = storedFlow(completed).getFinishedAt();
        var rows = stats.statisticsByCategory(finishedAt.minusMinutes(1), finishedAt.plusMinutes(1));
        assertEquals(1, rows.size());
        var books = rows.get(0);
        assertEquals("教材书籍", books.getCategoryName());
        assertEquals(1L, books.getFlowCount());
        assertEquals(new BigDecimal("20.00"), books.getTotalAmount());
        assertEquals(0.8, stats.carbonReduction(finishedAt.minusMinutes(1), finishedAt.plusMinutes(1)), 0.0001);
    }

    private User register(String username, String studentNumber) {
        return services.getUserService().register(username, "LocalTest123", "测试用户",
                studentNumber, null, null, null);
    }

    private Item item() {
        Item item = new Item();
        item.setOwnerId(seller);
        item.setCategoryId(categoryId);
        item.setTitle("集成测试教材");
        item.setDescription("九成新");
        item.setTradeType("SELL");
        item.setPrice(new BigDecimal("20.00"));
        item.setConditionLevel(9);
        return item;
    }

    private Item publish() {
        return services.getItemService().publish(item(), List.of());
    }

    private Item onSale() {
        var item = publish();
        services.getItemService().audit(admin, item.getId(), true, "测试审核");
        return storedItem(item.getId());
    }

    private TradeFlow agreedFlow() {
        var trades = services.getTradeService();
        TradeFlow flow = trades.apply(onSale().getId(), buyer, "希望流转");
        trades.agree(flow.getId(), seller);
        return flow;
    }

    private Item storedItem(int id) {
        return dao.getItemDao().findById(id).orElseThrow();
    }

    private TradeFlow storedFlow(TradeFlow flow) {
        return dao.getTradeFlowDao().findById(flow.getId()).orElseThrow();
    }

    private int creditOf(int userId) {
        return services.getUserService().findById(userId).getCreditScore();
    }
}
