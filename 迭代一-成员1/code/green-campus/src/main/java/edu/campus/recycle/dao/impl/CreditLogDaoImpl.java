package edu.campus.recycle.dao.impl;

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
