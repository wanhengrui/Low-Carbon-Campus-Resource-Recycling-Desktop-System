package edu.campus.recycle.entity;

import java.time.LocalDateTime;

/**
 * 信用分变更流水实体，与数据库表 {@code credit_log} 一一对应（契约第 3.9 节，字段不得增删）。
 *
 * <p>字段名由表字段下划线形式转驼峰，金额使用 {@link java.math.BigDecimal}，
 * 时间使用 {@link java.time.LocalDateTime}，布尔语义字段使用 {@link Boolean}。</p>
 */
public class CreditLog {

    /** 流水ID（主键） */
    private Integer id;

    /** 用户（FK→user.id） */
    private Integer userId;

    /** 关联流转（FK→trade_flow.id，可空） */
    private Integer flowId;

    /** 变化量（+2/-5…） */
    private Integer delta;

    /** 变更后分数快照，0–150 */
    private Integer scoreAfter;

    /** 变更原因 */
    private String reason;

    /** 变更时间 */
    private LocalDateTime createdAt;

    /** 无参构造器，供 DAO 与框架反射使用。 */
    public CreditLog() {
    }

    /** 全参构造器。 */
    public CreditLog(Integer id, Integer userId, Integer flowId, Integer delta, Integer scoreAfter, String reason, LocalDateTime createdAt) {
        this.id = id;
        this.userId = userId;
        this.flowId = flowId;
        this.delta = delta;
        this.scoreAfter = scoreAfter;
        this.reason = reason;
        this.createdAt = createdAt;
    }

    public Integer getId() {
        return id;
    }

    public void setId(Integer id) {
        this.id = id;
    }

    public Integer getUserId() {
        return userId;
    }

    public void setUserId(Integer userId) {
        this.userId = userId;
    }

    public Integer getFlowId() {
        return flowId;
    }

    public void setFlowId(Integer flowId) {
        this.flowId = flowId;
    }

    public Integer getDelta() {
        return delta;
    }

    public void setDelta(Integer delta) {
        this.delta = delta;
    }

    public Integer getScoreAfter() {
        return scoreAfter;
    }

    public void setScoreAfter(Integer scoreAfter) {
        this.scoreAfter = scoreAfter;
    }

    public String getReason() {
        return reason;
    }

    public void setReason(String reason) {
        this.reason = reason;
    }

    public LocalDateTime getCreatedAt() {
        return createdAt;
    }

    public void setCreatedAt(LocalDateTime createdAt) {
        this.createdAt = createdAt;
    }

    @Override
    public String toString() {
        return "CreditLog{" + "id=" + id + ", " + "userId=" + userId + ", " + "flowId=" + flowId + ", " + "delta=" + delta + ", " + "scoreAfter=" + scoreAfter + ", " + "reason=" + reason + ", " + "createdAt=" + createdAt + '}';
    }
}
