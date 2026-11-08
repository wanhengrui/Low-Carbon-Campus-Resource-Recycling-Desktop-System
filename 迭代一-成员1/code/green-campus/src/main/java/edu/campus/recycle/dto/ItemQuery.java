package edu.campus.recycle.dto;

import java.math.BigDecimal;

/**
 * 物品检索条件对象（契约第 4 节），承载 keyword/categoryId/价格区间/交易方式/状态/
 * 发布者/排序/分页共 10 个可选条件，避免超长参数表。
 */
public class ItemQuery {

    /** 关键字，匹配标题、描述与标签 */
    private String keyword;
    /** 分类ID（含二级分类时由 Service 展开） */
    private Integer categoryId;
    /** 价格下限（含） */
    private BigDecimal minPrice;
    /** 价格上限（含） */
    private BigDecimal maxPrice;
    /** 交易方式：SELL/EXCHANGE/FREE */
    private String tradeType;
    /** 物品状态，默认仅检索 ON_SALE */
    private String status;
    /** 发布者ID */
    private Integer ownerId;
    /** 排序方式：LATEST/PRICE_ASC/PRICE_DESC/CREDIT_FIRST（第 3 轮裁决 v1.1 §13-16） */
    private String sortBy;
    /** 页码，从 1 开始 */
    private int pageNo = 1;
    /** 每页条数 */
    private int pageSize = 10;

    public ItemQuery() {
    }

    public int getOffset() {
        return (Math.max(pageNo, 1) - 1) * getLimit();
    }

    public int getLimit() {
        return pageSize <= 0 ? 10 : pageSize;
    }

    /** 排序方式，未指定时按最新排序。 */
    public String getSortByOrDefault() {
        return sortBy == null || sortBy.isBlank() ? "LATEST" : sortBy;
    }

    public String getKeyword() {
        return keyword;
    }

    public void setKeyword(String keyword) {
        this.keyword = keyword;
    }

    public Integer getCategoryId() {
        return categoryId;
    }

    public void setCategoryId(Integer categoryId) {
        this.categoryId = categoryId;
    }

    public BigDecimal getMinPrice() {
        return minPrice;
    }

    public void setMinPrice(BigDecimal minPrice) {
        this.minPrice = minPrice;
    }

    public BigDecimal getMaxPrice() {
        return maxPrice;
    }

    public void setMaxPrice(BigDecimal maxPrice) {
        this.maxPrice = maxPrice;
    }

    public String getTradeType() {
        return tradeType;
    }

    public void setTradeType(String tradeType) {
        this.tradeType = tradeType;
    }

    public String getStatus() {
        return status;
    }

    public void setStatus(String status) {
        this.status = status;
    }

    public Integer getOwnerId() {
        return ownerId;
    }

    public void setOwnerId(Integer ownerId) {
        this.ownerId = ownerId;
    }

    public String getSortBy() {
        return sortBy;
    }

    public void setSortBy(String sortBy) {
        this.sortBy = sortBy;
    }

    public int getPageNo() {
        return pageNo;
    }

    public void setPageNo(int pageNo) {
        this.pageNo = pageNo;
    }

    public int getPageSize() {
        return pageSize;
    }

    public void setPageSize(int pageSize) {
        this.pageSize = pageSize;
    }

    @Override
    public String toString() {
        return "ItemQuery{keyword=" + keyword + ", categoryId=" + categoryId
                + ", minPrice=" + minPrice + ", maxPrice=" + maxPrice
                + ", tradeType=" + tradeType + ", status=" + status
                + ", ownerId=" + ownerId + ", sortBy=" + sortBy
                + ", pageNo=" + pageNo + ", pageSize=" + pageSize + '}';
    }
}
