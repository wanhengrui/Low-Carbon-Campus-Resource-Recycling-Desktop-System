package edu.campus.recycle.dao.impl;

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
    public List<Review> findByFlowId(int flowId) {
        return queryList("SELECT " + COLUMNS + " FROM " + TABLE
                + " WHERE flow_id = ? ORDER BY created_at ASC, id ASC", ROW_MAPPER, flowId);
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
