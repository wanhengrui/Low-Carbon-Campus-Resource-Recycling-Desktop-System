package edu.campus.recycle.entity;

import java.time.LocalDateTime;

/**
 * 收藏实体，与数据库表 {@code favorite} 一一对应（契约第 3.5 节，字段不得增删）。
 *
 * <p>字段名由表字段下划线形式转驼峰，金额使用 {@link java.math.BigDecimal}，
 * 时间使用 {@link java.time.LocalDateTime}，布尔语义字段使用 {@link Boolean}。</p>
 */
public class Favorite {

    /** 收藏ID（主键） */
    private Integer id;

    /** 收藏人（FK→user.id） */
    private Integer userId;

    /** 物品（FK→item.id） */
    private Integer itemId;

    /** 收藏时间 */
    private LocalDateTime createdAt;

    /** 无参构造器，供 DAO 与框架反射使用。 */
    public Favorite() {
    }

    /** 全参构造器。 */
    public Favorite(Integer id, Integer userId, Integer itemId, LocalDateTime createdAt) {
        this.id = id;
        this.userId = userId;
        this.itemId = itemId;
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

    public Integer getItemId() {
        return itemId;
    }

    public void setItemId(Integer itemId) {
        this.itemId = itemId;
    }

    public LocalDateTime getCreatedAt() {
        return createdAt;
    }

    public void setCreatedAt(LocalDateTime createdAt) {
        this.createdAt = createdAt;
    }

    @Override
    public String toString() {
        return "Favorite{" + "id=" + id + ", " + "userId=" + userId + ", " + "itemId=" + itemId + ", " + "createdAt=" + createdAt + '}';
    }
}
