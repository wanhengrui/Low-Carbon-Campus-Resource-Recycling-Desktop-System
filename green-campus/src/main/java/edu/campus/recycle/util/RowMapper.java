package edu.campus.recycle.util;

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
