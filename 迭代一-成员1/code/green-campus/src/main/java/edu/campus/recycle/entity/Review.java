package edu.campus.recycle.entity;

import java.time.LocalDateTime;

/**
 * 评价实体，与数据库表 {@code review} 一一对应（契约第 3.8 节，字段不得增删）。
 *
 * <p>字段名由表字段下划线形式转驼峰，金额使用 {@link java.math.BigDecimal}，
 * 时间使用 {@link java.time.LocalDateTime}，布尔语义字段使用 {@link Boolean}。</p>
 */
public class Review {

    /** 评价ID（主键） */
    private Integer id;

    /** 关联流转（FK→trade_flow.id） */
    private Integer flowId;

    /** 评价人（FK→user.id） */
    private Integer reviewerId;

    /** 被评价人（FK→user.id） */
    private Integer revieweeId;

    /** 评分 1–5 星 */
    private Integer score;

    /** 评价内容，≤200 字 */
    private String content;

    /** 评价时间 */
    private LocalDateTime createdAt;

    /** 无参构造器，供 DAO 与框架反射使用。 */
    public Review() {
    }

    /** 全参构造器。 */
    public Review(Integer id, Integer flowId, Integer reviewerId, Integer revieweeId, Integer score, String content, LocalDateTime createdAt) {
        this.id = id;
        this.flowId = flowId;
        this.reviewerId = reviewerId;
        this.revieweeId = revieweeId;
        this.score = score;
        this.content = content;
        this.createdAt = createdAt;
    }

    public Integer getId() {
        return id;
    }

    public void setId(Integer id) {
        this.id = id;
    }

    public Integer getFlowId() {
        return flowId;
    }

    public void setFlowId(Integer flowId) {
        this.flowId = flowId;
    }

    public Integer getReviewerId() {
        return reviewerId;
    }

    public void setReviewerId(Integer reviewerId) {
        this.reviewerId = reviewerId;
    }

    public Integer getRevieweeId() {
        return revieweeId;
    }

    public void setRevieweeId(Integer revieweeId) {
        this.revieweeId = revieweeId;
    }

    public Integer getScore() {
        return score;
    }

    public void setScore(Integer score) {
        this.score = score;
    }

    public String getContent() {
        return content;
    }

    public void setContent(String content) {
        this.content = content;
    }

    public LocalDateTime getCreatedAt() {
        return createdAt;
    }

    public void setCreatedAt(LocalDateTime createdAt) {
        this.createdAt = createdAt;
    }

    @Override
    public String toString() {
        return "Review{" + "id=" + id + ", " + "flowId=" + flowId + ", " + "reviewerId=" + reviewerId + ", " + "revieweeId=" + revieweeId + ", " + "score=" + score + ", " + "content=" + content + ", " + "createdAt=" + createdAt + '}';
    }
}
