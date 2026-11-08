package edu.campus.recycle.dao.impl;

import edu.campus.recycle.dao.ItemDao;
import edu.campus.recycle.dto.ItemQuery;
import edu.campus.recycle.dto.StatisticsDTO;
import edu.campus.recycle.entity.Item;
import edu.campus.recycle.entity.ItemStatus;
import edu.campus.recycle.util.CreditFirstItemSortStrategy;
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
                new PriceDescItemSortStrategy(), new CreditFirstItemSortStrategy()));
    }

    public ItemDaoImpl(List<ItemSortStrategy> sortStrategies) {
        this.sortStrategies = sortStrategies == null || sortStrategies.isEmpty()
                ? List.of(new LatestItemSortStrategy(), new PriceAscItemSortStrategy(),
                new PriceDescItemSortStrategy(), new CreditFirstItemSortStrategy())
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
        // 第 3 轮裁决 v1.1 §13-8：未显式给状态时默认 PENDING（待审核），DRAFT 仅供草稿
        String status = item.getStatus() == null || item.getStatus().isBlank()
                ? ItemStatus.PENDING.getCode() : item.getStatus();
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
