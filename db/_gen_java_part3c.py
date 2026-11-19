# -*- coding: utf-8 -*-
"""D7 生成器 part3c：ItemImage/Favorite/TradeMessage/TradeFlow/Review/CreditLog/OperationLog/SystemConfig 的 DAO 实现。"""
import os

BASE = r'C:\Users\wanhe\Desktop\软件构造\迭代一-成员1\code\green-campus'


def write(rel, content):
    path = os.path.join(BASE, rel)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'w', encoding='utf-8', newline='\n') as f:
        f.write(content)
    print('  + %-82s %5d B' % (rel, len(content.encode('utf-8'))))


def out(cls):
    return os.path.join('src', 'main', 'java', 'edu', 'campus', 'recycle', 'dao', 'impl', cls + '.java')


ITEM_IMAGE = '''package edu.campus.recycle.dao.impl;

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
'''
write(out('ItemImageDaoImpl'), ITEM_IMAGE)

FAVORITE = '''package edu.campus.recycle.dao.impl;

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
'''
write(out('FavoriteDaoImpl'), FAVORITE)

TRADE_MESSAGE = '''package edu.campus.recycle.dao.impl;

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
'''
write(out('TradeMessageDaoImpl'), TRADE_MESSAGE)

TRADE_FLOW = '''package edu.campus.recycle.dao.impl;

import edu.campus.recycle.dao.TradeFlowDao;
import edu.campus.recycle.dto.StatisticsDTO;
import edu.campus.recycle.entity.TradeFlow;
import edu.campus.recycle.util.RowMapper;

import java.math.BigDecimal;
import java.time.LocalDateTime;
import java.util.List;
import java.util.Optional;

/**
 * 流转记录 DAO 实现（核心表）。
 *
 * <p>状态机 APPLYING→AGREED→DONE / CANCELLED，同一物品同时只能有一条进行中流转（BR-05），
 * 由数据库部分唯一索引 {@code uq_flow_item_active} 兜底，应用层先行校验只是为了给出友好提示。</p>
 */
public class TradeFlowDaoImpl extends AbstractJdbcDao<TradeFlow> implements TradeFlowDao {

    private static final String TABLE = "trade_flow";

    private static final String COLUMNS = "id, item_id, seller_id, buyer_id, flow_type, amount, status,"
            + " apply_remark, cancel_reason, created_at, finished_at";

    private static final RowMapper<TradeFlow> ROW_MAPPER = rs -> {
        TradeFlow flow = new TradeFlow();
        flow.setId(rs.getInt("id"));
        flow.setItemId(rs.getInt("item_id"));
        flow.setSellerId(rs.getInt("seller_id"));
        flow.setBuyerId(rs.getInt("buyer_id"));
        flow.setFlowType(rs.getString("flow_type"));
        flow.setAmount(readBigDecimal(rs, "amount"));
        flow.setStatus(rs.getString("status"));
        flow.setApplyRemark(rs.getString("apply_remark"));
        flow.setCancelReason(rs.getString("cancel_reason"));
        flow.setCreatedAt(readDateTime(rs, "created_at"));
        flow.setFinishedAt(readDateTime(rs, "finished_at"));
        return flow;
    };

    @Override
    protected String tableName() {
        return TABLE;
    }

    @Override
    protected RowMapper<TradeFlow> rowMapper() {
        return ROW_MAPPER;
    }

    @Override
    public Optional<TradeFlow> findById(Integer id) {
        return queryOne("SELECT " + COLUMNS + " FROM " + TABLE + " WHERE id = ?", ROW_MAPPER, id);
    }

    @Override
    public Optional<TradeFlow> findById(int id) {
        return findById(Integer.valueOf(id));
    }

    @Override
    public List<TradeFlow> findAll() {
        return queryList("SELECT " + COLUMNS + " FROM " + TABLE + " ORDER BY id", ROW_MAPPER);
    }

    @Override
    public int insert(TradeFlow flow) {
        LocalDateTime createdAt = flow.getCreatedAt() == null ? LocalDateTime.now() : flow.getCreatedAt();
        String status = flow.getStatus() == null ? "APPLYING" : flow.getStatus();
        BigDecimal amount = flow.getAmount() == null ? BigDecimal.ZERO : flow.getAmount();
        long id = executeInsert("INSERT INTO " + TABLE
                        + " (item_id, seller_id, buyer_id, flow_type, amount, status, apply_remark,"
                        + " cancel_reason, created_at, finished_at)"
                        + " VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                flow.getItemId(), flow.getSellerId(), flow.getBuyerId(), flow.getFlowType(),
                amount, status, flow.getApplyRemark(), flow.getCancelReason(),
                formatDateTime(createdAt), formatDateTime(flow.getFinishedAt()));
        flow.setId((int) id);
        return 1;
    }

    @Override
    public int update(TradeFlow flow) {
        return executeUpdate("UPDATE " + TABLE + " SET item_id = ?, seller_id = ?, buyer_id = ?,"
                        + " flow_type = ?, amount = ?, status = ?, apply_remark = ?, cancel_reason = ?,"
                        + " finished_at = ? WHERE id = ?",
                flow.getItemId(), flow.getSellerId(), flow.getBuyerId(), flow.getFlowType(),
                flow.getAmount(), flow.getStatus(), flow.getApplyRemark(), flow.getCancelReason(),
                formatDateTime(flow.getFinishedAt()), flow.getId());
    }

    @Override
    public int deleteById(Integer id) {
        return executeUpdate("DELETE FROM " + TABLE + " WHERE id = ?", id);
    }

    @Override
    public Optional<TradeFlow> findActiveByItemId(int itemId) {
        return queryOne("SELECT " + COLUMNS + " FROM " + TABLE
                        + " WHERE item_id = ? AND status IN ('APPLYING', 'AGREED')"
                        + " ORDER BY id DESC LIMIT 1",
                ROW_MAPPER, itemId);
    }

    @Override
    public int updateStatus(int flowId, String status, String cancelReason, LocalDateTime finishedAt) {
        return executeUpdate("UPDATE " + TABLE + " SET status = ?, cancel_reason = ?, finished_at = ?"
                        + " WHERE id = ?", status, cancelReason,
                formatDateTime(finishedAt), flowId);
    }

    @Override
    public List<TradeFlow> findByUserId(int userId, String status, int pageNo, int pageSize) {
        StringBuilder sql = new StringBuilder("SELECT " + COLUMNS + " FROM " + TABLE
                + " WHERE (seller_id = ? OR buyer_id = ?)");
        java.util.List<Object> params = new java.util.ArrayList<>();
        params.add(userId);
        params.add(userId);
        if (status != null && !status.isBlank()) {
            sql.append(" AND status = ?");
            params.add(status);
        }
        sql.append(" ORDER BY created_at DESC, id DESC LIMIT ? OFFSET ?");
        int size = pageSize <= 0 ? 10 : pageSize;
        int page = pageNo <= 0 ? 1 : pageNo;
        params.add(size);
        params.add((page - 1) * size);
        return queryList(sql.toString(), ROW_MAPPER, params.toArray());
    }

    @Override
    public int countByUserId(int userId, String status) {
        StringBuilder sql = new StringBuilder("SELECT COUNT(*) FROM " + TABLE
                + " WHERE (seller_id = ? OR buyer_id = ?)");
        java.util.List<Object> params = new java.util.ArrayList<>();
        params.add(userId);
        params.add(userId);
        if (status != null && !status.isBlank()) {
            sql.append(" AND status = ?");
            params.add(status);
        }
        return queryInt(sql.toString(), params.toArray());
    }

    @Override
    public List<StatisticsDTO> countByCategoryForPeriod(LocalDateTime from, LocalDateTime to) {
        String sql = "SELECT c.name AS category_name, COUNT(tf.id) AS flow_count,"
                + " IFNULL(SUM(tf.amount), 0) AS total_amount"
                + " FROM category c"
                + " LEFT JOIN item i ON i.category_id = c.id"
                + " LEFT JOIN trade_flow tf ON tf.item_id = i.id AND tf.status = 'DONE'"
                + "   AND tf.finished_at >= ? AND tf.finished_at <= ?"
                + " GROUP BY c.id, c.name ORDER BY flow_count DESC, c.id";
        return queryList(sql, rs -> new StatisticsDTO(
                rs.getString("category_name"),
                rs.getLong("flow_count"),
                readBigDecimal(rs, "total_amount"),
                0.0D),
                formatDateTime(from), formatDateTime(to));
    }
}
'''
write(out('TradeFlowDaoImpl'), TRADE_FLOW)

REVIEW = '''package edu.campus.recycle.dao.impl;

import edu.campus.recycle.dao.ReviewDao;
import edu.campus.recycle.entity.Review;
import edu.campus.recycle.util.RowMapper;

import java.time.LocalDateTime;
import java.util.List;
import java.util.Optional;

/**
 * 评价 DAO 实现。{@code UNIQUE(flow_id, reviewer_id)} 保证同一流转每人只评一次（BR-08），
 * 应用层 {@link #existsByFlowAndReviewer(int, int)} 先行判断以给出友好提示。
 */
public class ReviewDaoImpl extends AbstractJdbcDao<Review> implements ReviewDao {

    private static final String TABLE = "review";

    private static final String COLUMNS = "id, flow_id, reviewer_id, reviewee_id, score, content, created_at";

    private static final RowMapper<Review> ROW_MAPPER = rs -> {
        Review review = new Review();
        review.setId(rs.getInt("id"));
        review.setFlowId(rs.getInt("flow_id"));
        review.setReviewerId(rs.getInt("reviewer_id"));
        review.setRevieweeId(rs.getInt("reviewee_id"));
        review.setScore(rs.getInt("score"));
        review.setContent(rs.getString("content"));
        review.setCreatedAt(readDateTime(rs, "created_at"));
        return review;
    };

    @Override
    protected String tableName() {
        return TABLE;
    }

    @Override
    protected RowMapper<Review> rowMapper() {
        return ROW_MAPPER;
    }

    @Override
    public Optional<Review> findById(Integer id) {
        return queryOne("SELECT " + COLUMNS + " FROM " + TABLE + " WHERE id = ?", ROW_MAPPER, id);
    }

    @Override
    public List<Review> findAll() {
        return queryList("SELECT " + COLUMNS + " FROM " + TABLE + " ORDER BY id", ROW_MAPPER);
    }

    @Override
    public int insert(Review review) {
        LocalDateTime createdAt = review.getCreatedAt() == null
                ? LocalDateTime.now() : review.getCreatedAt();
        long id = executeInsert("INSERT INTO " + TABLE
                        + " (flow_id, reviewer_id, reviewee_id, score, content, created_at)"
                        + " VALUES (?, ?, ?, ?, ?, ?)",
                review.getFlowId(), review.getReviewerId(), review.getRevieweeId(),
                review.getScore(), review.getContent(), formatDateTime(createdAt));
        review.setId((int) id);
        return 1;
    }

    @Override
    public int update(Review review) {
        return executeUpdate("UPDATE " + TABLE + " SET flow_id = ?, reviewer_id = ?, reviewee_id = ?,"
                        + " score = ?, content = ? WHERE id = ?",
                review.getFlowId(), review.getReviewerId(), review.getRevieweeId(),
                review.getScore(), review.getContent(), review.getId());
    }

    @Override
    public int deleteById(Integer id) {
        return executeUpdate("DELETE FROM " + TABLE + " WHERE id = ?", id);
    }

    @Override
    public boolean existsByFlowAndReviewer(int flowId, int reviewerId) {
        return queryInt("SELECT COUNT(*) FROM " + TABLE
                + " WHERE flow_id = ? AND reviewer_id = ?", flowId, reviewerId) > 0;
    }

    @Override
    public List<Review> findByRevieweeId(int revieweeId) {
        return queryList("SELECT " + COLUMNS + " FROM " + TABLE
                + " WHERE reviewee_id = ? ORDER BY created_at DESC, id DESC", ROW_MAPPER, revieweeId);
    }

    @Override
    public double avgScoreByRevieweeId(int revieweeId) {
        return queryDouble("SELECT IFNULL(AVG(score), 0) FROM " + TABLE + " WHERE reviewee_id = ?", revieweeId);
    }
}
'''
write(out('ReviewDaoImpl'), REVIEW)

CREDIT_LOG = '''package edu.campus.recycle.dao.impl;

import edu.campus.recycle.dao.CreditLogDao;
import edu.campus.recycle.entity.CreditLog;
import edu.campus.recycle.util.RowMapper;

import java.time.LocalDateTime;
import java.util.List;
import java.util.Optional;

/**
 * 信用分流水 DAO 实现。流水只追加（BR-04），作为信用分变更的审计快照。
 */
public class CreditLogDaoImpl extends AbstractJdbcDao<CreditLog> implements CreditLogDao {

    private static final String TABLE = "credit_log";

    private static final String COLUMNS = "id, user_id, flow_id, delta, score_after, reason, created_at";

    private static final RowMapper<CreditLog> ROW_MAPPER = rs -> {
        CreditLog log = new CreditLog();
        log.setId(rs.getInt("id"));
        log.setUserId(rs.getInt("user_id"));
        log.setFlowId(readInteger(rs, "flow_id"));
        log.setDelta(rs.getInt("delta"));
        log.setScoreAfter(rs.getInt("score_after"));
        log.setReason(rs.getString("reason"));
        log.setCreatedAt(readDateTime(rs, "created_at"));
        return log;
    };

    @Override
    protected String tableName() {
        return TABLE;
    }

    @Override
    protected RowMapper<CreditLog> rowMapper() {
        return ROW_MAPPER;
    }

    @Override
    public Optional<CreditLog> findById(Integer id) {
        return queryOne("SELECT " + COLUMNS + " FROM " + TABLE + " WHERE id = ?", ROW_MAPPER, id);
    }

    @Override
    public List<CreditLog> findAll() {
        return queryList("SELECT " + COLUMNS + " FROM " + TABLE + " ORDER BY id", ROW_MAPPER);
    }

    @Override
    public int insert(CreditLog log) {
        LocalDateTime createdAt = log.getCreatedAt() == null ? LocalDateTime.now() : log.getCreatedAt();
        long id = executeInsert("INSERT INTO " + TABLE
                        + " (user_id, flow_id, delta, score_after, reason, created_at)"
                        + " VALUES (?, ?, ?, ?, ?, ?)",
                log.getUserId(), log.getFlowId(), log.getDelta(), log.getScoreAfter(),
                log.getReason(), formatDateTime(createdAt));
        log.setId((int) id);
        return 1;
    }

    @Override
    public int update(CreditLog log) {
        return executeUpdate("UPDATE " + TABLE + " SET user_id = ?, flow_id = ?, delta = ?,"
                        + " score_after = ?, reason = ? WHERE id = ?",
                log.getUserId(), log.getFlowId(), log.getDelta(), log.getScoreAfter(),
                log.getReason(), log.getId());
    }

    @Override
    public int deleteById(Integer id) {
        return executeUpdate("DELETE FROM " + TABLE + " WHERE id = ?", id);
    }

    @Override
    public List<CreditLog> findByUserId(int userId, int limit) {
        int size = limit <= 0 ? 20 : limit;
        return queryList("SELECT " + COLUMNS + " FROM " + TABLE
                + " WHERE user_id = ? ORDER BY created_at DESC, id DESC LIMIT ?", ROW_MAPPER, userId, size);
    }
}
'''
write(out('CreditLogDaoImpl'), CREDIT_LOG)

OPERATION_LOG = '''package edu.campus.recycle.dao.impl;

import edu.campus.recycle.dao.OperationLogDao;
import edu.campus.recycle.entity.OperationLog;
import edu.campus.recycle.util.RowMapper;

import java.time.LocalDateTime;
import java.util.List;
import java.util.Optional;

/**
 * 操作日志 DAO 实现。日志仅追加，不提供修改与删除（BR-11）；审计查询按操作人 + 时间排序。
 */
public class OperationLogDaoImpl extends AbstractJdbcDao<OperationLog> implements OperationLogDao {

    private static final String TABLE = "operation_log";

    private static final String COLUMNS = "id, operator_id, operation, target_type, target_id, detail, ip, created_at";

    private static final RowMapper<OperationLog> ROW_MAPPER = rs -> {
        OperationLog log = new OperationLog();
        log.setId(rs.getInt("id"));
        log.setOperatorId(readInteger(rs, "operator_id"));
        log.setOperation(rs.getString("operation"));
        log.setTargetType(rs.getString("target_type"));
        log.setTargetId(readInteger(rs, "target_id"));
        log.setDetail(rs.getString("detail"));
        log.setIp(rs.getString("ip"));
        log.setCreatedAt(readDateTime(rs, "created_at"));
        return log;
    };

    @Override
    protected String tableName() {
        return TABLE;
    }

    @Override
    protected RowMapper<OperationLog> rowMapper() {
        return ROW_MAPPER;
    }

    @Override
    public Optional<OperationLog> findById(Integer id) {
        return queryOne("SELECT " + COLUMNS + " FROM " + TABLE + " WHERE id = ?", ROW_MAPPER, id);
    }

    @Override
    public List<OperationLog> findAll() {
        return queryList("SELECT " + COLUMNS + " FROM " + TABLE + " ORDER BY id", ROW_MAPPER);
    }

    @Override
    public int insert(OperationLog log) {
        LocalDateTime createdAt = log.getCreatedAt() == null ? LocalDateTime.now() : log.getCreatedAt();
        long id = executeInsert("INSERT INTO " + TABLE
                        + " (operator_id, operation, target_type, target_id, detail, ip, created_at)"
                        + " VALUES (?, ?, ?, ?, ?, ?, ?)",
                log.getOperatorId(), log.getOperation(), log.getTargetType(), log.getTargetId(),
                log.getDetail(), log.getIp(), formatDateTime(createdAt));
        log.setId((int) id);
        return 1;
    }

    @Override
    public int update(OperationLog log) {
        throw new UnsupportedOperationException("操作日志只追加，不允许修改（BR-11）");
    }

    @Override
    public int deleteById(Integer id) {
        throw new UnsupportedOperationException("操作日志只追加，不允许删除（BR-11）");
    }

    @Override
    public List<OperationLog> findRecent(int limit) {
        int size = limit <= 0 ? 50 : limit;
        return queryList("SELECT " + COLUMNS + " FROM " + TABLE
                + " ORDER BY created_at DESC, id DESC LIMIT ?", ROW_MAPPER, size);
    }
}
'''
write(out('OperationLogDaoImpl'), OPERATION_LOG)

SYSTEM_CONFIG = '''package edu.campus.recycle.dao.impl;

import edu.campus.recycle.dao.SystemConfigDao;
import edu.campus.recycle.entity.SystemConfig;
import edu.campus.recycle.util.RowMapper;

import java.time.LocalDateTime;
import java.util.List;
import java.util.Optional;

/**
 * 系统配置 DAO 实现。业务参数（信用分阈值、减排系数、锁定策略等）集中存放，
 * 由 {@code ConfigManager} 与各 Service 读取，避免硬编码。
 */
public class SystemConfigDaoImpl extends AbstractJdbcDao<SystemConfig> implements SystemConfigDao {

    private static final String TABLE = "system_config";

    private static final String COLUMNS = "id, config_key, config_value, description, updated_at";

    private static final RowMapper<SystemConfig> ROW_MAPPER = rs -> {
        SystemConfig config = new SystemConfig();
        config.setId(rs.getInt("id"));
        config.setConfigKey(rs.getString("config_key"));
        config.setConfigValue(rs.getString("config_value"));
        config.setDescription(rs.getString("description"));
        config.setUpdatedAt(readDateTime(rs, "updated_at"));
        return config;
    };

    @Override
    protected String tableName() {
        return TABLE;
    }

    @Override
    protected RowMapper<SystemConfig> rowMapper() {
        return ROW_MAPPER;
    }

    @Override
    public Optional<SystemConfig> findById(Integer id) {
        return queryOne("SELECT " + COLUMNS + " FROM " + TABLE + " WHERE id = ?", ROW_MAPPER, id);
    }

    @Override
    public List<SystemConfig> findAll() {
        return queryList("SELECT " + COLUMNS + " FROM " + TABLE + " ORDER BY config_key", ROW_MAPPER);
    }

    @Override
    public int insert(SystemConfig config) {
        LocalDateTime now = config.getUpdatedAt() == null ? LocalDateTime.now() : config.getUpdatedAt();
        long id = executeInsert("INSERT INTO " + TABLE
                        + " (config_key, config_value, description, updated_at) VALUES (?, ?, ?, ?)",
                config.getConfigKey(), config.getConfigValue(), config.getDescription(),
                formatDateTime(now));
        config.setId((int) id);
        return 1;
    }

    @Override
    public int update(SystemConfig config) {
        LocalDateTime now = config.getUpdatedAt() == null ? LocalDateTime.now() : config.getUpdatedAt();
        return executeUpdate("UPDATE " + TABLE + " SET config_key = ?, config_value = ?,"
                        + " description = ?, updated_at = ? WHERE id = ?",
                config.getConfigKey(), config.getConfigValue(), config.getDescription(),
                formatDateTime(now), config.getId());
    }

    @Override
    public int deleteById(Integer id) {
        return executeUpdate("DELETE FROM " + TABLE + " WHERE id = ?", id);
    }

    @Override
    public String getValue(String key) {
        return queryOne("SELECT config_value FROM " + TABLE + " WHERE config_key = ?",
                rs -> rs.getString(1), key).orElse(null);
    }

    @Override
    public int getInt(String key, int defaultValue) {
        String value = getValue(key);
        if (value == null || value.isBlank()) {
            return defaultValue;
        }
        try {
            return Integer.parseInt(value.trim());
        } catch (NumberFormatException e) {
            return defaultValue;
        }
    }

    @Override
    public double getDouble(String key, double defaultValue) {
        String value = getValue(key);
        if (value == null || value.isBlank()) {
            return defaultValue;
        }
        try {
            return Double.parseDouble(value.trim());
        } catch (NumberFormatException e) {
            return defaultValue;
        }
    }

    @Override
    public int upsert(String key, String value, String description) {
        int updated = executeUpdate("UPDATE " + TABLE + " SET config_value = ?, description = ?,"
                + " updated_at = ? WHERE config_key = ?", value, description,
                formatDateTime(LocalDateTime.now()), key);
        if (updated > 0) {
            return updated;
        }
        SystemConfig config = new SystemConfig();
        config.setConfigKey(key);
        config.setConfigValue(value);
        config.setDescription(description);
        return insert(config);
    }
}
'''
write(out('SystemConfigDaoImpl'), SYSTEM_CONFIG)

print('\npart3c 完成（8 个 DAO 实现）。')
