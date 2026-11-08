package edu.campus.recycle.util;

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
