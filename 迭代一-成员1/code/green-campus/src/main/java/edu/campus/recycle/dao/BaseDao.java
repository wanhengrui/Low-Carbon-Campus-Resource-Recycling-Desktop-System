package edu.campus.recycle.dao;

import java.util.List;
import java.util.Optional;

/**
 * 通用 DAO 接口（契约第 5 节）。
 *
 * <p>定义单表最基础的 5 个持久化操作；各业务 DAO 继承本接口后补充专有查询方法。
 * 模板方法 {@code AbstractJdbcDao} 提供这些方法的默认实现，实现类只需给出
 * 表名与行映射器。</p>
 *
 * @param <T>  实体类型
 * @param <ID> 主键类型
 */
public interface BaseDao<T, ID> {

    /**
     * 按主键查询。
     *
     * @param id 主键
     * @return 实体（不存在时返回空 Optional）
     */
    Optional<T> findById(ID id);

    /**
     * 查询全部记录（按主键升序）。
     *
     * @return 实体列表
     */
    List<T> findAll();

    /**
     * 插入记录。
     *
     * @param entity 实体
     * @return 受影响行数
     */
    int insert(T entity);

    /**
     * 按主键更新记录。
     *
     * @param entity 实体（必须携带主键）
     * @return 受影响行数
     */
    int update(T entity);

    /**
     * 按主键删除记录。
     *
     * @param id 主键
     * @return 受影响行数
     */
    int deleteById(ID id);
}
