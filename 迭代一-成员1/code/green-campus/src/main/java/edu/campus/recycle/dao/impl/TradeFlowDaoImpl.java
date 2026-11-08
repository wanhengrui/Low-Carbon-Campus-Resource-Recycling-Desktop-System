package edu.campus.recycle.dao.impl;

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
