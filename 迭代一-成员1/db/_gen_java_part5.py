# -*- coding: utf-8 -*-
"""D7 part5：config / controller / ui 占位 / Main 控制台演示 / application.properties / 2 个 JUnit 测试。

生成目标：C:\\Users\\wanhe\\Desktop\\软件构造\\迭代一-成员1\\code\\green-campus
"""
import os

ROOT = r"C:\Users\wanhe\Desktop\软件构造\迭代一-成员1\code\green-campus"
JAVA = os.path.join(ROOT, "src", "main", "java", "edu", "campus", "recycle")
files = {}


def add(rel, text):
    files[rel] = text.lstrip("\n")


add("config/DbConfig.java", r'''
package edu.campus.recycle.config;

import edu.campus.recycle.entity.SystemConfig;
import edu.campus.recycle.util.ConfigManager;
import edu.campus.recycle.util.DaoFactory;
import edu.campus.recycle.util.DbUtil;

import java.util.LinkedHashMap;
import java.util.Map;

/**
 * 数据库配置（单例）：启动时从 application.properties 读取连接串与脚本路径，
 * 并在运行期从 system_config 表读取业务参数（信用分、锁定策略、碳减排系数）。
 */
public final class DbConfig {

    private static final DbConfig INSTANCE = new DbConfig();

    private final String jdbcUrl;
    private final String schemaPath;
    private final String seedPath;
    private final String imageDir;
    private final boolean seedOnStart;

    private DbConfig() {
        ConfigManager config = ConfigManager.getInstance();
        this.jdbcUrl = config.getProperty(ConfigManager.KEY_DB_URL, "jdbc:sqlite:data/greencampus.db");
        this.schemaPath = config.getProperty(ConfigManager.KEY_SCHEMA, "../../db/schema.sql");
        this.seedPath = config.getProperty(ConfigManager.KEY_SEED, "../../db/seed-data.sql");
        this.imageDir = config.getProperty(ConfigManager.KEY_IMAGE_DIR, "data/images");
        this.seedOnStart = config.getBoolean(ConfigManager.KEY_SEED_ON_START, true);
    }

    /**
     * 获取单例。
     *
     * @return 配置对象
     */
    public static DbConfig getInstance() {
        return INSTANCE;
    }

    /**
     * 将连接串应用到 {@link DbUtil}（加载 JDBC 驱动）。
     */
    public void applyToDbUtil() {
        DbUtil.getInstance().init(jdbcUrl);
    }

    /**
     * 从 system_config 表读取全部配置项。
     *
     * @return 键值对（保持数据库读取顺序）
     */
    public Map<String, String> loadSystemConfigMap() {
        Map<String, String> result = new LinkedHashMap<>();
        for (SystemConfig config : DaoFactory.getInstance().getSystemConfigDao().findAll()) {
            result.put(config.getConfigKey(), config.getConfigValue());
        }
        return result;
    }

    public String getJdbcUrl() {
        return jdbcUrl;
    }

    public String getSchemaPath() {
        return schemaPath;
    }

    public String getSeedPath() {
        return seedPath;
    }

    public String getImageDir() {
        return imageDir;
    }

    public boolean isSeedOnStart() {
        return seedOnStart;
    }
}
''')

add("config/DatabaseInitializer.java", r'''
package edu.campus.recycle.config;

import edu.campus.recycle.exception.DataAccessException;
import edu.campus.recycle.util.DbUtil;

import java.io.IOException;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.sql.Connection;
import java.sql.SQLException;
import java.sql.Statement;
import java.util.ArrayList;
import java.util.List;
import java.util.logging.Level;
import java.util.logging.Logger;

/**
 * 数据库初始化器：执行 {@code schema.sql}（脚本自身可重复执行：先反序 DROP 再重建），
 * 并按开关执行 {@code seed-data.sql} 导入演示数据。
 *
 * <p>脚本按分号拆分逐条执行；拆分时识别单引号字符串与 {@code --} 行注释，避免误切。</p>
 */
public final class DatabaseInitializer {

    private static final Logger LOG = Logger.getLogger(DatabaseInitializer.class.getName());

    private DatabaseInitializer() {
    }

    /**
     * 初始化数据库（含种子数据，取决于配置 app.seed.on.start）。
     */
    public static void initialize() {
        initialize(DbConfig.getInstance().isSeedOnStart());
    }

    /**
     * 初始化数据库。
     *
     * @param withSeed 是否导入种子数据
     */
    public static void initialize(boolean withSeed) {
        ensureDatabaseDirectory();
        Path schema = Paths.get(DbConfig.getInstance().getSchemaPath()).toAbsolutePath().normalize();
        runScript(schema, "建库脚本");
        if (withSeed) {
            Path seed = Paths.get(DbConfig.getInstance().getSeedPath()).toAbsolutePath().normalize();
            runScript(seed, "种子数据脚本");
        }
        LOG.info(() -> "数据库初始化完成，schema=" + schema);
    }

    /**
     * 确保 SQLite 数据库文件所在目录存在（首次运行时 data 目录通常不存在）。
     */
    private static void ensureDatabaseDirectory() {
        String jdbcUrl = DbUtil.getInstance().getJdbcUrl();
        final String prefix = "jdbc:sqlite:";
        if (jdbcUrl == null || !jdbcUrl.startsWith(prefix)) {
            return;
        }
        String filePart = jdbcUrl.substring(prefix.length());
        if (filePart.isEmpty() || filePart.startsWith(":memory:")) {
            return;
        }
        Path parent = Paths.get(filePart).toAbsolutePath().normalize().getParent();
        if (parent == null) {
            return;
        }
        try {
            Files.createDirectories(parent);
        } catch (IOException e) {
            throw new DataAccessException("无法创建数据库目录：" + parent, e);
        }
    }

    /**
     * 执行一个 SQL 脚本文件。
     *
     * @param path  脚本路径
     * @param label 日志标签
     */
    private static void runScript(Path path, String label) {
        if (!Files.exists(path)) {
            throw new IllegalStateException(label + "不存在：" + path);
        }
        String content;
        try {
            content = Files.readString(path, StandardCharsets.UTF_8);
        } catch (IOException e) {
            throw DataAccessException.of("读取" + label + "失败：" + path, e);
        }
        List<String> statements = splitStatements(content);
        LOG.info(() -> label + "共 " + statements.size() + " 条语句：" + path.getFileName());
        try (Connection connection = DbUtil.getInstance().getConnection();
             Statement statement = connection.createStatement()) {
            for (String sql : statements) {
                statement.execute(sql);
            }
        } catch (SQLException e) {
            throw DataAccessException.of("执行" + label + "失败：" + path + "（" + e.getMessage() + "）", e);
        }
    }

    /**
     * 按分号拆分 SQL 语句：忽略行注释与字符串内的分号。
     *
     * @param content 脚本全文
     * @return 语句列表
     */
    static List<String> splitStatements(String content) {
        List<String> statements = new ArrayList<>();
        StringBuilder current = new StringBuilder();
        boolean inSingleQuote = false;
        boolean inComment = false;
        for (int i = 0; i < content.length(); i++) {
            char ch = content.charAt(i);
            if (inComment) {
                if (ch == '\n') {
                    inComment = false;
                    current.append('\n');
                }
                continue;
            }
            if (!inSingleQuote && ch == '-' && i + 1 < content.length() && content.charAt(i + 1) == '-') {
                inComment = true;
                i++;
                continue;
            }
            if (ch == '\'') {
                if (inSingleQuote && i + 1 < content.length() && content.charAt(i + 1) == '\'') {
                    current.append("''");
                    i++;
                    continue;
                }
                inSingleQuote = !inSingleQuote;
                current.append(ch);
                continue;
            }
            if (ch == ';' && !inSingleQuote) {
                addStatement(statements, current);
                current.setLength(0);
                continue;
            }
            current.append(ch);
        }
        addStatement(statements, current);
        return statements;
    }

    private static void addStatement(List<String> statements, StringBuilder buffer) {
        String sql = buffer.toString().trim();
        if (!sql.isEmpty()) {
            statements.add(sql);
        }
    }
}
''')

add("controller/AppController.java", r'''
package edu.campus.recycle.controller;

import edu.campus.recycle.config.DatabaseInitializer;
import edu.campus.recycle.dto.ItemQuery;
import edu.campus.recycle.dto.LoginResult;
import edu.campus.recycle.dto.PageResult;
import edu.campus.recycle.dto.StatisticsDTO;
import edu.campus.recycle.entity.Item;
import edu.campus.recycle.entity.TradeFlow;
import edu.campus.recycle.entity.User;
import edu.campus.recycle.service.FavoriteService;
import edu.campus.recycle.service.ItemService;
import edu.campus.recycle.service.ReviewService;
import edu.campus.recycle.service.StatisticService;
import edu.campus.recycle.service.TradeService;
import edu.campus.recycle.service.UserService;
import edu.campus.recycle.util.ServiceFactory;

import java.time.LocalDateTime;
import java.util.List;

/**
 * 应用控制器骨架：位于 UI 与 Service 之间，负责会话状态（当前登录用户）编排。
 *
 * <p>迭代一的 Swing 界面由成员3实现，本类只提供与界面无关的调用入口；
 * 控制器不直接访问 DAO，全部经由 {@link ServiceFactory} 装配的服务接口。</p>
 */
public class AppController {

    private final UserService userService;
    private final ItemService itemService;
    private final FavoriteService favoriteService;
    private final TradeService tradeService;
    private final ReviewService reviewService;
    private final StatisticService statisticService;

    private User currentUser;

    public AppController() {
        ServiceFactory factory = ServiceFactory.getInstance();
        this.userService = factory.getUserService();
        this.itemService = factory.getItemService();
        this.favoriteService = factory.getFavoriteService();
        this.tradeService = factory.getTradeService();
        this.reviewService = factory.getReviewService();
        this.statisticService = factory.getStatisticService();
    }

    /**
     * 初始化数据库（界面启动时调用一次）。
     */
    public void bootstrapDatabase() {
        DatabaseInitializer.initialize();
    }

    /**
     * 登录并记录会话。
     *
     * @return 登录结果
     */
    public LoginResult login(String username, String rawPassword) {
        LoginResult result = userService.login(username, rawPassword);
        this.currentUser = userService.findById(result.getUserId());
        return result;
    }

    /**
     * 退出登录。
     */
    public void logout() {
        this.currentUser = null;
    }

    public User getCurrentUser() {
        return currentUser;
    }

    public Item publishItem(Item item, List<String> imagePaths) {
        return itemService.publish(item, imagePaths);
    }

    public PageResult<Item> searchItems(ItemQuery query) {
        return itemService.search(query);
    }

    public Item itemDetail(int itemId) {
        return itemService.detail(itemId);
    }

    public TradeFlow applyTrade(int itemId, String remark) {
        if (currentUser == null) {
            throw new IllegalStateException("请先登录");
        }
        return tradeService.apply(itemId, currentUser.getId(), remark);
    }

    public void confirmTrade(int flowId) {
        if (currentUser == null) {
            throw new IllegalStateException("请先登录");
        }
        tradeService.confirm(flowId, currentUser.getId());
    }

    public boolean toggleFavorite(int itemId) {
        if (currentUser == null) {
            throw new IllegalStateException("请先登录");
        }
        return favoriteService.toggle(currentUser.getId(), itemId);
    }

    public List<StatisticsDTO> statistics() {
        LocalDateTime now = LocalDateTime.now();
        return statisticService.statisticsByCategory(LocalDateTime.of(2000, 1, 1, 0, 0), now);
    }
}
''')

add("ui/SwingUiPlaceholder.java", r'''
package edu.campus.recycle.ui;

/**
 * Swing 界面占位类。
 *
 * <p>迭代一交付中，图形界面（登录、物品列表、发布表单、流转与统计面板）由成员3实现，
 * 本类仅用于占位并声明 ui 包的职责边界：界面层只依赖 controller 与 service 接口，
 * 不得出现任何 SQL 或 JDBC 代码。</p>
 */
public final class SwingUiPlaceholder {

    private SwingUiPlaceholder() {
    }

    /**
     * 界面模块职责说明（供类图与文档引用）。
     *
     * @return 职责说明
     */
    public static String responsibility() {
        return "Swing 界面层：负责视图渲染与用户交互，通过 AppController 调用服务层，不含 SQL/JDBC。";
    }
}
''')

add("Main.java", r'''
package edu.campus.recycle;

import edu.campus.recycle.config.DatabaseInitializer;
import edu.campus.recycle.config.DbConfig;
import edu.campus.recycle.dao.UserDao;
import edu.campus.recycle.dto.ItemQuery;
import edu.campus.recycle.dto.LoginResult;
import edu.campus.recycle.dto.PageResult;
import edu.campus.recycle.dto.StatisticsDTO;
import edu.campus.recycle.entity.Category;
import edu.campus.recycle.entity.Item;
import edu.campus.recycle.entity.ItemStatus;
import edu.campus.recycle.entity.TradeFlow;
import edu.campus.recycle.entity.TradeType;
import edu.campus.recycle.entity.User;
import edu.campus.recycle.exception.AppException;
import edu.campus.recycle.exception.DuplicateEntityException;
import edu.campus.recycle.service.AdminService;
import edu.campus.recycle.service.FavoriteService;
import edu.campus.recycle.service.ItemService;
import edu.campus.recycle.service.ReviewService;
import edu.campus.recycle.service.StatisticService;
import edu.campus.recycle.service.TradeService;
import edu.campus.recycle.service.UserService;
import edu.campus.recycle.util.DaoFactory;
import edu.campus.recycle.util.ServiceFactory;

import java.math.BigDecimal;
import java.nio.file.Path;
import java.time.LocalDateTime;
import java.util.List;
import java.util.logging.Logger;

/**
 * 控制台演示入口：初始化数据库 → 注册 → 登录 → 发布物品 → 检索 → 发起流转 →
 * 同意 → 确认成交（跨表事务）→ 评价 → 收藏 → 统计与 CSV 导出。
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
        TradeService tradeService = factory.getTradeService();
        ReviewService reviewService = factory.getReviewService();
        FavoriteService favoriteService = factory.getFavoriteService();
        StatisticService statisticService = factory.getStatisticService();
        AdminService adminService = factory.getAdminService();
        UserDao userDao = DaoFactory.getInstance().getUserDao();

        // 1. 初始化数据库（执行 schema + seed）
        DbConfig config = DbConfig.getInstance();
        config.applyToDbUtil();
        DatabaseInitializer.initialize();
        System.out.println("[1/9] 数据库初始化完成：" + config.getJdbcUrl());
        System.out.println("      system_config 项数：" + config.loadSystemConfigMap().size());
        List<Category> categories = DaoFactory.getInstance().getCategoryDao().findEnabled();
        System.out.println("      可用分类数：" + categories.size()
                + "，示例：" + (categories.isEmpty() ? "-" : categories.get(0).getName()));

        // 2. 注册（重复执行时自动降级为登录）
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

        // 3. 登录
        LoginResult login = userService.login(DEMO_USERNAME, DEMO_PASSWORD);
        System.out.println("[3/9] 登录成功：" + login.getUsername()
                + "，角色=" + login.getRole() + "，登录时间=" + login.getLoginAt());

        // 4. 发布物品 + 图片（同一事务）
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
        item.setStatus(ItemStatus.ON_SALE.getCode());
        Item published = itemService.publish(item, List.of("data/images/demo-book-1.jpg"));
        System.out.println("[4/9] 发布物品成功：itemId=" + published.getId()
                + "，状态=" + published.getStatus() + "，价格=" + published.getPrice());

        // 5. 检索
        ItemQuery query = new ItemQuery();
        query.setKeyword("数据库");
        query.setPageSize(5);
        PageResult<Item> page = itemService.search(query);
        System.out.println("[5/9] 检索「数据库」命中 " + page.getTotal() + " 条，当前页 "
                + page.getRecords().size() + " 条：");
        for (Item record : page.getRecords()) {
            System.out.println("      - #" + record.getId() + " " + record.getTitle()
                    + " / " + record.getTradeType() + " / " + record.getPrice());
        }

        // 6. 发起流转（买家使用种子用户 zhangsan）
        User buyer = userDao.findByUsername("zhangsan")
                .orElseThrow(() -> new IllegalStateException("种子用户 zhangsan 不存在"));
        TradeFlow flow = tradeService.apply(published.getId(), buyer.getId(), "教材正需要，希望转让");
        System.out.println("[6/9] 发起流转成功：flowId=" + flow.getId()
                + "，status=" + flow.getStatus() + "，金额=" + flow.getAmount());

        // 7. 同意 + 确认成交（跨表事务：物品 SOLD + 流转 DONE + 信用分 + 日志 + 统计）
        tradeService.agree(flow.getId(), demoUser.getId());
        System.out.println("      卖家已同意，物品状态="
                + itemService.detail(published.getId()).getStatus());
        int sellerCreditBefore = userService.findById(demoUser.getId()).getCreditScore();
        tradeService.confirm(flow.getId(), demoUser.getId());
        System.out.println("[7/9] 确认成交成功：物品状态="
                + itemService.detail(published.getId()).getStatus()
                + "，卖家信用分 " + sellerCreditBefore + " -> "
                + userService.findById(demoUser.getId()).getCreditScore());

        // 8. 评价 + 收藏 + 管理端日志
        reviewService.review(flow.getId(), buyer.getId(), 5, "书很新，交易顺利，感谢！");
        boolean favorited = favoriteService.toggle(buyer.getId(), published.getId());
        System.out.println("[8/9] 买家已评价（5 分）；收藏切换结果=" + favorited
                + "，收藏数=" + favoriteService.listByUser(buyer.getId()).size());
        System.out.println("      最近操作日志条数：" + adminService.recentLogs(10).size());

        // 9. 统计与 CSV 导出
        LocalDateTime from = LocalDateTime.of(2026, 1, 1, 0, 0, 0);
        LocalDateTime to = LocalDateTime.of(2026, 12, 31, 23, 59, 59);
        List<StatisticsDTO> statistics = statisticService.statisticsByCategory(from, to);
        System.out.println("[9/9] 完成流转统计（按一级分类）：");
        for (StatisticsDTO dto : statistics) {
            System.out.println("      - " + dto.getCategoryName() + "：完成 " + dto.getFlowCount()
                    + " 笔，金额 " + dto.getTotalAmount() + " 元，减排 "
                    + String.format("%.2f", dto.getCarbonReduction()) + " kgCO2e");
        }
        System.out.println("      碳减排总量：" + statisticService.carbonReduction(from, to) + " kgCO2e");
        String csvPath;
        try {
            csvPath = statisticService.exportCsv(Path.of("data", "export", "statistics.csv"), from, to);
        } catch (java.io.IOException e) {
            csvPath = "（导出失败：" + e.getMessage() + "）";
        }
        System.out.println("      统计 CSV 已导出：" + csvPath);
        System.out.println("============================================================");
        System.out.println(" 演示流程全部通过（注册/登录/发布/检索/流转/成交事务/评价/收藏/统计）");
        System.out.println("============================================================");
    }
}
''')

# application.properties
files_props = r'''
# 绿色校园闲置物品循环流转平台 —— 运行期配置（迭代一 · 成员1 D7）
app.name=绿色校园闲置物品循环流转平台
app.version=1.0.0

# SQLite 数据库文件（相对进程工作目录，即 code/green-campus）
db.url=jdbc:sqlite:data/greencampus.db
# 建库脚本与种子数据脚本（相对 code/green-campus，指向 迭代一-成员1/db）
db.schema=../../db/schema.sql
db.seed=../../db/seed-data.sql
# 图片根目录
app.image.dir=data/images
# 启动时是否导入种子数据
app.seed.on.start=true

# 日志级别（JUL / logback 共用语义）
log.level=INFO
'''.lstrip("\n")

# tests
add_test = r'''
package edu.campus.recycle.util;

import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Test;

import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertNotEquals;
import static org.junit.jupiter.api.Assertions.assertTrue;

/**
 * {@link PasswordUtil} 单元测试：PBKDF2WithHmacSHA256 加盐哈希与校验。
 */
class PasswordUtilTest {

    @Test
    @DisplayName("盐应为 16 字节随机数的 Base64 文本")
    void generateSaltShouldBeBase64Of16Bytes() {
        String salt = PasswordUtil.generateSalt();
        assertNotEquals(salt, PasswordUtil.generateSalt(), "两次生成的盐不应相同");
        byte[] decoded = java.util.Base64.getDecoder().decode(salt);
        assertTrue(decoded.length == PasswordUtil.SALT_BYTES,
                "盐解码后长度应为 " + PasswordUtil.SALT_BYTES + " 字节");
    }

    @Test
    @DisplayName("相同口令与盐应得到相同摘要（确定性）")
    void hashShouldBeDeterministic() {
        String salt = PasswordUtil.generateSalt();
        assertTrue(PasswordUtil.hash("Demo@12345", salt).equals(PasswordUtil.hash("Demo@12345", salt)));
    }

    @Test
    @DisplayName("正确口令应通过校验")
    void verifyShouldAcceptCorrectPassword() {
        String salt = PasswordUtil.generateSalt();
        String hash = PasswordUtil.hash("Demo@12345", salt);
        assertTrue(PasswordUtil.verify("Demo@12345", salt, hash));
    }

    @Test
    @DisplayName("错误口令应校验失败")
    void verifyShouldRejectWrongPassword() {
        String salt = PasswordUtil.generateSalt();
        String hash = PasswordUtil.hash("Demo@12345", salt);
        assertFalse(PasswordUtil.verify("Demo@12346", salt, hash));
    }

    @Test
    @DisplayName("encodeDemo 应返回 salt:hash 两段结构")
    void encodeDemoShouldReturnSaltAndHash() {
        String encoded = PasswordUtil.encodeDemo("Admin@123");
        String[] parts = encoded.split(":");
        assertTrue(parts.length == 2, "encodeDemo 结果应包含盐与摘要两段");
        assertTrue(PasswordUtil.verify("Admin@123", parts[0], parts[1]));
    }
}
'''.lstrip("\n")

add_test2 = r'''
package edu.campus.recycle.util;

import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Test;

import java.math.BigDecimal;

import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;

/**
 * {@link Validator} 单元测试：BR-01 用户名/口令/学号规则与 BR-12 图片规则。
 */
class ValidatorTest {

    @Test
    @DisplayName("合法用户名应通过（4-20 位字母数字下划线）")
    void validUsernameShouldPass() {
        assertTrue(Validator.isValidUsername("zhang_san01"));
        assertTrue(Validator.isValidUsername("abcd"));
    }

    @Test
    @DisplayName("非法用户名应被拒绝")
    void invalidUsernameShouldFail() {
        assertFalse(Validator.isValidUsername("ab"));
        assertFalse(Validator.isValidUsername("张三同学"));
        assertFalse(Validator.isValidUsername("bad-name"));
    }

    @Test
    @DisplayName("口令必须同时包含字母与数字且长度 8-20")
    void passwordShouldRequireLetterAndDigit() {
        assertTrue(Validator.isValidPassword("Demo@12345"));
        assertFalse(Validator.isValidPassword("12345678"));
        assertFalse(Validator.isValidPassword("abcdefgh"));
        assertFalse(Validator.isValidPassword("Ab1"));
    }

    @Test
    @DisplayName("学号必须为 8-12 位数字")
    void studentNoShouldBe8To12Digits() {
        assertTrue(Validator.isValidStudentNo("20239901"));
        assertFalse(Validator.isValidStudentNo("2023"));
        assertFalse(Validator.isValidStudentNo("2023990X"));
    }

    @Test
    @DisplayName("图片仅允许 jpg/jpeg/png 后缀")
    void imageFileNameShouldOnlyAllowCommonSuffixes() {
        assertTrue(Validator.isValidImageFileName("book.jpg"));
        assertTrue(Validator.isValidImageFileName("photo.JPEG"));
        assertTrue(Validator.isValidImageFileName("cover.png"));
        assertFalse(Validator.isValidImageFileName("cover.gif"));
    }

    @Test
    @DisplayName("价格不得为负，描述长度受 500 字限制")
    void priceAndDescriptionShouldBeValidated() {
        assertTrue(Validator.isValidPrice(new BigDecimal("45.00")));
        assertFalse(Validator.isValidPrice(new BigDecimal("-1")));
        assertTrue(Validator.isValidDescription("九成新教材"));
        assertThrows(RuntimeException.class, () -> Validator.checkUsername("a"));
    }
}
'''.lstrip("\n")

# ---------------------------------------------------------------------------
# 写出
# ---------------------------------------------------------------------------
count = 0
for rel, text in files.items():
    path = os.path.join(JAVA, rel.replace("/", os.sep))
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="\n") as fp:
        fp.write(text)
    count += 1
    print("  + " + rel + "  " + str(len(text.encode("utf-8"))) + " B")

props_path = os.path.join(ROOT, "src", "main", "resources", "application.properties")
os.makedirs(os.path.dirname(props_path), exist_ok=True)
with open(props_path, "w", encoding="utf-8", newline="\n") as fp:
    fp.write(files_props)
count += 1
print("  + src/main/resources/application.properties  " + str(len(files_props.encode("utf-8"))) + " B")

tests = {
    "util/PasswordUtilTest.java": add_test,
    "util/ValidatorTest.java": add_test2,
}
for rel, text in tests.items():
    path = os.path.join(ROOT, "src", "test", "java", "edu", "campus", "recycle", rel.replace("/", os.sep))
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="\n") as fp:
        fp.write(text)
    count += 1
    print("  + src/test/java/edu/campus/recycle/" + rel + "  " + str(len(text.encode("utf-8"))) + " B")

print("part5 完成：%d 个文件" % count)
