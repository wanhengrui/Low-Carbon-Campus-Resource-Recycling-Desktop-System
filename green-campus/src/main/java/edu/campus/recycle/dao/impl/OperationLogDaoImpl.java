package edu.campus.recycle.dao.impl;

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
