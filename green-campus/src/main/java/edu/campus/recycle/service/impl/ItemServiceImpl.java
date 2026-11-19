package edu.campus.recycle.service.impl;

import edu.campus.recycle.dao.CategoryDao;
import edu.campus.recycle.dao.ItemDao;
import edu.campus.recycle.dao.ItemImageDao;
import edu.campus.recycle.dao.SystemConfigDao;
import edu.campus.recycle.dao.TradeFlowDao;
import edu.campus.recycle.dao.UserDao;
import edu.campus.recycle.dto.ItemQuery;
import edu.campus.recycle.dto.PageResult;
import edu.campus.recycle.entity.Category;
import edu.campus.recycle.entity.FlowStatus;
import edu.campus.recycle.entity.Item;
import edu.campus.recycle.entity.ItemImage;
import edu.campus.recycle.entity.ItemStatus;
import edu.campus.recycle.entity.Role;
import edu.campus.recycle.entity.TradeFlow;
import edu.campus.recycle.entity.TradeType;
import edu.campus.recycle.entity.User;
import edu.campus.recycle.exception.BusinessRuleException;
import edu.campus.recycle.exception.EntityNotFoundException;
import edu.campus.recycle.exception.PermissionDeniedException;
import edu.campus.recycle.exception.ValidationException;
import edu.campus.recycle.service.ItemService;
import edu.campus.recycle.util.DbUtil;
import edu.campus.recycle.util.ItemEvent;
import edu.campus.recycle.util.ItemEventBus;
import edu.campus.recycle.util.Validator;

import java.math.BigDecimal;
import java.time.LocalDateTime;
import java.util.ArrayList;
import java.util.List;
import java.util.Locale;
import java.util.Objects;
import java.util.logging.Logger;

/**
 * 物品服务实现。
 *
 * <p>发布物品与图片在同一事务内完成（BR-12 图片规则、BR-04 信用分门槛）；下架与审核
 * 保留操作痕迹并通过观察者写入操作日志。</p>
 */
public class ItemServiceImpl implements ItemService {

    private static final Logger LOG = Logger.getLogger(ItemServiceImpl.class.getName());

    /** 物品描述最大长度。 */
    public static final int DESCRIPTION_MAX = 500;

    private final ItemDao itemDao;
    private final ItemImageDao itemImageDao;
    private final CategoryDao categoryDao;
    private final UserDao userDao;
    private final TradeFlowDao tradeFlowDao;
    private final SystemConfigDao systemConfigDao;

    public ItemServiceImpl(ItemDao itemDao, ItemImageDao itemImageDao, CategoryDao categoryDao,
                           UserDao userDao, TradeFlowDao tradeFlowDao, SystemConfigDao systemConfigDao) {
        this.itemDao = Objects.requireNonNull(itemDao, "itemDao");
        this.itemImageDao = Objects.requireNonNull(itemImageDao, "itemImageDao");
        this.categoryDao = Objects.requireNonNull(categoryDao, "categoryDao");
        this.userDao = Objects.requireNonNull(userDao, "userDao");
        this.tradeFlowDao = Objects.requireNonNull(tradeFlowDao, "tradeFlowDao");
        this.systemConfigDao = Objects.requireNonNull(systemConfigDao, "systemConfigDao");
    }

    @Override
    public Item publish(Item item, List<String> imagePaths)
            throws ValidationException, BusinessRuleException {
        if (item == null) {
            throw ValidationException.of("物品信息不能为空");
        }
        Validator.checkTitle(item.getTitle());
        if (item.getDescription() != null && item.getDescription().length() > DESCRIPTION_MAX) {
            throw ValidationException.of("物品描述不能超过 " + DESCRIPTION_MAX + " 字");
        }
        List<String> paths = normalizeImages(imagePaths);
        if (item.getOwnerId() == null) {
            throw ValidationException.of("发布者不能为空");
        }
        User owner = userDao.findById(item.getOwnerId())
                .orElseThrow(() -> EntityNotFoundException.of("发布者不存在：id=" + item.getOwnerId()));
        int minCredit = systemConfigDao.getInt("credit.min_publish", 60);
        if (owner.getCreditScore() != null && owner.getCreditScore() < minCredit) {
            throw BusinessRuleException.of("BR-04",
                    "信用分低于 " + minCredit + "，暂不可发布物品（当前 " + owner.getCreditScore() + "）");
        }
        if (item.getCategoryId() == null) {
            throw ValidationException.of("请选择物品分类");
        }
        Category category = categoryDao.findById(item.getCategoryId())
                .orElseThrow(() -> EntityNotFoundException.of("分类不存在：id=" + item.getCategoryId()));
        if (!Boolean.TRUE.equals(category.getEnabled())) {
            throw BusinessRuleException.of("BR-06", "分类已停用，暂不可发布：" + category.getName());
        }
        if (item.getTradeType() == null || item.getTradeType().trim().isEmpty()) {
            item.setTradeType(TradeType.SELL.getCode());
        }
        if (item.getPrice() == null) {
            item.setPrice(BigDecimal.ZERO);
        }
        if (item.getPrice().signum() < 0) {
            throw ValidationException.of("价格不能为负数");
        }
        // 第 3 轮裁决 v1.1 §13-9 / BR-12 / FR-05：赠送（FREE）价格必须为 0，
        // 此处与 schema.sql 的 ck_item_free_price 构成"Service + DB 双层"校验。
        if (TradeType.FREE.getCode().equals(item.getTradeType()) && item.getPrice().signum() != 0) {
            throw ValidationException.of("赠送（FREE）物品的价格必须为 0 元");
        }
        // 第 3 轮裁决 v1.1 §13-8：未显式给状态时默认 PENDING（待审核），审核通过后才写入 published_at
        String status = item.getStatus() == null || item.getStatus().trim().isEmpty()
                ? ItemStatus.PENDING.getCode() : item.getStatus();
        LocalDateTime now = LocalDateTime.now().withNano(0);
        item.setStatus(status);
        item.setCreatedAt(now);
        item.setUpdatedAt(now);
        item.setPublishedAt(ItemStatus.ON_SALE.getCode().equals(status) ? now : null);
        item.setViewCount(0);
        item.setFavoriteCount(0);
        DbUtil.getInstance().executeInTransaction(conn -> {
            itemDao.insert(item);
            if (!paths.isEmpty()) {
                List<ItemImage> images = new ArrayList<>(paths.size());
                for (int i = 0; i < paths.size(); i++) {
                    ItemImage image = new ItemImage();
                    image.setItemId(item.getId());
                    image.setFilePath(paths.get(i));
                    image.setSortOrder(i);
                    image.setCreatedAt(now);
                    images.add(image);
                }
                itemImageDao.batchInsert(images);
            }
            ItemEventBus.getInstance().publish(
                    ItemEvent.item(ItemEvent.Type.ITEM_PUBLISHED, item, item.getOwnerId(), "发布物品：" + item.getTitle()));
            return null;
        });
        LOG.info(() -> "物品发布成功：itemId=" + item.getId() + "，图片 " + paths.size() + " 张");
        return item;
    }

    @Override
    public void updateItem(Item item, int operatorId) throws PermissionDeniedException, EntityNotFoundException {
        if (item == null || item.getId() == null) {
            throw ValidationException.of("待更新物品不能为空");
        }
        Item existing = itemDao.findById(item.getId())
                .orElseThrow(() -> EntityNotFoundException.of("物品不存在：id=" + item.getId()));
        boolean admin = isAdmin(operatorId);
        if (!admin && !Objects.equals(existing.getOwnerId(), operatorId)) {
            throw PermissionDeniedException.of("仅物品发布者或管理员可修改该物品");
        }
        Validator.checkTitle(item.getTitle());
        if (item.getDescription() != null && item.getDescription().length() > DESCRIPTION_MAX) {
            throw ValidationException.of("物品描述不能超过 " + DESCRIPTION_MAX + " 字");
        }
        item.setId(existing.getId());
        item.setOwnerId(existing.getOwnerId());
        item.setStatus(existing.getStatus());
        item.setPublishedAt(existing.getPublishedAt());
        item.setViewCount(existing.getViewCount());
        item.setFavoriteCount(existing.getFavoriteCount());
        item.setUpdatedAt(LocalDateTime.now().withNano(0));
        itemDao.update(item);
    }

    @Override
    public void offShelf(int itemId, int operatorId) throws PermissionDeniedException {
        Item item = itemDao.findById(itemId)
                .orElseThrow(() -> EntityNotFoundException.of("物品不存在：id=" + itemId));
        boolean admin = isAdmin(operatorId);
        if (!admin && !Objects.equals(item.getOwnerId(), operatorId)) {
            throw PermissionDeniedException.of("仅物品发布者或管理员可下架该物品");
        }
        if (ItemStatus.SOLD.getCode().equals(item.getStatus())
                || ItemStatus.OFF_SHELF.getCode().equals(item.getStatus())) {
            throw BusinessRuleException.of("BR-10", "当前状态不可下架：" + item.getStatus());
        }
        LocalDateTime now = LocalDateTime.now().withNano(0);
        DbUtil.getInstance().executeInTransaction(conn -> {
            tradeFlowDao.findActiveByItemId(itemId).ifPresent(flow ->
                    tradeFlowDao.updateStatus(flow.getId(), FlowStatus.CANCELLED.getCode(), "物品下架自动取消", now));
            itemDao.updateStatus(itemId, ItemStatus.OFF_SHELF.getCode(), "操作人下架");
            ItemEventBus.getInstance().publish(
                    ItemEvent.of(ItemEvent.Type.ITEM_OFF_SHELF, itemId, null, operatorId, "下架物品：" + item.getTitle()));
            return null;
        });
    }

    @Override
    public PageResult<Item> search(ItemQuery query) {
        ItemQuery effective = query == null ? new ItemQuery() : query;
        List<Item> records = itemDao.search(effective);
        long total = itemDao.countSearch(effective);
        return PageResult.of(records, total, Math.max(1, effective.getPageNo()), Math.max(1, effective.getPageSize()));
    }

    @Override
    public Item detail(int itemId) throws EntityNotFoundException {
        Item item = itemDao.findById(itemId)
                .orElseThrow(() -> EntityNotFoundException.of("物品不存在：id=" + itemId));
        itemDao.increaseViewCount(itemId);
        item.setViewCount((item.getViewCount() == null ? 0 : item.getViewCount()) + 1);
        return item;
    }

    @Override
    public void audit(int operatorId, int itemId, boolean pass, String remark) throws PermissionDeniedException {
        requireAdmin(operatorId);
        Item item = itemDao.findById(itemId)
                .orElseThrow(() -> EntityNotFoundException.of("物品不存在：id=" + itemId));
        if (ItemStatus.SOLD.getCode().equals(item.getStatus())) {
            throw BusinessRuleException.of("BR-10", "已成交物品不可再审核");
        }
        if (!ItemStatus.PENDING.getCode().equals(item.getStatus())
                && !ItemStatus.DRAFT.getCode().equals(item.getStatus())) {
            throw BusinessRuleException.of("BR-10", "仅待审核状态可审核，当前：" + item.getStatus());
        }
        LocalDateTime now = LocalDateTime.now().withNano(0);
        DbUtil.getInstance().executeInTransaction(conn -> {
            if (pass) {
                item.setStatus(ItemStatus.ON_SALE.getCode());
                item.setAuditRemark(remark);
                item.setUpdatedAt(now);
                if (item.getPublishedAt() == null) {
                    item.setPublishedAt(now);
                }
                itemDao.update(item);
            } else {
                itemDao.updateStatus(itemId, ItemStatus.REJECTED.getCode(), remark);
            }
            ItemEventBus.getInstance().publish(
                    ItemEvent.of(ItemEvent.Type.ITEM_AUDITED, itemId, null, operatorId,
                            (pass ? "审核通过：" : "审核驳回：") + item.getTitle()));
            return null;
        });
    }

    /**
     * 图片路径规整与后缀/数量校验（BR-12）。
     */
    private List<String> normalizeImages(List<String> imagePaths) {
        List<String> paths = new ArrayList<>();
        if (imagePaths != null) {
            for (String path : imagePaths) {
                if (path != null && !path.trim().isEmpty()) {
                    paths.add(path.trim());
                }
            }
        }
        if (paths.size() > Validator.MAX_IMAGE_COUNT) {
            throw ValidationException.of("图片最多上传 " + Validator.MAX_IMAGE_COUNT + " 张");
        }
        for (String path : paths) {
            String lower = path.toLowerCase(Locale.ROOT);
            if (!lower.endsWith(".jpg") && !lower.endsWith(".jpeg") && !lower.endsWith(".png")) {
                throw ValidationException.of("仅支持 jpg/jpeg/png 格式的图片：" + path);
            }
        }
        return paths;
    }

    private boolean isAdmin(int operatorId) {
        return userDao.findById(operatorId).map(u -> Role.ADMIN.getCode().equals(u.getRole())).orElse(false);
    }

    private User requireAdmin(int operatorId) throws PermissionDeniedException {
        User operator = userDao.findById(operatorId)
                .orElseThrow(() -> EntityNotFoundException.of("操作用户不存在：id=" + operatorId));
        if (!Role.ADMIN.getCode().equals(operator.getRole())) {
            throw PermissionDeniedException.of("仅管理员可执行该操作");
        }
        return operator;
    }
}
