package edu.campus.recycle.entity;

import java.math.BigDecimal;
import java.time.LocalDateTime;

/**
 * 流转记录（核心表）实体，与数据库表 {@code trade_flow} 一一对应（契约第 3.7 节，字段不得增删）。
 *
 * <p>字段名由表字段下划线形式转驼峰，金额使用 {@link java.math.BigDecimal}，
 * 时间使用 {@link java.time.LocalDateTime}，布尔语义字段使用 {@link Boolean}。</p>
 */
public class TradeFlow {

    /** 流转ID（主键） */
    private Integer id;

    /** 物品（FK→item.id） */
    private Integer itemId;

    /** 出让方（FK→user.id） */
    private Integer sellerId;

    /** 受让方（FK→user.id） */
    private Integer buyerId;

    /** 流转方式：SELL/EXCHANGE/FREE（冗余自 item，历史快照） */
    private String flowType;

    /** 成交金额 */
    private BigDecimal amount;

    /** 流转状态：APPLYING/AGREED/DONE/CANCELLED */
    private String status;

    /** 申请留言 */
    private String applyRemark;

    /** 取消原因 */
    private String cancelReason;

    /** 发起时间 */
    private LocalDateTime createdAt;

    /** 完成时间 */
    private LocalDateTime finishedAt;

    /** 无参构造器，供 DAO 与框架反射使用。 */
    public TradeFlow() {
    }

    /** 全参构造器。 */
    public TradeFlow(Integer id, Integer itemId, Integer sellerId, Integer buyerId, String flowType, BigDecimal amount, String status, String applyRemark, String cancelReason, LocalDateTime createdAt, LocalDateTime finishedAt) {
        this.id = id;
        this.itemId = itemId;
        this.sellerId = sellerId;
        this.buyerId = buyerId;
        this.flowType = flowType;
        this.amount = amount;
        this.status = status;
        this.applyRemark = applyRemark;
        this.cancelReason = cancelReason;
        this.createdAt = createdAt;
        this.finishedAt = finishedAt;
    }

    public Integer getId() {
        return id;
    }

    public void setId(Integer id) {
        this.id = id;
    }

    public Integer getItemId() {
        return itemId;
    }

    public void setItemId(Integer itemId) {
        this.itemId = itemId;
    }

    public Integer getSellerId() {
        return sellerId;
    }

    public void setSellerId(Integer sellerId) {
        this.sellerId = sellerId;
    }

    public Integer getBuyerId() {
        return buyerId;
    }

    public void setBuyerId(Integer buyerId) {
        this.buyerId = buyerId;
    }

    public String getFlowType() {
        return flowType;
    }

    public void setFlowType(String flowType) {
        this.flowType = flowType;
    }

    public BigDecimal getAmount() {
        return amount;
    }

    public void setAmount(BigDecimal amount) {
        this.amount = amount;
    }

    public String getStatus() {
        return status;
    }

    public void setStatus(String status) {
        this.status = status;
    }

    public String getApplyRemark() {
        return applyRemark;
    }

    public void setApplyRemark(String applyRemark) {
        this.applyRemark = applyRemark;
    }

    public String getCancelReason() {
        return cancelReason;
    }

    public void setCancelReason(String cancelReason) {
        this.cancelReason = cancelReason;
    }

    public LocalDateTime getCreatedAt() {
        return createdAt;
    }

    public void setCreatedAt(LocalDateTime createdAt) {
        this.createdAt = createdAt;
    }

    public LocalDateTime getFinishedAt() {
        return finishedAt;
    }

    public void setFinishedAt(LocalDateTime finishedAt) {
        this.finishedAt = finishedAt;
    }

    @Override
    public String toString() {
        return "TradeFlow{" + "id=" + id + ", " + "itemId=" + itemId + ", " + "sellerId=" + sellerId + ", " + "buyerId=" + buyerId + ", " + "flowType=" + flowType + ", " + "amount=" + amount + ", " + "status=" + status + ", " + "applyRemark=" + applyRemark + ", " + "cancelReason=" + cancelReason + ", " + "createdAt=" + createdAt + ", " + "finishedAt=" + finishedAt + '}';
    }
}
