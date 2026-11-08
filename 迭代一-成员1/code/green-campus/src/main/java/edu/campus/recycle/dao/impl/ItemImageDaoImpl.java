package edu.campus.recycle.dao.impl;

import edu.campus.recycle.dao.ItemImageDao;
import edu.campus.recycle.entity.ItemImage;
import edu.campus.recycle.util.RowMapper;

import java.sql.PreparedStatement;
import java.time.LocalDateTime;
import java.util.List;
import java.util.Optional;

/**
 * 物品图片 DAO 实现。图片二进制不入库，仅保存相对路径（BR-12）；
 * 批量写入在单个连接/事务内完成，保证"发布物品 + 图片"要么全成要么全败。
 */
public class ItemImageDaoImpl extends AbstractJdbcDao<ItemImage> implements ItemImageDao {

    private static final String TABLE = "item_image";

    private static final String COLUMNS = "id, item_id, file_path, sort_order, created_at";

    private static final String INSERT_SQL = "INSERT INTO " + TABLE
            + " (item_id, file_path, sort_order, created_at) VALUES (?, ?, ?, ?)";

    private static final RowMapper<ItemImage> ROW_MAPPER = rs -> {
        ItemImage image = new ItemImage();
        image.setId(rs.getInt("id"));
        image.setItemId(rs.getInt("item_id"));
        image.setFilePath(rs.getString("file_path"));
        image.setSortOrder(rs.getInt("sort_order"));
        image.setCreatedAt(readDateTime(rs, "created_at"));
        return image;
    };

    @Override
    protected String tableName() {
        return TABLE;
    }

    @Override
    protected RowMapper<ItemImage> rowMapper() {
        return ROW_MAPPER;
    }

    @Override
    public Optional<ItemImage> findById(Integer id) {
        return queryOne("SELECT " + COLUMNS + " FROM " + TABLE + " WHERE id = ?", ROW_MAPPER, id);
    }

    @Override
    public List<ItemImage> findAll() {
        return queryList("SELECT " + COLUMNS + " FROM " + TABLE + " ORDER BY item_id, sort_order", ROW_MAPPER);
    }

    @Override
    public int insert(ItemImage image) {
        LocalDateTime createdAt = image.getCreatedAt() == null ? LocalDateTime.now() : image.getCreatedAt();
        long id = executeInsert(INSERT_SQL, image.getItemId(), image.getFilePath(),
                image.getSortOrder() == null ? 0 : image.getSortOrder(), formatDateTime(createdAt));
        image.setId((int) id);
        return 1;
    }

    @Override
    public int update(ItemImage image) {
        return executeUpdate("UPDATE " + TABLE + " SET item_id = ?, file_path = ?, sort_order = ? WHERE id = ?",
                image.getItemId(), image.getFilePath(), image.getSortOrder(), image.getId());
    }

    @Override
    public int deleteById(Integer id) {
        return executeUpdate("DELETE FROM " + TABLE + " WHERE id = ?", id);
    }

    @Override
    public int batchInsert(List<ItemImage> images) {
        if (images == null || images.isEmpty()) {
            return 0;
        }
        return withConnection(conn -> {
            int affected = 0;
            try (PreparedStatement ps = conn.prepareStatement(INSERT_SQL)) {
                int index = 0;
                for (ItemImage image : images) {
                    LocalDateTime createdAt = image.getCreatedAt() == null
                            ? LocalDateTime.now() : image.getCreatedAt();
                    ps.setInt(1, image.getItemId());
                    ps.setString(2, image.getFilePath());
                    ps.setInt(3, image.getSortOrder() == null ? index : image.getSortOrder());
                    ps.setString(4, formatDateTime(createdAt));
                    ps.addBatch();
                    index++;
                }
                int[] counts = ps.executeBatch();
                for (int count : counts) {
                    affected += count == PreparedStatement.SUCCESS_NO_INFO ? 1 : count;
                }
            }
            return affected;
        });
    }

    @Override
    public List<ItemImage> findByItemId(int itemId) {
        return queryList("SELECT " + COLUMNS + " FROM " + TABLE
                + " WHERE item_id = ? ORDER BY sort_order, id", ROW_MAPPER, itemId);
    }

    @Override
    public int deleteByItemId(int itemId) {
        return executeUpdate("DELETE FROM " + TABLE + " WHERE item_id = ?", itemId);
    }
}
