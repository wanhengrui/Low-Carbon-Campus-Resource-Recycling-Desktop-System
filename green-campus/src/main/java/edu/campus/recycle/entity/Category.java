package edu.campus.recycle.entity;

import java.time.LocalDateTime;

/**
 * 分类实体，与数据库表 {@code category} 一一对应（契约第 3.2 节，字段不得增删）。
 *
 * <p>字段名由表字段下划线形式转驼峰，金额使用 {@link java.math.BigDecimal}，
 * 时间使用 {@link java.time.LocalDateTime}，布尔语义字段使用 {@link Boolean}。</p>
 */
public class Category {

    /** 分类ID（主键） */
    private Integer id;

    /** 分类名 */
    private String name;

    /** 父分类ID，NULL 表示一级分类（FK→category.id） */
    private Integer parentId;

    /** 排序值，升序展示 */
    private Integer sortOrder;

    /** 是否启用（下架分类不可选） */
    private Boolean enabled;

    /** 创建时间 */
    private LocalDateTime createdAt;

    /** 无参构造器，供 DAO 与框架反射使用。 */
    public Category() {
    }

    /** 全参构造器。 */
    public Category(Integer id, String name, Integer parentId, Integer sortOrder, Boolean enabled, LocalDateTime createdAt) {
        this.id = id;
        this.name = name;
        this.parentId = parentId;
        this.sortOrder = sortOrder;
        this.enabled = enabled;
        this.createdAt = createdAt;
    }

    public Integer getId() {
        return id;
    }

    public void setId(Integer id) {
        this.id = id;
    }

    public String getName() {
        return name;
    }

    public void setName(String name) {
        this.name = name;
    }

    public Integer getParentId() {
        return parentId;
    }

    public void setParentId(Integer parentId) {
        this.parentId = parentId;
    }

    public Integer getSortOrder() {
        return sortOrder;
    }

    public void setSortOrder(Integer sortOrder) {
        this.sortOrder = sortOrder;
    }

    public Boolean getEnabled() {
        return enabled;
    }

    public void setEnabled(Boolean enabled) {
        this.enabled = enabled;
    }

    public LocalDateTime getCreatedAt() {
        return createdAt;
    }

    public void setCreatedAt(LocalDateTime createdAt) {
        this.createdAt = createdAt;
    }

    @Override
    public String toString() {
        return "Category{" + "id=" + id + ", " + "name=" + name + ", " + "parentId=" + parentId + ", " + "sortOrder=" + sortOrder + ", " + "enabled=" + enabled + ", " + "createdAt=" + createdAt + '}';
    }
}
