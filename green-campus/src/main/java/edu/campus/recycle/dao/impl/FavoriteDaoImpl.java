package edu.campus.recycle.dao.impl;

import edu.campus.recycle.dao.FavoriteDao;
import edu.campus.recycle.entity.Favorite;
import edu.campus.recycle.entity.Item;
import edu.campus.recycle.util.RowMapper;

import java.time.LocalDateTime;
import java.util.List;
import java.util.Optional;

/**
 * 收藏 DAO 实现。{@code UNIQUE(user_id, item_id)} 由数据库兜底，Service 层以 toggle 语义调用（BR-09）；
 * "我的收藏"联表返回物品视图，避免界面多次查询。
 */
public class FavoriteDaoImpl extends AbstractJdbcDao<Favorite> implements FavoriteDao {

    private static final String TABLE = "favorite";

    private static final String COLUMNS = "id, user_id, item_id, created_at";

    private static final String ITEM_COLUMNS = "i.id, i.owner_id, i.category_id, i.title, i.description,"
            + " i.trade_type, i.price, i.original_price, i.condition_level, i.tags, i.status, i.view_count,"
            + " i.favorite_count, i.audit_remark, i.created_at, i.updated_at, i.published_at";

    private static final RowMapper<Favorite> ROW_MAPPER = rs -> {
        Favorite favorite = new Favorite();
        favorite.setId(rs.getInt("id"));
        favorite.setUserId(rs.getInt("user_id"));
        favorite.setItemId(rs.getInt("item_id"));
        favorite.setCreatedAt(readDateTime(rs, "created_at"));
        return favorite;
    };

    private static final RowMapper<Item> ITEM_MAPPER = rs -> {
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

    @Override
    protected String tableName() {
        return TABLE;
    }

    @Override
    protected RowMapper<Favorite> rowMapper() {
        return ROW_MAPPER;
    }

    @Override
    public Optional<Favorite> findById(Integer id) {
        return queryOne("SELECT " + COLUMNS + " FROM " + TABLE + " WHERE id = ?", ROW_MAPPER, id);
    }

    @Override
    public List<Favorite> findAll() {
        return queryList("SELECT " + COLUMNS + " FROM " + TABLE + " ORDER BY id", ROW_MAPPER);
    }

    @Override
    public int insert(Favorite favorite) {
        LocalDateTime createdAt = favorite.getCreatedAt() == null
                ? LocalDateTime.now() : favorite.getCreatedAt();
        long id = executeInsert("INSERT INTO " + TABLE
                        + " (user_id, item_id, created_at) VALUES (?, ?, ?)",
                favorite.getUserId(), favorite.getItemId(), formatDateTime(createdAt));
        favorite.setId((int) id);
        return 1;
    }

    @Override
    public int update(Favorite favorite) {
        return executeUpdate("UPDATE " + TABLE + " SET user_id = ?, item_id = ? WHERE id = ?",
                favorite.getUserId(), favorite.getItemId(), favorite.getId());
    }

    @Override
    public int deleteById(Integer id) {
        return executeUpdate("DELETE FROM " + TABLE + " WHERE id = ?", id);
    }

    @Override
    public boolean exists(int userId, int itemId) {
        return queryInt("SELECT COUNT(*) FROM " + TABLE + " WHERE user_id = ? AND item_id = ?",
                userId, itemId) > 0;
    }

    @Override
    public int delete(int userId, int itemId) {
        return executeUpdate("DELETE FROM " + TABLE + " WHERE user_id = ? AND item_id = ?", userId, itemId);
    }

    @Override
    public List<Item> findItemsByUserId(int userId) {
        String sql = "SELECT " + ITEM_COLUMNS + " FROM " + TABLE + " f"
                + " INNER JOIN item i ON i.id = f.item_id"
                + " WHERE f.user_id = ? ORDER BY f.created_at DESC, f.id DESC";
        return queryList(sql, ITEM_MAPPER, userId);
    }

    @Override
    public int countByItemId(int itemId) {
        return queryInt("SELECT COUNT(*) FROM " + TABLE + " WHERE item_id = ?", itemId);
    }
}
