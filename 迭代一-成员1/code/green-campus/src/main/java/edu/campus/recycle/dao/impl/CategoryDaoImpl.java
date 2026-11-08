package edu.campus.recycle.dao.impl;

import edu.campus.recycle.dao.CategoryDao;
import edu.campus.recycle.entity.Category;
import edu.campus.recycle.util.RowMapper;

import java.time.LocalDateTime;
import java.util.List;
import java.util.Optional;

/**
 * 分类 DAO 实现。两级分类树的父子关系由 {@code parent_id} 自关联维护。
 */
public class CategoryDaoImpl extends AbstractJdbcDao<Category> implements CategoryDao {

    private static final String TABLE = "category";

    private static final String COLUMNS = "id, name, parent_id, sort_order, enabled, created_at";

    private static final RowMapper<Category> ROW_MAPPER = rs -> {
        Category category = new Category();
        category.setId(rs.getInt("id"));
        category.setName(rs.getString("name"));
        category.setParentId(readInteger(rs, "parent_id"));
        category.setSortOrder(rs.getInt("sort_order"));
        category.setEnabled(readBoolean(rs, "enabled"));
        category.setCreatedAt(readDateTime(rs, "created_at"));
        return category;
    };

    @Override
    protected String tableName() {
        return "category";
    }

    @Override
    protected RowMapper<Category> rowMapper() {
        return ROW_MAPPER;
    }

    @Override
    public Optional<Category> findById(Integer id) {
        return queryOne("SELECT " + COLUMNS + " FROM " + TABLE + " WHERE id = ?", ROW_MAPPER, id);
    }

    @Override
    public List<Category> findAll() {
        return queryList("SELECT " + COLUMNS + " FROM " + TABLE + " ORDER BY sort_order, id", ROW_MAPPER);
    }

    @Override
    public int insert(Category category) {
        LocalDateTime now = category.getCreatedAt() == null ? LocalDateTime.now() : category.getCreatedAt();
        long id = executeInsert("INSERT INTO " + TABLE
                        + " (name, parent_id, sort_order, enabled, created_at) VALUES (?, ?, ?, ?, ?)",
                category.getName(), category.getParentId(),
                category.getSortOrder() == null ? 0 : category.getSortOrder(),
                category.getEnabled() == null ? Boolean.TRUE : category.getEnabled(),
                formatDateTime(now));
        category.setId((int) id);
        return 1;
    }

    @Override
    public int update(Category category) {
        return executeUpdate("UPDATE " + TABLE + " SET name = ?, parent_id = ?, sort_order = ?, enabled = ?"
                        + " WHERE id = ?", category.getName(), category.getParentId(), category.getSortOrder(),
                category.getEnabled(), category.getId());
    }

    @Override
    public int deleteById(Integer id) {
        return executeUpdate("DELETE FROM " + TABLE + " WHERE id = ?", id);
    }

    @Override
    public List<Category> findEnabled() {
        return queryList("SELECT " + COLUMNS + " FROM " + TABLE
                + " WHERE enabled = 1 ORDER BY sort_order, id", ROW_MAPPER);
    }

    @Override
    public List<Category> findByParentId(Integer parentId) {
        if (parentId == null) {
            return queryList("SELECT " + COLUMNS + " FROM " + TABLE
                    + " WHERE parent_id IS NULL ORDER BY sort_order, id", ROW_MAPPER);
        }
        return queryList("SELECT " + COLUMNS + " FROM " + TABLE
                + " WHERE parent_id = ? ORDER BY sort_order, id", ROW_MAPPER, parentId);
    }

    @Override
    public boolean existsByName(Integer parentId, String name) {
        if (parentId == null) {
            return queryInt("SELECT COUNT(*) FROM " + TABLE
                    + " WHERE parent_id IS NULL AND name = ?", name) > 0;
        }
        return queryInt("SELECT COUNT(*) FROM " + TABLE
                + " WHERE parent_id = ? AND name = ?", parentId, name) > 0;
    }

    @Override
    public int updateEnabled(int id, boolean enabled) {
        return executeUpdate("UPDATE " + TABLE + " SET enabled = ? WHERE id = ?", enabled, id);
    }
}
