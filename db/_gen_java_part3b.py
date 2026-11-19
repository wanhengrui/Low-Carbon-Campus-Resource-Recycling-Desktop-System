# -*- coding: utf-8 -*-
"""D7 生成器 part3b：UserDaoImpl、CategoryDaoImpl、ItemDaoImpl。"""
import os

BASE = r'C:\Users\wanhe\Desktop\软件构造\迭代一-成员1\code\green-campus'


def write(rel, content):
    path = os.path.join(BASE, rel)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'w', encoding='utf-8', newline='\n') as f:
        f.write(content)
    print('  + %-82s %5d B' % (rel, len(content.encode('utf-8'))))


def out(pkg, cls):
    return os.path.join('src', 'main', 'java', 'edu', 'campus', 'recycle', *pkg.split('.'), cls + '.java')


USER_DAO_IMPL = '''package edu.campus.recycle.dao.impl;

import edu.campus.recycle.dao.UserDao;
import edu.campus.recycle.entity.User;
import edu.campus.recycle.util.RowMapper;

import java.time.LocalDateTime;
import java.util.ArrayList;
import java.util.List;
import java.util.Optional;

/**
 * 用户 DAO 实现：{@code PreparedStatement} 全参数化，所有 SQL 常量集中声明，
 * 通用连接/异常处理由 {@link AbstractJdbcDao} 模板方法完成。
 */
public class UserDaoImpl extends AbstractJdbcDao<User> implements UserDao {

    private static final String TABLE = "\\"user\\"";

    private static final String COLUMNS = "id, username, password_hash, salt, real_name, student_no, "
            + "role, college, contact, credit_score, status, fail_count, locked_until, "
            + "created_at, updated_at, last_login_at";

    private static final RowMapper<User> ROW_MAPPER = rs -> {
        User user = new User();
        user.setId(rs.getInt("id"));
        user.setUsername(rs.getString("username"));
        user.setPasswordHash(rs.getString("password_hash"));
        user.setSalt(rs.getString("salt"));
        user.setRealName(rs.getString("real_name"));
        user.setStudentNo(rs.getString("student_no"));
        user.setRole(rs.getString("role"));
        user.setCollege(rs.getString("college"));
        user.setContact(rs.getString("contact"));
        user.setCreditScore(rs.getInt("credit_score"));
        user.setStatus(rs.getString("status"));
        user.setFailCount(rs.getInt("fail_count"));
        user.setLockedUntil(readDateTime(rs, "locked_until"));
        user.setCreatedAt(readDateTime(rs, "created_at"));
        user.setUpdatedAt(readDateTime(rs, "updated_at"));
        user.setLastLoginAt(readDateTime(rs, "last_login_at"));
        return user;
    };

    @Override
    protected String tableName() {
        return "user";
    }

    @Override
    protected RowMapper<User> rowMapper() {
        return ROW_MAPPER;
    }

    // ------------------------------------------------------------------ BaseDao

    @Override
    public Optional<User> findById(Integer id) {
        return queryOne("SELECT " + COLUMNS + " FROM " + TABLE + " WHERE id = ?", ROW_MAPPER, id);
    }

    @Override
    public List<User> findAll() {
        return queryList("SELECT " + COLUMNS + " FROM " + TABLE + " ORDER BY id", ROW_MAPPER);
    }

    @Override
    public int insert(User user) {
        LocalDateTime now = LocalDateTime.now();
        LocalDateTime createdAt = user.getCreatedAt() == null ? now : user.getCreatedAt();
        LocalDateTime updatedAt = user.getUpdatedAt() == null ? now : user.getUpdatedAt();
        String role = user.getRole() == null ? "STUDENT" : user.getRole();
        String status = user.getStatus() == null ? "ACTIVE" : user.getStatus();
        int creditScore = user.getCreditScore() == null ? 100 : user.getCreditScore();
        int failCount = user.getFailCount() == null ? 0 : user.getFailCount();

        long id = executeInsert("INSERT INTO " + TABLE
                        + " (username, password_hash, salt, real_name, student_no, role, college, contact,"
                        + " credit_score, status, fail_count, locked_until, created_at, updated_at, last_login_at)"
                        + " VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                user.getUsername(), user.getPasswordHash(), user.getSalt(), user.getRealName(),
                user.getStudentNo(), role, user.getCollege(), user.getContact(), creditScore, status,
                failCount, formatDateTime(user.getLockedUntil()), formatDateTime(createdAt),
                formatDateTime(updatedAt), formatDateTime(user.getLastLoginAt()));
        user.setId((int) id);
        return 1;
    }

    @Override
    public int update(User user) {
        LocalDateTime updatedAt = user.getUpdatedAt() == null ? LocalDateTime.now() : user.getUpdatedAt();
        return executeUpdate("UPDATE " + TABLE + " SET username = ?, password_hash = ?, salt = ?,"
                        + " real_name = ?, student_no = ?, role = ?, college = ?, contact = ?,"
                        + " credit_score = ?, status = ?, fail_count = ?, locked_until = ?,"
                        + " updated_at = ?, last_login_at = ? WHERE id = ?",
                user.getUsername(), user.getPasswordHash(), user.getSalt(), user.getRealName(),
                user.getStudentNo(), user.getRole(), user.getCollege(), user.getContact(),
                user.getCreditScore(), user.getStatus(), user.getFailCount(),
                formatDateTime(user.getLockedUntil()), formatDateTime(updatedAt),
                formatDateTime(user.getLastLoginAt()), user.getId());
    }

    @Override
    public int deleteById(Integer id) {
        return executeUpdate("DELETE FROM " + TABLE + " WHERE id = ?", id);
    }

    // ------------------------------------------------------------------ 登录域查询

    @Override
    public Optional<User> findByUsername(String username) {
        return queryOne("SELECT " + COLUMNS + " FROM " + TABLE + " WHERE username = ?", ROW_MAPPER, username);
    }

    @Override
    public boolean existsByUsername(String username) {
        return queryInt("SELECT COUNT(*) FROM " + TABLE + " WHERE username = ?", username) > 0;
    }

    @Override
    public boolean existsByStudentNo(String studentNo) {
        if (studentNo == null || studentNo.isBlank()) {
            return false;
        }
        return queryInt("SELECT COUNT(*) FROM " + TABLE + " WHERE student_no = ?", studentNo) > 0;
    }

    @Override
    public List<User> findByCondition(String keyword, String role, int pageNo, int pageSize) {
        StringBuilder sql = new StringBuilder("SELECT " + COLUMNS + " FROM " + TABLE + " WHERE 1 = 1");
        List<Object> params = new ArrayList<>();
        appendCondition(sql, params, keyword, role);
        sql.append(" ORDER BY id LIMIT ? OFFSET ?");
        params.add(pageSize <= 0 ? 10 : pageSize);
        params.add(Math.max(pageNo, 1) - 1 < 0 ? 0 : (Math.max(pageNo, 1) - 1) * (pageSize <= 0 ? 10 : pageSize));
        return queryList(sql.toString(), ROW_MAPPER, params.toArray());
    }

    @Override
    public int countByCondition(String keyword, String role) {
        StringBuilder sql = new StringBuilder("SELECT COUNT(*) FROM " + TABLE + " WHERE 1 = 1");
        List<Object> params = new ArrayList<>();
        appendCondition(sql, params, keyword, role);
        return queryInt(sql.toString(), params.toArray());
    }

    private void appendCondition(StringBuilder sql, List<Object> params, String keyword, String role) {
        if (keyword != null && !keyword.isBlank()) {
            String like = "%" + keyword.trim() + "%";
            sql.append(" AND (username LIKE ? OR real_name LIKE ? OR IFNULL(student_no, '') LIKE ?)");
            params.add(like);
            params.add(like);
            params.add(like);
        }
        if (role != null && !role.isBlank()) {
            sql.append(" AND role = ?");
            params.add(role);
        }
    }

    @Override
    public int updateLoginSuccess(int userId, LocalDateTime loginTime) {
        return executeUpdate("UPDATE " + TABLE + " SET fail_count = 0, locked_until = NULL,"
                + " last_login_at = ?, updated_at = ? WHERE id = ?",
                formatDateTime(loginTime == null ? LocalDateTime.now() : loginTime),
                formatDateTime(LocalDateTime.now()), userId);
    }

    @Override
    public int updateFailCount(int userId, int failCount, LocalDateTime lockedUntil) {
        return executeUpdate("UPDATE " + TABLE + " SET fail_count = ?, locked_until = ?, updated_at = ?"
                + " WHERE id = ?", failCount, formatDateTime(lockedUntil),
                formatDateTime(LocalDateTime.now()), userId);
    }

    @Override
    public int updateCreditScore(int userId, int newScore) {
        return executeUpdate("UPDATE " + TABLE + " SET credit_score = ?, updated_at = ? WHERE id = ?",
                newScore, formatDateTime(LocalDateTime.now()), userId);
    }

    @Override
    public int updateStatus(int userId, String status) {
        return executeUpdate("UPDATE " + TABLE + " SET status = ?, updated_at = ? WHERE id = ?",
                status, formatDateTime(LocalDateTime.now()), userId);
    }
}
'''
write(out('dao.impl', 'UserDaoImpl'), USER_DAO_IMPL)

CATEGORY_DAO_IMPL = '''package edu.campus.recycle.dao.impl;

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
'''
write(out('dao.impl', 'CategoryDaoImpl'), CATEGORY_DAO_IMPL)

ITEM_DAO_IMPL = '''package edu.campus.recycle.dao.impl;

import edu.campus.recycle.dao.ItemDao;
import edu.campus.recycle.dto.ItemQuery;
import edu.campus.recycle.dto.StatisticsDTO;
import edu.campus.recycle.entity.Item;
import edu.campus.recycle.util.ItemSortStrategy;
import edu.campus.recycle.util.LatestItemSortStrategy;
import edu.campus.recycle.util.PriceAscItemSortStrategy;
import edu.campus.recycle.util.PriceDescItemSortStrategy;
import edu.campus.recycle.util.RowMapper;

import java.math.BigDecimal;
import java.time.LocalDateTime;
import java.util.ArrayList;
import java.util.List;
import java.util.Optional;

/**
 * 物品 DAO 实现。
 *
 * <p>检索把动态条件拼接为参数化 SQL（只拼 SQL 片段、不拼用户输入），
 * ORDER BY 通过 {@link ItemSortStrategy} 策略解析，杜绝排序字段注入。</p>
 */
public class ItemDaoImpl extends AbstractJdbcDao<Item> implements ItemDao {

    private static final String TABLE = "item";

    private static final String COLUMNS = "id, owner_id, category_id, title, description, trade_type, "
            + "price, original_price, condition_level, tags, status, view_count, favorite_count, "
            + "audit_remark, created_at, updated_at, published_at";

    private static final String COLUMNS_ALIASED = "i.id, i.owner_id, i.category_id, i.title, i.description, "
            + "i.trade_type, i.price, i.original_price, i.condition_level, i.tags, i.status, i.view_count, "
            + "i.favorite_count, i.audit_remark, i.created_at, i.updated_at, i.published_at";

    private static final RowMapper<Item> ROW_MAPPER = rs -> {
        Item item = new Item();
        item.setId(rs.getInt("id"));
        item.setOwnerId(rs.getInt("owner_id"));
        item.setCategoryId(rs.getInt("category_id"));
        item.setTitle(rs.getString("title"));
        item.setDescription(rs.getString("description"));
        item.setTradeType(rs.getString("trade_type"));
        item.setPrice(readBigDecimal(rs, "price"));
        item.setOriginalPrice(readBigDecimal(rs, "original_price"));
        item.setConditionLevel(rs.getInt("condition_level"));
        item.setTags(rs.getString("tags"));
        item.setStatus(rs.getString("status"));
        item.setViewCount(rs.getInt("view_count"));
        item.setFavoriteCount(rs.getInt("favorite_count"));
        item.setAuditRemark(rs.getString("audit_remark"));
        item.setCreatedAt(readDateTime(rs, "created_at"));
        item.setUpdatedAt(readDateTime(rs, "updated_at"));
        item.setPublishedAt(readDateTime(rs, "published_at"));
        return item;
    };

    /** 排序策略集合（策略模式：新增排序只需注册新实现） */
    private final List<ItemSortStrategy> sortStrategies;

    public ItemDaoImpl() {
        this(List.of(new LatestItemSortStrategy(), new PriceAscItemSortStrategy(),
                new PriceDescItemSortStrategy()));
    }

    public ItemDaoImpl(List<ItemSortStrategy> sortStrategies) {
        this.sortStrategies = sortStrategies == null || sortStrategies.isEmpty()
                ? List.of(new LatestItemSortStrategy(), new PriceAscItemSortStrategy(),
                new PriceDescItemSortStrategy())
                : List.copyOf(sortStrategies);
    }

    @Override
    protected String tableName() {
        return "item";
    }

    @Override
    protected RowMapper<Item> rowMapper() {
        return ROW_MAPPER;
    }

    // ------------------------------------------------------------------ BaseDao

    @Override
    public Optional<Item> findById(Integer id) {
        return queryOne("SELECT " + COLUMNS + " FROM " + TABLE + " WHERE id = ?", ROW_MAPPER, id);
    }

    @Override
    public Optional<Item> findById(int id) {
        return findById(Integer.valueOf(id));
    }

    @Override
    public List<Item> findAll() {
        return queryList("SELECT " + COLUMNS + " FROM " + TABLE + " ORDER BY id", ROW_MAPPER);
    }

    @Override
    public int insert(Item item) {
        LocalDateTime now = LocalDateTime.now();
        LocalDateTime createdAt = item.getCreatedAt() == null ? now : item.getCreatedAt();
        LocalDateTime updatedAt = item.getUpdatedAt() == null ? now : item.getUpdatedAt();
        String status = item.getStatus() == null ? "ON_SALE" : item.getStatus();
        long id = executeInsert("INSERT INTO " + TABLE
                        + " (owner_id, category_id, title, description, trade_type, price, original_price,"
                        + " condition_level, tags, status, view_count, favorite_count, audit_remark,"
                        + " created_at, updated_at, published_at)"
                        + " VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                item.getOwnerId(), item.getCategoryId(), item.getTitle(), item.getDescription(),
                item.getTradeType(), item.getPrice() == null ? BigDecimal.ZERO : item.getPrice(),
                item.getOriginalPrice(),
                item.getConditionLevel() == null ? 9 : item.getConditionLevel(),
                item.getTags(), status,
                item.getViewCount() == null ? 0 : item.getViewCount(),
                item.getFavoriteCount() == null ? 0 : item.getFavoriteCount(),
                item.getAuditRemark(), formatDateTime(createdAt), formatDateTime(updatedAt),
                formatDateTime(item.getPublishedAt()));
        item.setId((int) id);
        return 1;
    }

    @Override
    public int update(Item item) {
        LocalDateTime updatedAt = item.getUpdatedAt() == null ? LocalDateTime.now() : item.getUpdatedAt();
        return executeUpdate("UPDATE " + TABLE + " SET owner_id = ?, category_id = ?, title = ?,"
                        + " description = ?, trade_type = ?, price = ?, original_price = ?, condition_level = ?,"
                        + " tags = ?, status = ?, view_count = ?, favorite_count = ?, audit_remark = ?,"
                        + " updated_at = ?, published_at = ? WHERE id = ?",
                item.getOwnerId(), item.getCategoryId(), item.getTitle(), item.getDescription(),
                item.getTradeType(), item.getPrice(), item.getOriginalPrice(), item.getConditionLevel(),
                item.getTags(), item.getStatus(),
                item.getViewCount() == null ? 0 : item.getViewCount(),
                item.getFavoriteCount() == null ? 0 : item.getFavoriteCount(),
                item.getAuditRemark(), formatDateTime(updatedAt),
                formatDateTime(item.getPublishedAt()), item.getId());
    }

    @Override
    public int deleteById(Integer id) {
        return executeUpdate("DELETE FROM " + TABLE + " WHERE id = ?", id);
    }

    // ------------------------------------------------------------------ 检索

    @Override
    public List<Item> search(ItemQuery query) {
        StringBuilder sql = new StringBuilder("SELECT " + COLUMNS_ALIASED + " FROM " + TABLE + " i");
        List<Object> params = new ArrayList<>();
        appendCondition(sql, params, query);
        sql.append(" ORDER BY ").append(resolveSortStrategy(query.getSortByOrDefault()).orderByClause());
        sql.append(" LIMIT ? OFFSET ?");
        params.add(query.getLimit());
        params.add(query.getOffset());
        return queryList(sql.toString(), ROW_MAPPER, params.toArray());
    }

    @Override
    public int countSearch(ItemQuery query) {
        StringBuilder sql = new StringBuilder("SELECT COUNT(*) FROM " + TABLE + " i");
        List<Object> params = new ArrayList<>();
        appendCondition(sql, params, query);
        return queryInt(sql.toString(), params.toArray());
    }

    private void appendCondition(StringBuilder sql, List<Object> params, ItemQuery query) {
        sql.append(" WHERE 1 = 1");
        if (query.getKeyword() != null && !query.getKeyword().isBlank()) {
            String like = "%" + query.getKeyword().trim() + "%";
            sql.append(" AND (i.title LIKE ? OR i.description LIKE ? OR IFNULL(i.tags, '') LIKE ?)");
            params.add(like);
            params.add(like);
            params.add(like);
        }
        if (query.getCategoryId() != null) {
            sql.append(" AND (i.category_id = ? OR i.category_id IN"
                    + " (SELECT c.id FROM category c WHERE c.parent_id = ?))");
            params.add(query.getCategoryId());
            params.add(query.getCategoryId());
        }
        if (query.getMinPrice() != null) {
            sql.append(" AND i.price >= ?");
            params.add(query.getMinPrice());
        }
        if (query.getMaxPrice() != null) {
            sql.append(" AND i.price <= ?");
            params.add(query.getMaxPrice());
        }
        if (query.getTradeType() != null && !query.getTradeType().isBlank()) {
            sql.append(" AND i.trade_type = ?");
            params.add(query.getTradeType());
        }
        if (query.getStatus() != null && !query.getStatus().isBlank()) {
            sql.append(" AND i.status = ?");
            params.add(query.getStatus());
        }
        if (query.getOwnerId() != null) {
            sql.append(" AND i.owner_id = ?");
            params.add(query.getOwnerId());
        }
    }

    private ItemSortStrategy resolveSortStrategy(String code) {
        for (ItemSortStrategy strategy : sortStrategies) {
            if (strategy.getCode().equalsIgnoreCase(code)) {
                return strategy;
            }
        }
        return sortStrategies.get(0);
    }

    // ------------------------------------------------------------------ 状态维护

    @Override
    public int updateStatus(int itemId, String status, String remark) {
        return executeUpdate("UPDATE " + TABLE + " SET status = ?, audit_remark = ?, updated_at = ?"
                + " WHERE id = ?", status, remark, formatDateTime(LocalDateTime.now()), itemId);
    }

    @Override
    public int increaseViewCount(int itemId) {
        return executeUpdate("UPDATE " + TABLE + " SET view_count = view_count + 1 WHERE id = ?", itemId);
    }

    @Override
    public int increaseFavoriteCount(int itemId, int delta) {
        return executeUpdate("UPDATE " + TABLE
                + " SET favorite_count = MAX(0, favorite_count + ?) WHERE id = ?", delta, itemId);
    }

    @Override
    public List<Item> findByOwnerId(int ownerId) {
        return queryList("SELECT " + COLUMNS + " FROM " + TABLE
                + " WHERE owner_id = ? ORDER BY created_at DESC, id DESC", ROW_MAPPER, ownerId);
    }

    @Override
    public List<StatisticsDTO> countByCategory() {
        String sql = "SELECT c.name AS category_name, COUNT(tf.id) AS flow_count,"
                + " IFNULL(SUM(tf.amount), 0) AS total_amount"
                + " FROM category c"
                + " LEFT JOIN item i ON i.category_id = c.id"
                + " LEFT JOIN trade_flow tf ON tf.item_id = i.id AND tf.status = 'DONE'"
                + " GROUP BY c.id, c.name ORDER BY flow_count DESC, c.id";
        return queryList(sql, rs -> new StatisticsDTO(
                rs.getString("category_name"),
                rs.getLong("flow_count"),
                readBigDecimal(rs, "total_amount"),
                0.0D));
    }
}
'''
write(out('dao.impl', 'ItemDaoImpl'), ITEM_DAO_IMPL)

print('\npart3b 完成（User/Category/Item DAO 实现）。')
