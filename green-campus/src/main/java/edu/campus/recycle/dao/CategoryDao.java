package edu.campus.recycle.dao;

import edu.campus.recycle.entity.Category;

import java.util.List;

/**
 * 分类 DAO（契约第 5 节）。支持两级分类树查询与启用状态维护。
 */
public interface CategoryDao extends BaseDao<Category, Integer> {

    /**
     * 查询全部启用分类（按 sort_order 升序）。
     *
     * @return 启用分类列表
     */
    List<Category> findEnabled();

    /**
     * 按父分类查询直接子分类；{@code parentId} 为 null 时查询一级分类。
     *
     * @param parentId 父分类ID，可为 null
     * @return 子分类列表
     */
    List<Category> findByParentId(Integer parentId);

    /**
     * 判断同一父分类下分类名是否已存在（UNIQUE(parent_id, name)）。
     *
     * @param parentId 父分类ID，可为 null
     * @param name     分类名
     * @return 已存在返回 true
     */
    boolean existsByName(Integer parentId, String name);

    /**
     * 启用/停用分类。
     *
     * @param id      分类ID
     * @param enabled 是否启用
     * @return 受影响行数
     */
    int updateEnabled(int id, boolean enabled);
}
