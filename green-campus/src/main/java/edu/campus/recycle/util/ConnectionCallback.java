package edu.campus.recycle.util;

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
