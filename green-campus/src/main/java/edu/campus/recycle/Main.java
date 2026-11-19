package edu.campus.recycle;

import edu.campus.recycle.config.DatabaseInitializer;
import edu.campus.recycle.config.DbConfig;
import edu.campus.recycle.controller.ItemController;
import edu.campus.recycle.controller.ReviewController;
import edu.campus.recycle.controller.StatisticController;
import edu.campus.recycle.controller.TradeController;
import edu.campus.recycle.controller.UserController;
import edu.campus.recycle.dao.UserDao;
import edu.campus.recycle.dto.ItemQuery;
import edu.campus.recycle.dto.LoginResult;
import edu.campus.recycle.dto.PageResult;
import edu.campus.recycle.dto.StatisticsDTO;
import edu.campus.recycle.dto.TradeDetailDTO;
import edu.campus.recycle.dto.UserCreditDTO;
import edu.campus.recycle.entity.Category;
import edu.campus.recycle.entity.Item;
import edu.campus.recycle.entity.TradeFlow;
import edu.campus.recycle.entity.TradeType;
import edu.campus.recycle.entity.User;
import edu.campus.recycle.exception.AppException;
import edu.campus.recycle.exception.DuplicateEntityException;
import edu.campus.recycle.service.ItemService;
import edu.campus.recycle.service.StatisticService;
import edu.campus.recycle.service.UserService;
import edu.campus.recycle.util.DaoFactory;
import edu.campus.recycle.util.ServiceFactory;

import java.math.BigDecimal;
import java.nio.file.Path;
import java.time.LocalDateTime;
import java.util.List;
import java.util.logging.Logger;

/**
 * 控制台演示入口：初始化数据库 → 注册 → 登录 → 发布（待审核）→ 管理员审核 →
 * 检索 → 发起流转 → 同意 → 确认成交（跨表事务）→ 评价/收藏 → 统计与 CSV 导出。
 *
 * <p>第 3 轮裁决（v1.1）§13-8：物品默认 {@code PENDING}，必须经
 * {@code ItemService.audit(pass=true)} 审核通过（写入 {@code published_at}）后才能被检索与申请；
 * 演示因此插入"管理员审核"步骤，并改用 {@code controller} 包薄壳调用业务（界面层视角）。</p>
 *
 * <p>本演示在独立数据库文件 {@code data/greencampus.db} 上重建 schema 并导入
 * {@code db/seed-data.sql} 演示数据，不触碰任何验证库。</p>
 */
public final class Main {

    private static final Logger LOG = Logger.getLogger(Main.class.getName());

    private static final String DEMO_USERNAME = "demo_stu";
    private static final String DEMO_PASSWORD = "Demo@12345";
    private static final String DEMO_STUDENT_NO = "20239901";

    private Main() {
    }

    public static void main(String[] args) {
        System.out.println("============================================================");
        System.out.println(" 绿色校园闲置物品循环流转平台 · 迭代一（成员1 数据层 D7 骨架）");
        System.out.println(" 技术栈：Java 17 + SQLite(JDBC) + 手写 DAO + 工厂/策略/观察者/模板方法");
        System.out.println("============================================================");
        try {
            runDemo();
        } catch (AppException e) {
            System.out.println("[业务异常] code=" + e.getCode() + "，" + e.getUserMessage());
            LOG.warning(() -> "演示中断：" + e.getCode());
        } catch (RuntimeException e) {
            System.out.println("[运行异常] " + e.getMessage());
            LOG.warning(() -> "演示中断：" + e);
        }
    }

    private static void runDemo() {
        ServiceFactory factory = ServiceFactory.getInstance();
        UserService userService = factory.getUserService();
        ItemService itemService = factory.getItemService();
        StatisticService statisticService = factory.getStatisticService();
        UserDao userDao = DaoFactory.getInstance().getUserDao();

        // 控制器薄壳（界面层只依赖 controller，不直连 service/dao）
        UserController userController = new UserController();
        ItemController itemController = new ItemController();
        TradeController tradeController = new TradeController();
        ReviewController reviewController = new ReviewController();
        StatisticController statisticController = new StatisticController();

        // 1. 初始化数据库（执行 schema + seed）
        DbConfig config = DbConfig.getInstance();
        config.applyToDbUtil();
        DatabaseInitializer.initialize();
        System.out.println("[1/9] 数据库初始化完成：" + config.getJdbcUrl());
        System.out.println("      system_config 项数：" + config.loadSystemConfigMap().size());
        List<Category> categories = DaoFactory.getInstance().getCategoryDao().findEnabled();
        System.out.println("      可用分类数：" + categories.size()
                + "，示例：" + (categories.isEmpty() ? "-" : categories.get(0).getName()));

        // 2. 注册（重复执行时自动降级为复用已有用户）
        User demoUser;
        try {
            demoUser = userService.register(DEMO_USERNAME, DEMO_PASSWORD, "演示同学",
                    DEMO_STUDENT_NO, "STUDENT", "计算机学院", "demo@campus.edu.cn");
            System.out.println("[2/9] 注册成功：userId=" + demoUser.getId()
                    + "，初始信用分=" + demoUser.getCreditScore());
        } catch (DuplicateEntityException e) {
            demoUser = userDao.findByUsername(DEMO_USERNAME).orElseThrow(() -> e);
            System.out.println("[2/9] 用户已存在，复用：userId=" + demoUser.getId());
        }

        // 3. 登录（经 UserController，异常已转用户文案）
        LoginResult login = userController.login(DEMO_USERNAME, DEMO_PASSWORD);
        if (!login.isSuccess()) {
            throw new IllegalStateException("演示登录失败：" + login.getMessage());
        }
        System.out.println("[3/9] 登录成功：" + login.getUsername()
                + "，角色=" + login.getRole() + "，信用分=" + login.getCreditScore());

        // 4. 发布物品（不显式给状态 → 默认 PENDING 待审核；§13-8）
        Item item = new Item();
        item.setOwnerId(demoUser.getId());
        item.setCategoryId(categories.get(0).getId());
        item.setTitle("数据库系统概念（第 7 版）");
        item.setDescription("九成新，无笔记，适合《软件构造》前置课程复习。");
        item.setTradeType(TradeType.SELL.getCode());
        item.setPrice(new BigDecimal("45.00"));
        item.setOriginalPrice(new BigDecimal("89.00"));
        item.setConditionLevel(8);
        item.setTags("数据库,教材,计算机");
        Item published = itemService.publish(item, List.of("data/images/demo-book-1.jpg"));
        System.out.println("[4/9] 发布物品成功：itemId=" + published.getId()
                + "，状态=" + published.getStatus() + "（默认待审核）"
                + "，上架时间=" + published.getPublishedAt());

        // 5. 管理员审核通过 → ON_SALE 并写入 published_at（§13-8）
        User admin = userDao.findByUsername("admin")
                .orElseThrow(() -> new IllegalStateException("种子管理员 admin 不存在"));
        String auditMessage = itemController.audit(admin.getId(), published.getId(), true, "演示审核通过");
        Item audited = itemService.detail(published.getId());
        System.out.println("[5/9] " + auditMessage + "，当前状态=" + audited.getStatus()
                + "，上架时间=" + audited.getPublishedAt());

        // 6. 检索（默认排序 + 信用优先排序，§13-16）
        ItemQuery query = new ItemQuery();
        query.setKeyword("数据库");
        query.setPageSize(5);
        PageResult<Item> page = itemController.search(query);
        System.out.println("[6/9] 检索「数据库」命中 " + page.getTotal() + " 条，当前页 "
                + page.getRecords().size() + " 条：");
        for (Item record : page.getRecords()) {
            System.out.println("      - #" + record.getId() + " " + record.getTitle()
                    + " / " + record.getTradeType() + " / " + record.getPrice());
        }
        ItemQuery creditQuery = new ItemQuery();
        creditQuery.setTradeType(TradeType.SELL.getCode());
        creditQuery.setPageSize(3);
        creditQuery.setSortBy("CREDIT_FIRST");
        List<Item> creditFirst = itemController.search(creditQuery).getRecords();
        System.out.println("      信用优先排序（CREDIT_FIRST）前 " + creditFirst.size() + " 条：");
        for (Item record : creditFirst) {
            System.out.println("      * #" + record.getId() + " " + record.getTitle());
        }

        // 7. 发起流转（买家使用种子用户 zhangsan）+ 卖家同意
        User buyer = userDao.findByUsername("zhangsan")
                .orElseThrow(() -> new IllegalStateException("种子用户 zhangsan 不存在"));
        String applyMessage = tradeController.apply(published.getId(), buyer.getId(), "教材正需要，希望转让");
        TradeFlow flow = tradeController.history(demoUser.getId(), "APPLYING", 1, 1).stream()
                .filter(f -> f.getItemId() != null && f.getItemId().equals(published.getId()))
                .findFirst()
                .orElseThrow(() -> new IllegalStateException("未找到刚创建的流转"));
        System.out.println("[7/9] " + applyMessage + "；" + tradeController.agree(flow.getId(), demoUser.getId())
                + "，物品状态=" + itemService.detail(published.getId()).getStatus());

        // 8. 确认成交（跨表事务：物品 SOLD + 流转 DONE + 信用分 + 日志 + 统计）+ 评价/收藏
        int sellerCreditBefore = userService.findById(demoUser.getId()).getCreditScore();
        String confirmMessage = tradeController.confirm(flow.getId(), demoUser.getId());
        Item sold = itemService.detail(published.getId());
        System.out.println("[8/9] " + confirmMessage + "：物品状态=" + sold.getStatus()
                + "，卖家信用分 " + sellerCreditBefore + " -> "
                + userService.findById(demoUser.getId()).getCreditScore());
        System.out.println("      " + reviewController.review(flow.getId(), buyer.getId(), 5, "书很新，交易顺利，感谢！"));
        boolean favorited = factory.getFavoriteService().toggle(buyer.getId(), published.getId());
        UserCreditDTO credit = userController.getCredit(demoUser.getId());
        System.out.println("      收藏切换结果=" + favorited
                + "；卖家信用等级=" + (credit == null ? "-" : credit.getCreditLevel())
                + "（变更次数 " + (credit == null ? 0 : credit.getChangeCount()) + "）"
                + "；买家未读消息=" + tradeController.countUnread(buyer.getId())
                + "；" + demoUser.getUsername() + " 流转详情条数="
                + tradeController.historyDetail(demoUser.getId(), null, 1, 5).size());
        System.out.println("      最近操作日志条数：" + factory.getAdminService().recentLogs(10).size());

        // 9. 统计与 CSV 导出（经 StatisticController）
        LocalDateTime from = LocalDateTime.of(2026, 1, 1, 0, 0, 0);
        LocalDateTime to = LocalDateTime.of(2026, 12, 31, 23, 59, 59);
        List<StatisticsDTO> statistics = statisticController.statisticsByCategory(from, to);
        System.out.println("[9/9] 完成流转统计（按一级分类）：");
        for (StatisticsDTO dto : statistics) {
            System.out.println("      - " + dto.getCategoryName() + "：完成 " + dto.getFlowCount()
                    + " 笔，金额 " + dto.getTotalAmount() + " 元，减排 "
                    + String.format("%.2f", dto.getCarbonReduction()) + " kgCO2e");
        }
        System.out.println("      碳减排总量：" + statisticController.carbonReduction(from, to) + " kgCO2e");
        String csvPath = statisticController.exportCsv(Path.of("data", "export", "statistics.csv"), from, to);
        System.out.println("      统计 CSV 已导出：" + csvPath);
        System.out.println("============================================================");
        System.out.println(" 演示流程全部通过（注册/登录/发布/审核/检索/流转/成交事务/评价/收藏/统计）");
        System.out.println("============================================================");
    }
}
