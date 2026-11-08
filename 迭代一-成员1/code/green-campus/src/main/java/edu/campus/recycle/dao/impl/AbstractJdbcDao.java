package edu.campus.recycle.dao.impl;

import edu.campus.recycle.exception.DataAccessException;
import edu.campus.recycle.util.ConnectionCallback;
import edu.campus.recycle.util.DbUtil;
import edu.campus.recycle.util.RowMapper;

import java.math.BigDecimal;
import java.sql.Connection;
import java.sql.PreparedStatement;
import java.sql.ResultSet;
import java.sql.SQLException;
import java.sql.Statement;
import java.time.LocalDateTime;
import java.time.format.DateTimeFormatter;
import java.time.format.DateTimeParseException;
import java.util.ArrayList;
import java.util.List;
import java.util.Optional;
import java.util.logging.Level;
import java.util.logging.Logger;

/**
 * JDBC DAO 模板基类（契约第 8 节：模板方法 + 统一异常转换）。
 *
 * <p>模板方法负责：获取连接（事务中自动复用事务连接）→ 绑定参数 → 执行 →
 * 映射结果 → 关闭资源 → 把 {@link SQLException} 统一转换为
 * {@link DataAccessException}。子类只需声明表名、行映射器与业务 SQL，不再出现
 * 重复的 try-catch-finally。</p>
 *
 * @param <T> 实体类型
 */
public abstract class AbstractJdbcDao<T> {

    private static final Logger LOG = Logger.getLogger(AbstractJdbcDao.class.getName());

    /** 数据库时间格式：yyyy-MM-dd HH:mm:ss（契约第 2 节） */
    public static final DateTimeFormatter DATE_TIME_FORMATTER =
            DateTimeFormatter.ofPattern("yyyy-MM-dd HH:mm:ss");

    /**
     * 逻辑表名，仅用于日志与错误信息定位。
     *
     * @return 表名
     */
    protected abstract String tableName();

    /**
     * 行映射器，把结果集当前行转换为实体。
     *
     * @return 行映射器
     */
    protected abstract RowMapper<T> rowMapper();

    // ------------------------------------------------------------------ 模板方法

    /**
     * 模板方法：在连接上执行 JDBC 操作并统一处理资源与异常。
     *
     * @param callback JDBC 回调
     * @param <R>      返回类型
     * @return 回调结果
     */
    protected <R> R withConnection(ConnectionCallback<R> callback) {
        boolean managed = DbUtil.getInstance().isInTransaction();
        Connection conn = null;
        try {
            conn = DbUtil.getInstance().currentConnection();
            return callback.doInConnection(conn);
        } catch (SQLException e) {
            LOG.log(Level.SEVERE, "[" + tableName() + "] 数据访问失败：" + e.getMessage(), e);
            throw DataAccessException.of("数据访问失败（" + tableName() + "），请稍后重试", e);
        } finally {
            if (!managed) {
                DbUtil.getInstance().closeQuietly(conn);
            }
        }
    }

    /**
     * 执行 INSERT/UPDATE/DELETE。
     *
     * @param sql    SQL 语句（参数使用 ? 占位）
     * @param params 参数
     * @return 受影响行数
     */
    protected int executeUpdate(String sql, Object... params) {
        return withConnection(conn -> {
            try (PreparedStatement ps = conn.prepareStatement(sql)) {
                setParams(ps, params);
                return ps.executeUpdate();
            }
        });
    }

    /**
     * 执行 INSERT 并返回自增主键。
     *
     * @param sql    SQL 语句
     * @param params 参数
     * @return 自增主键
     */
    protected long executeInsert(String sql, Object... params) {
        return withConnection(conn -> {
            try (PreparedStatement ps = conn.prepareStatement(sql, Statement.RETURN_GENERATED_KEYS)) {
                setParams(ps, params);
                ps.executeUpdate();
                try (ResultSet keys = ps.getGeneratedKeys()) {
                    if (keys.next()) {
                        return keys.getLong(1);
                    }
                }
            }
            throw new SQLException("插入成功但未获取到自增主键");
        });
    }

    /**
     * 查询多行并映射。
     *
     * @param sql    SQL 语句
     * @param mapper 行映射器
     * @param params 参数
     * @param <R>    结果类型
     * @return 结果列表（无结果返回空列表）
     */
    protected <R> List<R> queryList(String sql, RowMapper<R> mapper, Object... params) {
        return withConnection(conn -> {
            try (PreparedStatement ps = conn.prepareStatement(sql)) {
                setParams(ps, params);
                try (ResultSet rs = ps.executeQuery()) {
                    List<R> list = new ArrayList<>();
                    while (rs.next()) {
                        list.add(mapper.mapRow(rs));
                    }
                    return list;
                }
            }
        });
    }

    /**
     * 查询单行并映射。
     *
     * @param sql    SQL 语句
     * @param mapper 行映射器
     * @param params 参数
     * @param <R>    结果类型
     * @return 结果（无结果返回空 Optional）
     */
    protected <R> Optional<R> queryOne(String sql, RowMapper<R> mapper, Object... params) {
        List<R> list = queryList(sql, mapper, params);
        return list.isEmpty() ? Optional.empty() : Optional.of(list.get(0));
    }

    /**
     * 查询单个整数（如 COUNT(*)）。
     *
     * @param sql    SQL 语句
     * @param params 参数
     * @return 整数结果，NULL 时返回 0
     */
    protected int queryInt(String sql, Object... params) {
        Optional<Integer> value = queryOne(sql, rs -> rs.getInt(1), params);
        return value.orElse(0);
    }

    /**
     * 查询单个字符串。
     *
     * @param sql    SQL 语句
     * @param params 参数
     * @return 字符串结果
     */
    protected Optional<String> queryString(String sql, Object... params) {
        return queryOne(sql, rs -> rs.getString(1), params);
    }

    /**
     * 查询单个浮点数。
     *
     * @param sql    SQL 语句
     * @param params 参数
     * @return 浮点结果，NULL 时返回 0
     */
    protected double queryDouble(String sql, Object... params) {
        Optional<Double> value = queryOne(sql, rs -> rs.getDouble(1), params);
        return value.orElse(0.0D);
    }

    // ------------------------------------------------------------------ 参数绑定与类型转换

    /**
     * 绑定 PreparedStatement 参数，统一处理 LocalDateTime、BigDecimal、Boolean 与枚举。
     *
     * @param ps     PreparedStatement
     * @param params 参数数组
     * @throws SQLException 绑定失败
     */
    protected static void setParams(PreparedStatement ps, Object[] params) throws SQLException {
        if (params == null) {
            return;
        }
        for (int i = 0; i < params.length; i++) {
            Object value = params[i];
            int index = i + 1;
            if (value == null) {
                ps.setObject(index, null);
            } else if (value instanceof LocalDateTime) {
                ps.setString(index, formatDateTime((LocalDateTime) value));
            } else if (value instanceof BigDecimal) {
                ps.setBigDecimal(index, (BigDecimal) value);
            } else if (value instanceof Boolean) {
                ps.setInt(index, ((Boolean) value) ? 1 : 0);
            } else if (value instanceof Enum) {
                ps.setString(index, ((Enum<?>) value).name());
            } else {
                ps.setObject(index, value);
            }
        }
    }

    /**
     * 读取 TEXT 时间列并解析为 LocalDateTime。
     *
     * @param rs     结果集
     * @param column 列名
     * @return 时间，NULL 返回 null
     * @throws SQLException 读取失败
     */
    protected static LocalDateTime readDateTime(ResultSet rs, String column) throws SQLException {
        String value = rs.getString(column);
        if (value == null || value.isBlank()) {
            return null;
        }
        String trimmed = value.trim();
        try {
            return LocalDateTime.parse(trimmed, DATE_TIME_FORMATTER);
        } catch (DateTimeParseException e) {
            return LocalDateTime.parse(trimmed, DateTimeFormatter.ISO_LOCAL_DATE_TIME);
        }
    }

    /**
     * 把 LocalDateTime 格式化为数据库 TEXT 形式。
     *
     * @param time 时间
     * @return 格式化字符串，null 返回 null
     */
    protected static String formatDateTime(LocalDateTime time) {
        return time == null ? null : time.format(DATE_TIME_FORMATTER);
    }

    /**
     * 读取 INTEGER(0/1) 布尔列。
     *
     * @param rs     结果集
     * @param column 列名
     * @return 布尔值
     * @throws SQLException 读取失败
     */
    protected static boolean readBoolean(ResultSet rs, String column) throws SQLException {
        return rs.getInt(column) != 0;
    }

    /**
     * 读取可空整数列。
     *
     * @param rs     结果集
     * @param column 列名
     * @return 整数，NULL 返回 null
     * @throws SQLException 读取失败
     */
    protected static Integer readInteger(ResultSet rs, String column) throws SQLException {
        int value = rs.getInt(column);
        return rs.wasNull() ? null : value;
    }

    /**
     * 读取可空长整型列。
     *
     * @param rs     结果集
     * @param column 列名
     * @return 长整型，NULL 返回 null
     * @throws SQLException 读取失败
     */
    protected static Long readLong(ResultSet rs, String column) throws SQLException {
        long value = rs.getLong(column);
        return rs.wasNull() ? null : value;
    }

    /**
     * 读取 REAL 金额列并转 BigDecimal。
     *
     * @param rs     结果集
     * @param column 列名
     * @return 金额，NULL 返回 null
     * @throws SQLException 读取失败
     */
    protected static BigDecimal readBigDecimal(ResultSet rs, String column) throws SQLException {
        return rs.getBigDecimal(column);
    }
}
