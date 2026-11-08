package edu.campus.recycle.entity;

import java.math.BigDecimal;
import java.time.LocalDateTime;

/**
 * 闲置物品实体，与数据库表 {@code item} 一一对应（契约第 3.3 节，字段不得增删）。
 *
 * <p>字段名由表字段下划线形式转驼峰，金额使用 {@link java.math.BigDecimal}，
 * 时间使用 {@link java.time.LocalDateTime}，布尔语义字段使用 {@link Boolean}。</p>
 */
public class Item {

    /** 物品ID（主键） */
    private Integer id;

    /** 发布者（FK→user.id） */
    private Integer ownerId;

    /** 分类（FK→category.id） */
    private Integer categoryId;

    /** 标题，2–50 字 */
    private String title;

    /** 描述，≤500 字 */
    private String description;

    /** 交易方式：SELL/EXCHANGE/FREE */
    private String tradeType;

    /** 期望价格，EXCHANGE/FREE 为 0 */
    private BigDecimal price;

    /** 原价（用于减排估算） */
    private BigDecimal originalPrice;

    /** 成色 1–10 成新 */
    private Integer conditionLevel;

    /** 标签，逗号分隔（反范式存储，见 D5 第 7 章） */
    private String tags;

    /** 物品状态：DRAFT/PENDING/ON_SALE/LOCKED/SOLD/OFF_SHELF/REJECTED */
    private String status;

    /** 浏览数 */
    private Integer viewCount;

    /** 收藏数 */
    private Integer favoriteCount;

    /** 管理员审核/下架原因 */
    private String auditRemark;

    /** 创建时间 */
    private LocalDateTime createdAt;

    /** 更新时间 */
    private LocalDateTime updatedAt;

    /** 上架时间 */
    private LocalDateTime publishedAt;

    /** 无参构造器，供 DAO 与框架反射使用。 */
    public Item() {
    }

    /** 全参构造器。 */
    public Item(Integer id, Integer ownerId, Integer categoryId, String title, String description, String tradeType, BigDecimal price, BigDecimal originalPrice, Integer conditionLevel, String tags, String status, Integer viewCount, Integer favoriteCount, String auditRemark, LocalDateTime createdAt, LocalDateTime updatedAt, LocalDateTime publishedAt) {
        this.id = id;
        this.ownerId = ownerId;
        this.categoryId = categoryId;
        this.title = title;
        this.description = description;
        this.tradeType = tradeType;
        this.price = price;
        this.originalPrice = originalPrice;
        this.conditionLevel = conditionLevel;
        this.tags = tags;
        this.status = status;
        this.viewCount = viewCount;
        this.favoriteCount = favoriteCount;
        this.auditRemark = auditRemark;
        this.createdAt = createdAt;
        this.updatedAt = updatedAt;
        this.publishedAt = publishedAt;
    }

    public Integer getId() {
        return id;
    }

    public void setId(Integer id) {
        this.id = id;
    }

    public Integer getOwnerId() {
        return ownerId;
    }

    public void setOwnerId(Integer ownerId) {
        this.ownerId = ownerId;
    }

    public Integer getCategoryId() {
        return categoryId;
    }

    public void setCategoryId(Integer categoryId) {
        this.categoryId = categoryId;
    }

    public String getTitle() {
        return title;
    }

    public void setTitle(String title) {
        this.title = title;
    }

    public String getDescription() {
        return description;
    }

    public void setDescription(String description) {
        this.description = description;
    }

    public String getTradeType() {
        return tradeType;
    }

    public void setTradeType(String tradeType) {
        this.tradeType = tradeType;
    }

    public BigDecimal getPrice() {
        return price;
    }

    public void setPrice(BigDecimal price) {
        this.price = price;
    }

    public BigDecimal getOriginalPrice() {
        return originalPrice;
    }

    public void setOriginalPrice(BigDecimal originalPrice) {
        this.originalPrice = originalPrice;
    }

    public Integer getConditionLevel() {
        return conditionLevel;
    }

    public void setConditionLevel(Integer conditionLevel) {
        this.conditionLevel = conditionLevel;
    }

    public String getTags() {
        return tags;
    }

    public void setTags(String tags) {
        this.tags = tags;
    }

    public String getStatus() {
        return status;
    }

    public void setStatus(String status) {
        this.status = status;
    }

    public Integer getViewCount() {
        return viewCount;
    }

    public void setViewCount(Integer viewCount) {
        this.viewCount = viewCount;
    }

    public Integer getFavoriteCount() {
        return favoriteCount;
    }

    public void setFavoriteCount(Integer favoriteCount) {
        this.favoriteCount = favoriteCount;
    }

    public String getAuditRemark() {
        return auditRemark;
    }

    public void setAuditRemark(String auditRemark) {
        this.auditRemark = auditRemark;
    }

    public LocalDateTime getCreatedAt() {
        return createdAt;
    }

    public void setCreatedAt(LocalDateTime createdAt) {
        this.createdAt = createdAt;
    }

    public LocalDateTime getUpdatedAt() {
        return updatedAt;
    }

    public void setUpdatedAt(LocalDateTime updatedAt) {
        this.updatedAt = updatedAt;
    }

    public LocalDateTime getPublishedAt() {
        return publishedAt;
    }

    public void setPublishedAt(LocalDateTime publishedAt) {
        this.publishedAt = publishedAt;
    }

    @Override
    public String toString() {
        return "Item{" + "id=" + id + ", " + "ownerId=" + ownerId + ", " + "categoryId=" + categoryId + ", " + "title=" + title + ", " + "description=" + description + ", " + "tradeType=" + tradeType + ", " + "price=" + price + ", " + "originalPrice=" + originalPrice + ", " + "conditionLevel=" + conditionLevel + ", " + "tags=" + tags + ", " + "status=" + status + ", " + "viewCount=" + viewCount + ", " + "favoriteCount=" + favoriteCount + ", " + "auditRemark=" + auditRemark + ", " + "createdAt=" + createdAt + ", " + "updatedAt=" + updatedAt + ", " + "publishedAt=" + publishedAt + '}';
    }
}
