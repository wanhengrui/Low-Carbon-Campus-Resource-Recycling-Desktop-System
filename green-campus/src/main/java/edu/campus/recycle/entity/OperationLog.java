package edu.campus.recycle.entity;

import java.time.LocalDateTime;

/**
 * 关键操作日志实体，与数据库表 {@code operation_log} 一一对应（契约第 3.10 节，字段不得增删）。
 *
 * <p>字段名由表字段下划线形式转驼峰，金额使用 {@link java.math.BigDecimal}，
 * 时间使用 {@link java.time.LocalDateTime}，布尔语义字段使用 {@link Boolean}。</p>
 */
public class OperationLog {

    /** 日志ID（主键） */
    private Integer id;

    /** 操作人（FK→user.id，NULL=系统） */
    private Integer operatorId;

    /** 操作类型：LOGIN/PUBLISH_ITEM/CONFIRM_FLOW/OFF_SHELF… */
    private String operation;

    /** 对象类型：ITEM/USER/FLOW/CATEGORY */
    private String targetType;

    /** 对象ID */
    private Integer targetId;

    /** 详情（JSON 或文本） */
    private String detail;

    /** 来源（桌面端记录 hostname） */
    private String ip;

    /** 操作时间 */
    private LocalDateTime createdAt;

    /** 无参构造器，供 DAO 与框架反射使用。 */
    public OperationLog() {
    }

    /** 全参构造器。 */
    public OperationLog(Integer id, Integer operatorId, String operation, String targetType, Integer targetId, String detail, String ip, LocalDateTime createdAt) {
        this.id = id;
        this.operatorId = operatorId;
        this.operation = operation;
        this.targetType = targetType;
        this.targetId = targetId;
        this.detail = detail;
        this.ip = ip;
        this.createdAt = createdAt;
    }

    public Integer getId() {
        return id;
    }

    public void setId(Integer id) {
        this.id = id;
    }

    public Integer getOperatorId() {
        return operatorId;
    }

    public void setOperatorId(Integer operatorId) {
        this.operatorId = operatorId;
    }

    public String getOperation() {
        return operation;
    }

    public void setOperation(String operation) {
        this.operation = operation;
    }

    public String getTargetType() {
        return targetType;
    }

    public void setTargetType(String targetType) {
        this.targetType = targetType;
    }

    public Integer getTargetId() {
        return targetId;
    }

    public void setTargetId(Integer targetId) {
        this.targetId = targetId;
    }

    public String getDetail() {
        return detail;
    }

    public void setDetail(String detail) {
        this.detail = detail;
    }

    public String getIp() {
        return ip;
    }

    public void setIp(String ip) {
        this.ip = ip;
    }

    public LocalDateTime getCreatedAt() {
        return createdAt;
    }

    public void setCreatedAt(LocalDateTime createdAt) {
        this.createdAt = createdAt;
    }

    @Override
    public String toString() {
        return "OperationLog{" + "id=" + id + ", " + "operatorId=" + operatorId + ", " + "operation=" + operation + ", " + "targetType=" + targetType + ", " + "targetId=" + targetId + ", " + "detail=" + detail + ", " + "ip=" + ip + ", " + "createdAt=" + createdAt + '}';
    }
}
