# -*- coding: utf-8 -*-
"""D7 生成器 part2：异常体系（10 个类）与 util 基础设施（事务、口令、校验、配置、CSV、策略、观察者、SQL 脚本）。"""
import os

BASE = r'C:\Users\wanhe\Desktop\软件构造\迭代一-成员1\code\green-campus'
JAVA = os.path.join(BASE, 'src', 'main', 'java', 'edu', 'campus', 'recycle')


def write(rel, content):
    path = os.path.join(BASE, rel)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'w', encoding='utf-8', newline='\n') as f:
        f.write(content)
    print('  + %-78s %5d B' % (rel, len(content.encode('utf-8'))))


def out(pkg, cls):
    return os.path.join('src', 'main', 'java', 'edu', 'campus', 'recycle', *pkg.split('.'), cls + '.java')


# ==========================================================================
# 异常体系
# ==========================================================================
APP_EXCEPTION = '''package edu.campus.recycle.exception;

/**
 * 业务异常基类（契约第 7 节）。
 *
 * <p>所有可预期异常均继承本类，携带机器可读的 {@code code} 与面向用户的
 * {@code userMessage}；UI 层只捕获本类并按 {@code code} 映射提示文案，
 * 未捕获异常由全局处理器写 {@code operation_log} 与日志文件。</p>
 */
public class AppException extends RuntimeException {

    private static final long serialVersionUID = 1L;

    /** 错误码，形如 VAL-001 / BR-04 / DB-001 */
    private final String code;

    /** 面向用户的提示文案（不含堆栈与内部细节） */
    private final String userMessage;

    public AppException(String code, String userMessage) {
        super(userMessage);
        this.code = code;
        this.userMessage = userMessage;
    }

    public AppException(String code, String userMessage, Throwable cause) {
        super(userMessage, cause);
        this.code = code;
        this.userMessage = userMessage;
    }

    /**
     * 统一工厂方法（契约第 7 节）。
     *
     * @param code        错误码
     * @param userMessage 用户提示文案
     * @param cause       根因
     * @return 业务异常实例
     */
    public static AppException of(String code, String userMessage, Throwable cause) {
        return new AppException(code, userMessage, cause);
    }

    public String getCode() {
        return code;
    }

    public String getUserMessage() {
        return userMessage;
    }
}
'''
write(out('exception', 'AppException'), APP_EXCEPTION)

SIMPLE_EXCEPTIONS = [
    ('ValidationException', 'VAL', '参数校验失败', [
        ('校验类异常', '用户输入不符合 BR-01/BR-12 等规则时抛出，携带具体字段与规则说明。'),
    ]),
]
# 逐个手写，保证构造器与工厂方法口径一致
EXC_SPECS = [
    ('ValidationException', 'VAL-001', '参数校验失败',
     '校验类异常：用户输入不符合 BR-01/BR-12 等规则时抛出，携带具体字段与规则说明。'),
    ('DuplicateEntityException', 'DUP-001', '数据已存在',
     '唯一性冲突异常：用户名、学号、收藏、评价、配置键等唯一约束冲突时抛出。'),
    ('EntityNotFoundException', 'NF-001', '数据不存在',
     '实体不存在异常：按主键查询无结果（或已被删除）时抛出。'),
    ('AuthenticationException', 'AUTH-001', '认证失败',
     '认证异常：用户名或口令错误、旧口令校验失败时抛出；提示文案不得暴露口令信息（BR-02）。'),
    ('AccountLockedException', 'LOCK-001', '账号已锁定',
     '账号锁定异常：连续登录失败达到阈值（BR-03）时抛出，携带剩余锁定时间。'),
    ('PermissionDeniedException', 'PERM-001', '权限不足',
     '权限异常：非本人/非管理员执行受限操作时抛出（BR-06、BR-10）。'),
    ('DataAccessException', 'DB-001', '数据访问失败',
     '数据访问异常：JDBC 操作失败时由模板方法统一转换，屏蔽底层 SQLException 细节。'),
    ('TransactionException', 'TX-001', '事务执行失败',
     '事务异常：提交或回滚失败、事务嵌套异常时抛出；业务规则拒绝使用 BusinessRuleException。'),
]

for cls, code, cn, desc in EXC_SPECS:
    content = '''package edu.campus.recycle.exception;

/**
 * %(desc)s
 */
public class %(cls)s extends AppException {

    private static final long serialVersionUID = 1L;

    /** 默认错误码前缀（子类可传入更细粒度的错误码） */
    public static final String DEFAULT_CODE = "%(code)s";

    public %(cls)s(String userMessage) {
        super(DEFAULT_CODE, userMessage);
    }

    public %(cls)s(String userMessage, Throwable cause) {
        super(DEFAULT_CODE, userMessage, cause);
    }

    public %(cls)s(String code, String userMessage) {
        super(code, userMessage);
    }

    /**
     * 使用默认错误码构造异常。
     *
     * @param userMessage 用户提示文案
     * @return 异常实例
     */
    public static %(cls)s of(String userMessage) {
        return new %(cls)s(userMessage);
    }

    /**
     * 使用默认错误码构造异常并保留根因。
     *
     * @param userMessage 用户提示文案
     * @param cause       根因
     * @return 异常实例
     */
    public static %(cls)s of(String userMessage, Throwable cause) {
        return new %(cls)s(userMessage, cause);
    }

    /**
     * 使用指定错误码构造异常。
     *
     * @param code        错误码
     * @param userMessage 用户提示文案
     * @return 异常实例
     */
    public static %(cls)s ofCode(String code, String userMessage) {
        return new %(cls)s(code, userMessage);
    }
}
''' % {'cls': cls, 'code': code, 'desc': desc}
    write(out('exception', cls), content)

BR_EXCEPTION = '''package edu.campus.recycle.exception;

/**
 * 业务规则异常：违反 BR-01..BR-12 时抛出，{@code code} 携带被违反的 BR 编号
 * （如 {@code BR-04}），便于界面直接展示"信用分不足"等明确原因。
 */
public class BusinessRuleException extends AppException {

    private static final long serialVersionUID = 1L;

    /** 被违反的业务规则编号，形如 BR-04 */
    private final String brCode;

    /**
     * 构造业务规则异常。
     *
     * @param brCode      业务规则编号，允许传 "BR-04" 或 "04"
     * @param userMessage 用户提示文案
     */
    public BusinessRuleException(String brCode, String userMessage) {
        super(normalize(brCode), userMessage);
        this.brCode = normalize(brCode);
    }

    public BusinessRuleException(String brCode, String userMessage, Throwable cause) {
        super(normalize(brCode), userMessage, cause);
        this.brCode = normalize(brCode);
    }

    private static String normalize(String brCode) {
        if (brCode == null || brCode.isBlank()) {
            return "BR-000";
        }
        String trimmed = brCode.trim().toUpperCase();
        return trimmed.startsWith("BR-") ? trimmed : "BR-" + trimmed;
    }

    /**
     * 构造业务规则异常（无根因）。
     *
     * @param brCode      业务规则编号
     * @param userMessage 用户提示文案
     * @return 异常实例
     */
    public static BusinessRuleException of(String brCode, String userMessage) {
        return new BusinessRuleException(brCode, userMessage);
    }

    /**
     * 构造业务规则异常（保留根因）。
     *
     * @param brCode      业务规则编号
     * @param userMessage 用户提示文案
     * @param cause       根因
     * @return 异常实例
     */
    public static BusinessRuleException of(String brCode, String userMessage, Throwable cause) {
        return new BusinessRuleException(brCode, userMessage, cause);
    }

    public String getBrCode() {
        return brCode;
    }
}
'''
write(out('exception', 'BusinessRuleException'), BR_EXCEPTION)

# ==========================================================================
# util：事务与 JDBC 模板所需的函数式接口
# ==========================================================================
TXCALLBACK = '''package edu.campus.recycle.util;

import java.sql.Connection;

/**
 * 事务回调（模板方法的可变部分）：契约第 8 节模板方法 {@code DbUtil.executeInTransaction} 的入参。
 *
 * <p>实现类只描述"在事务内做什么"，连接的开启、提交、回滚、释放由 {@link DbUtil} 统一完成。</p>
 *
 * @param <T> 返回值类型
 */
@FunctionalInterface
public interface TransactionCallback<T> {

    /**
     * 在给定连接上执行事务体。
     *
     * @param conn 已关闭自动提交的连接（DAO 内部会自动复用该连接）
     * @return 事务结果
     * @throws Exception 任意异常都会触发整体回滚
     */
    T doInTransaction(Connection conn) throws Exception;
}
'''
write(out('util', 'TransactionCallback'), TXCALLBACK)

CONNCALLBACK = '''package edu.campus.recycle.util;

import java.sql.Connection;
import java.sql.SQLException;

/**
 * JDBC 回调：由 {@code AbstractJdbcDao} 统一负责连接获取、复用与释放。
 *
 * @param <R> 返回值类型
 */
@FunctionalInterface
public interface ConnectionCallback<R> {

    /**
     * 在连接上执行 JDBC 操作。
     *
     * @param conn 当前连接（事务中为事务连接）
     * @return 操作结果
     * @throws SQLException JDBC 异常，由模板方法转换为 DataAccessException
     */
    R doInConnection(Connection conn) throws SQLException;
}
'''
write(out('util', 'ConnectionCallback'), CONNCALLBACK)

ROW_MAPPER = '''package edu.campus.recycle.util;

import java.sql.ResultSet;
import java.sql.SQLException;

/**
 * 行映射器：把 {@link ResultSet} 当前行转换为实体或 DTO。
 *
 * @param <T> 目标类型
 */
@FunctionalInterface
public interface RowMapper<T> {

    /**
     * 映射当前行。
     *
     * @param rs 已定位到当前行的结果集
     * @return 映射结果
     * @throws SQLException 列不存在或类型不匹配
     */
    T mapRow(ResultSet rs) throws SQLException;
}
'''
write(out('util', 'RowMapper'), ROW_MAPPER)

# ==========================================================================
# util：DbUtil（单例 + 模板方法 + ThreadLocal 事务上下文）
# ==========================================================================
DB_UTIL = '''package edu.campus.recycle.util;

import edu.campus.recycle.exception.DataAccessException;
import edu.campus.recycle.exception.TransactionException;

import java.sql.Connection;
import java.sql.DriverManager;
import java.sql.SQLException;
import java.util.logging.Level;
import java.util.logging.Logger;

/**
 * 数据库工具类（契约第 8 节：单例 + 模板方法）。
 *
 * <p>职责：</p>
 * <ol>
 *   <li><b>单例</b>：全进程共享一个实例，避免重复加载驱动、重复解析连接串；</li>
 *   <li><b>连接获取</b>：{@link #getConnection()} 按 JDBC URL 新建连接，
 *       SQLite 以文件为库，连接本身开销远小于 server 型数据库；</li>
 *   <li><b>事务模板</b>：{@link #executeInTransaction(TransactionCallback)} 统一完成
 *       {@code setAutoCommit(false)} → 执行 → {@code commit} → 失败 {@code rollback} → 释放，
 *       调用方只需实现事务体；</li>
 *   <li><b>事务上下文</b>：事务期间把连接放入 {@link ThreadLocal}，
 *       DAO 通过 {@link #currentConnection()} 自动复用同一连接，
 *       因此 Service 层组合多个 DAO 时天然处于同一事务（BR-07）。</li>
 * </ol>
 *
 * <p>SQLite 并发说明：默认隔离级别 SERIALIZABLE，写事务串行化；本类在
 * {@code setAutoCommit(false)} 后由驱动发起事务，写冲突由
 * {@code SQLITE_BUSY} 表现，上层捕获后转换为 {@link TransactionException}，
 * 迭代二可通过 {@code busy_timeout} 与重试策略增强。</p>
 */
public final class DbUtil {

    private static final Logger LOG = Logger.getLogger(DbUtil.class.getName());

    /** 单例实例 */
    private static final DbUtil INSTANCE = new DbUtil();

    /** 事务连接上下文：仅事务线程可见 */
    private static final ThreadLocal<Connection> TX_CONNECTION = new ThreadLocal<>();

    /** JDBC URL，默认使用工程 data 目录下的 SQLite 文件 */
    private String jdbcUrl = "jdbc:sqlite:data/greencampus.db";

    private DbUtil() {
        // 单例：禁止外部实例化
    }

    /**
     * 获取单例。
     *
     * @return 数据库工具单例
     */
    public static DbUtil getInstance() {
        return INSTANCE;
    }

    /**
     * 初始化 JDBC 驱动与连接串。
     *
     * @param url SQLite 连接串，如 {@code jdbc:sqlite:data/greencampus.db}
     */
    public void init(String url) {
        if (url != null && !url.isBlank()) {
            this.jdbcUrl = url;
        }
        try {
            Class.forName("org.sqlite.JDBC");
        } catch (ClassNotFoundException e) {
            throw DataAccessException.of("未找到 SQLite JDBC 驱动 org.sqlite.JDBC，请检查 classpath", e);
        }
        LOG.log(Level.INFO, "DbUtil 初始化完成，JDBC URL = {0}", jdbcUrl);
    }

    public String getJdbcUrl() {
        return jdbcUrl;
    }

    /**
     * 新建一条数据库连接。
     *
     * @return 新连接
     * @throws SQLException 连接失败
     */
    public Connection getConnection() throws SQLException {
        Connection conn = DriverManager.getConnection(jdbcUrl);
        // SQLite 外键约束默认关闭，按连接显式开启（DDL 中亦声明 PRAGMA，双保险）
        // busy_timeout：写锁被占用时最多等待 5 秒再报 SQLITE_BUSY，避免桌面端偶发写冲突直接失败
        try (var stmt = conn.createStatement()) {
            stmt.execute("PRAGMA foreign_keys = ON");
            stmt.execute("PRAGMA busy_timeout = 5000");
        }
        return conn;
    }

    /**
     * 当前线程是否处于事务中。
     *
     * @return true 表示事务上下文存在
     */
    public boolean isInTransaction() {
        return TX_CONNECTION.get() != null;
    }

    /**
     * 获取当前线程可用的连接：事务中返回事务连接（调用方不得关闭），
     * 否则新建连接（调用方负责关闭）。
     *
     * @return 可用连接
     * @throws SQLException 连接失败
     */
    public Connection currentConnection() throws SQLException {
        Connection inTx = TX_CONNECTION.get();
        return inTx != null ? inTx : getConnection();
    }

    /**
     * 模板方法：在单个事务中执行回调（BR-07 的落点）。
     *
     * <p>若当前线程已处于事务中，则直接复用外层事务（嵌套调用不会二次提交），
     * 保证 Service 组合调用的事务原子性。</p>
     *
     * @param callback 事务体
     * @param <T>      返回类型
     * @return 事务体返回值
     * @throws TransactionException 提交或回滚失败
     */
    public <T> T executeInTransaction(TransactionCallback<T> callback) {
        Connection outer = TX_CONNECTION.get();
        if (outer != null) {
            try {
                return callback.doInTransaction(outer);
            } catch (RuntimeException e) {
                throw e;
            } catch (Exception e) {
                throw TransactionException.of("事务嵌套执行失败：" + e.getMessage(), e);
            }
        }

        Connection conn = null;
        boolean originalAutoCommit = true;
        try {
            conn = getConnection();
            originalAutoCommit = conn.getAutoCommit();
            conn.setAutoCommit(false);
            TX_CONNECTION.set(conn);
            LOG.log(Level.FINE, "事务开始");
            T result = callback.doInTransaction(conn);
            conn.commit();
            LOG.log(Level.FINE, "事务提交");
            return result;
        } catch (RuntimeException e) {
            rollbackQuietly(conn);
            throw e;
        } catch (Exception e) {
            rollbackQuietly(conn);
            LOG.log(Level.SEVERE, "事务失败已回滚：" + e.getMessage(), e);
            throw TransactionException.of("事务执行失败，已整体回滚：" + e.getMessage(), e);
        } finally {
            TX_CONNECTION.remove();
            if (conn != null) {
                try {
                    conn.setAutoCommit(originalAutoCommit);
                } catch (SQLException e) {
                    LOG.log(Level.WARNING, "恢复自动提交失败", e);
                }
                closeQuietly(conn);
            }
        }
    }

    /**
     * 安静回滚：回滚失败只记录日志，避免覆盖原始异常。
     *
     * @param conn 连接，可为 null
     */
    public void rollbackQuietly(Connection conn) {
        if (conn == null) {
            return;
        }
        try {
            if (!conn.isClosed()) {
                conn.rollback();
                LOG.log(Level.FINE, "事务回滚");
            }
        } catch (SQLException e) {
            LOG.log(Level.SEVERE, "事务回滚失败", e);
        }
    }

    /**
     * 安静关闭连接。
     *
     * @param conn 连接，可为 null
     */
    public void closeQuietly(Connection conn) {
        if (conn == null) {
            return;
        }
        try {
            conn.close();
        } catch (SQLException e) {
            LOG.log(Level.WARNING, "关闭连接失败", e);
        }
    }
}
'''
write(out('util', 'DbUtil'), DB_UTIL)

# ==========================================================================
# util：PasswordUtil
# ==========================================================================
PASSWORD_UTIL = '''package edu.campus.recycle.util;

import javax.crypto.SecretKeyFactory;
import javax.crypto.spec.PBEKeySpec;
import java.nio.charset.StandardCharsets;
import java.security.GeneralSecurityException;
import java.security.MessageDigest;
import java.security.SecureRandom;
import java.util.Base64;

/**
 * 口令工具类（BR-02）：PBKDF2WithHmacSHA256，100000 次迭代、16 字节随机盐、256 位密钥，Base64 编码。
 *
 * <p>存储格式：{@code user.password_hash} 存 Base64 摘要，{@code user.salt} 存 Base64 盐；
 * 任何日志、界面、异常信息均不得输出明文口令或盐。</p>
 */
public final class PasswordUtil {

    /** 摘要算法 */
    public static final String ALGORITHM = "PBKDF2WithHmacSHA256";
    /** 迭代次数（BR-02） */
    public static final int ITERATIONS = 100_000;
    /** 盐字节数（BR-02） */
    public static final int SALT_BYTES = 16;
    /** 密钥位数（BR-02） */
    public static final int KEY_BITS = 256;

    private static final SecureRandom RANDOM = new SecureRandom();
    private static final Base64.Encoder ENCODER = Base64.getEncoder();
    private static final Base64.Decoder DECODER = Base64.getDecoder();

    private PasswordUtil() {
    }

    /**
     * 生成 16 字节随机盐并 Base64 编码。
     *
     * @return Base64 盐字符串
     */
    public static String generateSalt() {
        byte[] salt = new byte[SALT_BYTES];
        RANDOM.nextBytes(salt);
        return ENCODER.encodeToString(salt);
    }

    /**
     * 计算口令摘要。
     *
     * @param rawPassword 明文口令
     * @param saltBase64  Base64 盐
     * @return Base64 摘要
     */
    public static String hash(String rawPassword, String saltBase64) {
        if (rawPassword == null || saltBase64 == null) {
            throw new IllegalArgumentException("口令与盐不能为空");
        }
        char[] chars = rawPassword.toCharArray();
        byte[] salt = DECODER.decode(saltBase64);
        PBEKeySpec spec = new PBEKeySpec(chars, salt, ITERATIONS, KEY_BITS);
        try {
            SecretKeyFactory factory = SecretKeyFactory.getInstance(ALGORITHM);
            byte[] encoded = factory.generateSecret(spec).getEncoded();
            return ENCODER.encodeToString(encoded);
        } catch (GeneralSecurityException e) {
            throw new IllegalStateException("口令摘要计算失败", e);
        } finally {
            spec.clearPassword();
            java.util.Arrays.fill(chars, '\\0');
        }
    }

    /**
     * 校验口令：对候选口令重新做 PBKDF2 后与存储摘要做常量时间比较。
     *
     * @param rawPassword  明文口令
     * @param saltBase64   Base64 盐
     * @param expectedHash 存储的 Base64 摘要
     * @return 一致返回 true
     */
    public static boolean verify(String rawPassword, String saltBase64, String expectedHash) {
        if (rawPassword == null || saltBase64 == null || expectedHash == null) {
            return false;
        }
        String actual = hash(rawPassword, saltBase64);
        return MessageDigest.isEqual(actual.getBytes(StandardCharsets.UTF_8),
                expectedHash.getBytes(StandardCharsets.UTF_8));
    }

    /**
     * 为 {@code admin/Admin@123} 等演示数据生成"盐:摘要"格式字符串的辅助方法，
     * 仅供种子数据生成脚本与单元测试使用。
     *
     * @param rawPassword 明文口令
     * @return {@code salt:hash} 形式的演示串
     */
    public static String encodeDemo(String rawPassword) {
        String salt = generateSalt();
        return salt + ":" + hash(rawPassword, salt);
    }
}
'''
write(out('util', 'PasswordUtil'), PASSWORD_UTIL)

# ==========================================================================
# util：Validator
# ==========================================================================
VALIDATOR = r'''package edu.campus.recycle.util;

import edu.campus.recycle.exception.ValidationException;

import java.math.BigDecimal;
import java.util.regex.Pattern;

/**
 * 输入校验器（BR-01、BR-12）：集中管理用户名、口令、学号、价格、图片等规则，
 * 避免各层重复编写正则导致口径漂移。
 */
public final class Validator {

    /** 用户名：4–20 位字母、数字、下划线（BR-01） */
    public static final Pattern USERNAME = Pattern.compile("^[A-Za-z0-9_]{4,20}$");
    /** 口令：8–20 位且同时包含字母与数字（BR-01） */
    public static final Pattern PASSWORD = Pattern.compile("^(?=.*[A-Za-z])(?=.*\\d)\\S{8,20}$");
    /** 学号/工号：8–12 位数字（BR-01） */
    public static final Pattern STUDENT_NO = Pattern.compile("^\\d{8,12}$");
    /** 图片扩展名：仅 jpg/jpeg/png（BR-12） */
    public static final Pattern IMAGE_FILE = Pattern.compile("(?i)^[^\\\\/:*?\"<>|]+\\.(jpg|jpeg|png)$");
    /** 手机号（可选联系方式，11 位数字） */
    public static final Pattern MOBILE = Pattern.compile("^1[3-9]\\d{9}$");

    /** 单张图片上限 2MB（BR-12） */
    public static final long MAX_IMAGE_BYTES = 2L * 1024L * 1024L;
    /** 单物品最多 5 张图（BR-12） */
    public static final int MAX_IMAGE_COUNT = 5;
    /** 标题 2–50 字 */
    public static final int TITLE_MIN = 2;
    public static final int TITLE_MAX = 50;
    /** 描述 ≤500 字 */
    public static final int DESCRIPTION_MAX = 500;
    /** 消息 ≤300 字 */
    public static final int MESSAGE_MAX = 300;

    private Validator() {
    }

    // ------------------------------------------------------------------ 布尔判定

    public static boolean isValidUsername(String username) {
        return username != null && USERNAME.matcher(username).matches();
    }

    public static boolean isValidPassword(String rawPassword) {
        return rawPassword != null && PASSWORD.matcher(rawPassword).matches();
    }

    public static boolean isValidStudentNo(String studentNo) {
        return studentNo != null && STUDENT_NO.matcher(studentNo).matches();
    }

    public static boolean isValidImageFileName(String fileName) {
        return fileName != null && IMAGE_FILE.matcher(fileName).matches();
    }

    public static boolean isValidImageSize(long bytes) {
        return bytes > 0 && bytes <= MAX_IMAGE_BYTES;
    }

    public static boolean isValidImageCount(int count) {
        return count >= 0 && count <= MAX_IMAGE_COUNT;
    }

    public static boolean isValidPrice(BigDecimal price) {
        return price != null && price.compareTo(BigDecimal.ZERO) >= 0;
    }

    public static boolean isValidTitle(String title) {
        return title != null && title.length() >= TITLE_MIN && title.length() <= TITLE_MAX;
    }

    public static boolean isValidDescription(String description) {
        return description != null && description.length() <= DESCRIPTION_MAX;
    }

    public static boolean isValidCreditScore(int score) {
        return score >= 0 && score <= 150;
    }

    // ------------------------------------------------------------------ 断言式校验

    /**
     * 校验用户名，不合法时抛出 {@link ValidationException}。
     *
     * @param username 用户名
     */
    public static void checkUsername(String username) {
        if (!isValidUsername(username)) {
            throw ValidationException.of("用户名必须为 4–20 位字母、数字或下划线");
        }
    }

    /**
     * 校验口令强度，不合法时抛出 {@link ValidationException}。
     *
     * @param rawPassword 明文口令
     */
    public static void checkPassword(String rawPassword) {
        if (!isValidPassword(rawPassword)) {
            throw ValidationException.of("口令必须为 8–20 位且同时包含字母与数字");
        }
    }

    /**
     * 校验学号，不合法时抛出 {@link ValidationException}。
     *
     * @param studentNo 学号/工号
     */
    public static void checkStudentNo(String studentNo) {
        if (!isValidStudentNo(studentNo)) {
            throw ValidationException.of("学号必须为 8–12 位数字");
        }
    }

    /**
     * 校验标题，不合法时抛出 {@link ValidationException}。
     *
     * @param title 标题
     */
    public static void checkTitle(String title) {
        if (!isValidTitle(title)) {
            throw ValidationException.of("标题长度必须为 2–50 字");
        }
    }

    /**
     * 校验图片文件名、大小与张数（BR-12）。
     *
     * @param fileName 文件名（含扩展名）
     * @param bytes    文件字节数
     * @param count    已选图片张数
     */
    public static void checkImage(String fileName, long bytes, int count) {
        if (!isValidImageFileName(fileName)) {
            throw ValidationException.of("图片仅支持 jpg/jpeg/png 格式");
        }
        if (!isValidImageSize(bytes)) {
            throw ValidationException.of("单张图片不得超过 2MB");
        }
        if (!isValidImageCount(count)) {
            throw ValidationException.of("每个物品最多上传 5 张图片");
        }
    }
}
'''
write(out('util', 'Validator'), VALIDATOR)

# ==========================================================================
# util：ConfigManager（单例）
# ==========================================================================
CONFIG_MANAGER = '''package edu.campus.recycle.util;

import java.io.IOException;
import java.io.InputStream;
import java.util.Properties;
import java.util.logging.Level;
import java.util.logging.Logger;

/**
 * 配置管理器（契约第 8 节：单例）。
 *
 * <p>读取 classpath 下的 {@code application.properties}，未配置项使用内置默认值；
 * 数据库中的 {@code system_config} 由业务层通过 {@code SystemConfigDao} 读取，
 * 二者分工为"部署参数"与"业务参数"。</p>
 */
public final class ConfigManager {

    private static final Logger LOG = Logger.getLogger(ConfigManager.class.getName());

    /** 单例实例 */
    private static final ConfigManager INSTANCE = new ConfigManager();

    /** 配置文件位置 */
    public static final String CONFIG_RESOURCE = "application.properties";

    /** 建库脚本路径（默认相对工程根目录） */
    public static final String KEY_SCHEMA = "db.schema";
    /** 种子数据脚本路径 */
    public static final String KEY_SEED = "db.seed";
    /** SQLite 连接串 */
    public static final String KEY_DB_URL = "db.url";
    /** 图片根目录 */
    public static final String KEY_IMAGE_DIR = "app.image.dir";
    /** 控制台演示数据开关 */
    public static final String KEY_SEED_ON_START = "app.seed.on.start";

    private final Properties properties = new Properties();

    private ConfigManager() {
        loadDefaults();
        loadFromResource(CONFIG_RESOURCE);
    }

    /**
     * 获取单例。
     *
     * @return 配置管理器
     */
    public static ConfigManager getInstance() {
        return INSTANCE;
    }

    private void loadDefaults() {
        properties.setProperty(KEY_DB_URL, "jdbc:sqlite:data/greencampus.db");
        properties.setProperty(KEY_SCHEMA, "../../db/schema.sql");
        properties.setProperty(KEY_SEED, "../../db/seed-data.sql");
        properties.setProperty(KEY_IMAGE_DIR, "data/images");
        properties.setProperty(KEY_SEED_ON_START, "true");
        properties.setProperty("app.name", "绿色校园闲置物品循环流转平台");
        properties.setProperty("app.version", "1.0.0");
    }

    private void loadFromResource(String resource) {
        try (InputStream in = ConfigManager.class.getClassLoader().getResourceAsStream(resource)) {
            if (in == null) {
                LOG.log(Level.INFO, "未找到 {0}，使用内置默认配置", resource);
                return;
            }
            properties.load(new java.io.InputStreamReader(in, java.nio.charset.StandardCharsets.UTF_8));
            LOG.log(Level.INFO, "已加载配置 {0}，共 {1} 项", new Object[]{resource, properties.size()});
        } catch (IOException e) {
            LOG.log(Level.WARNING, "加载配置失败，使用内置默认配置", e);
        }
    }

    /**
     * 读取字符串配置。
     *
     * @param key          键
     * @param defaultValue 默认值
     * @return 配置值
     */
    public String getProperty(String key, String defaultValue) {
        return properties.getProperty(key, defaultValue);
    }

    /**
     * 读取整型配置。
     *
     * @param key          键
     * @param defaultValue 默认值
     * @return 配置值
     */
    public int getInt(String key, int defaultValue) {
        String value = properties.getProperty(key);
        if (value == null) {
            return defaultValue;
        }
        try {
            return Integer.parseInt(value.trim());
        } catch (NumberFormatException e) {
            LOG.log(Level.WARNING, "配置 {0} 不是合法整数：{1}", new Object[]{key, value});
            return defaultValue;
        }
    }

    /**
     * 读取浮点配置。
     *
     * @param key          键
     * @param defaultValue 默认值
     * @return 配置值
     */
    public double getDouble(String key, double defaultValue) {
        String value = properties.getProperty(key);
        if (value == null) {
            return defaultValue;
        }
        try {
            return Double.parseDouble(value.trim());
        } catch (NumberFormatException e) {
            LOG.log(Level.WARNING, "配置 {0} 不是合法数值：{1}", new Object[]{key, value});
            return defaultValue;
        }
    }

    /**
     * 读取布尔配置。
     *
     * @param key          键
     * @param defaultValue 默认值
     * @return 配置值
     */
    public boolean getBoolean(String key, boolean defaultValue) {
        String value = properties.getProperty(key);
        return value == null ? defaultValue : Boolean.parseBoolean(value.trim());
    }
}
'''
write(out('util', 'ConfigManager'), CONFIG_MANAGER)

print('\npart2 完成（异常 + 事务/口令/校验/配置工具）。')
