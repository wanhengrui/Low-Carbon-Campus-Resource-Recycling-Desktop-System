package edu.campus.recycle.entity;

import java.time.LocalDateTime;

/**
 * 物品图片实体，与数据库表 {@code item_image} 一一对应（契约第 3.4 节，字段不得增删）。
 *
 * <p>字段名由表字段下划线形式转驼峰，金额使用 {@link java.math.BigDecimal}，
 * 时间使用 {@link java.time.LocalDateTime}，布尔语义字段使用 {@link Boolean}。</p>
 */
public class ItemImage {

    /** 图片ID（主键） */
    private Integer id;

    /** 所属物品（FK→item.id） */
    private Integer itemId;

    /** 相对路径 data/images/{itemId}/{uuid}.jpg */
    private String filePath;

    /** 排序，首图 sort_order=0 */
    private Integer sortOrder;

    /** 上传时间 */
    private LocalDateTime createdAt;

    /** 无参构造器，供 DAO 与框架反射使用。 */
    public ItemImage() {
    }

    /** 全参构造器。 */
    public ItemImage(Integer id, Integer itemId, String filePath, Integer sortOrder, LocalDateTime createdAt) {
        this.id = id;
        this.itemId = itemId;
        this.filePath = filePath;
        this.sortOrder = sortOrder;
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

    public String getFilePath() {
        return filePath;
    }

    public void setFilePath(String filePath) {
        this.filePath = filePath;
    }

    public Integer getSortOrder() {
        return sortOrder;
    }

    public void setSortOrder(Integer sortOrder) {
        this.sortOrder = sortOrder;
    }

    public LocalDateTime getCreatedAt() {
        return createdAt;
    }

    public void setCreatedAt(LocalDateTime createdAt) {
        this.createdAt = createdAt;
    }

    @Override
    public String toString() {
        return "ItemImage{" + "id=" + id + ", " + "itemId=" + itemId + ", " + "filePath=" + filePath + ", " + "sortOrder=" + sortOrder + ", " + "createdAt=" + createdAt + '}';
    }
}
