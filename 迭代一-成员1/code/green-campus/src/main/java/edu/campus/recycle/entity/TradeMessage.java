package edu.campus.recycle.entity;

import java.time.LocalDateTime;

/**
 * 流转沟通消息实体，与数据库表 {@code trade_message} 一一对应（契约第 3.6 节，字段不得增删）。
 *
 * <p>字段名由表字段下划线形式转驼峰，金额使用 {@link java.math.BigDecimal}，
 * 时间使用 {@link java.time.LocalDateTime}，布尔语义字段使用 {@link Boolean}。</p>
 */
public class TradeMessage {

    /** 消息ID（主键） */
    private Integer id;

    /** 关联物品（FK→item.id） */
    private Integer itemId;

    /** 发送者（FK→user.id） */
    private Integer fromUserId;

    /** 接收者（FK→user.id） */
    private Integer toUserId;

    /** 内容，≤300 字 */
    private String content;

    /** 是否已读 */
    private Boolean isRead;

    /** 发送时间 */
    private LocalDateTime createdAt;

    /** 无参构造器，供 DAO 与框架反射使用。 */
    public TradeMessage() {
    }

    /** 全参构造器。 */
    public TradeMessage(Integer id, Integer itemId, Integer fromUserId, Integer toUserId, String content, Boolean isRead, LocalDateTime createdAt) {
        this.id = id;
        this.itemId = itemId;
        this.fromUserId = fromUserId;
        this.toUserId = toUserId;
        this.content = content;
        this.isRead = isRead;
        this.createdAt = createdAt;
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

    public Integer getFromUserId() {
        return fromUserId;
    }

    public void setFromUserId(Integer fromUserId) {
        this.fromUserId = fromUserId;
    }

    public Integer getToUserId() {
        return toUserId;
    }

    public void setToUserId(Integer toUserId) {
        this.toUserId = toUserId;
    }

    public String getContent() {
        return content;
    }

    public void setContent(String content) {
        this.content = content;
    }

    public Boolean getIsRead() {
        return isRead;
    }

    public void setIsRead(Boolean isRead) {
        this.isRead = isRead;
    }

    public LocalDateTime getCreatedAt() {
        return createdAt;
    }

    public void setCreatedAt(LocalDateTime createdAt) {
        this.createdAt = createdAt;
    }

    @Override
    public String toString() {
        return "TradeMessage{" + "id=" + id + ", " + "itemId=" + itemId + ", " + "fromUserId=" + fromUserId + ", " + "toUserId=" + toUserId + ", " + "content=" + content + ", " + "isRead=" + isRead + ", " + "createdAt=" + createdAt + '}';
    }
}
