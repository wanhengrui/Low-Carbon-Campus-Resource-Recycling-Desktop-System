package edu.campus.recycle.dao.impl;

import edu.campus.recycle.dao.TradeMessageDao;
import edu.campus.recycle.entity.TradeMessage;
import edu.campus.recycle.util.RowMapper;

import java.time.LocalDateTime;
import java.util.List;
import java.util.Optional;

/**
 * 流转沟通消息 DAO 实现。会话维度为（物品, 用户A, 用户B），双向查询按时间升序返回。
 */
public class TradeMessageDaoImpl extends AbstractJdbcDao<TradeMessage> implements TradeMessageDao {

    private static final String TABLE = "trade_message";

    private static final String COLUMNS = "id, item_id, from_user_id, to_user_id, content, is_read, created_at";

    private static final RowMapper<TradeMessage> ROW_MAPPER = rs -> {
        TradeMessage message = new TradeMessage();
        message.setId(rs.getInt("id"));
        message.setItemId(rs.getInt("item_id"));
        message.setFromUserId(rs.getInt("from_user_id"));
        message.setToUserId(rs.getInt("to_user_id"));
        message.setContent(rs.getString("content"));
        message.setIsRead(readBoolean(rs, "is_read"));
        message.setCreatedAt(readDateTime(rs, "created_at"));
        return message;
    };

    @Override
    protected String tableName() {
        return TABLE;
    }

    @Override
    protected RowMapper<TradeMessage> rowMapper() {
        return ROW_MAPPER;
    }

    @Override
    public Optional<TradeMessage> findById(Integer id) {
        return queryOne("SELECT " + COLUMNS + " FROM " + TABLE + " WHERE id = ?", ROW_MAPPER, id);
    }

    @Override
    public List<TradeMessage> findAll() {
        return queryList("SELECT " + COLUMNS + " FROM " + TABLE + " ORDER BY created_at, id", ROW_MAPPER);
    }

    @Override
    public int insert(TradeMessage message) {
        LocalDateTime createdAt = message.getCreatedAt() == null
                ? LocalDateTime.now() : message.getCreatedAt();
        boolean read = Boolean.TRUE.equals(message.getIsRead());
        long id = executeInsert("INSERT INTO " + TABLE
                        + " (item_id, from_user_id, to_user_id, content, is_read, created_at)"
                        + " VALUES (?, ?, ?, ?, ?, ?)",
                message.getItemId(), message.getFromUserId(), message.getToUserId(),
                message.getContent(), read, formatDateTime(createdAt));
        message.setId((int) id);
        return 1;
    }

    @Override
    public int update(TradeMessage message) {
        return executeUpdate("UPDATE " + TABLE + " SET item_id = ?, from_user_id = ?, to_user_id = ?,"
                        + " content = ?, is_read = ? WHERE id = ?",
                message.getItemId(), message.getFromUserId(), message.getToUserId(),
                message.getContent(), Boolean.TRUE.equals(message.getIsRead()), message.getId());
    }

    @Override
    public int deleteById(Integer id) {
        return executeUpdate("DELETE FROM " + TABLE + " WHERE id = ?", id);
    }

    @Override
    public List<TradeMessage> findConversation(int userId, int otherUserId, int itemId) {
        return queryList("SELECT " + COLUMNS + " FROM " + TABLE
                        + " WHERE item_id = ? AND ((from_user_id = ? AND to_user_id = ?)"
                        + " OR (from_user_id = ? AND to_user_id = ?))"
                        + " ORDER BY created_at, id",
                ROW_MAPPER, itemId, userId, otherUserId, otherUserId, userId);
    }

    @Override
    public int markRead(int toUserId, int itemId) {
        return executeUpdate("UPDATE " + TABLE + " SET is_read = 1"
                + " WHERE to_user_id = ? AND item_id = ? AND is_read = 0", toUserId, itemId);
    }

    @Override
    public int countUnread(int userId) {
        return queryInt("SELECT COUNT(*) FROM " + TABLE + " WHERE to_user_id = ? AND is_read = 0", userId);
    }
}
