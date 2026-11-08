package edu.campus.recycle.dao.impl;

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

    private static final String TABLE = "\"user\"";

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
