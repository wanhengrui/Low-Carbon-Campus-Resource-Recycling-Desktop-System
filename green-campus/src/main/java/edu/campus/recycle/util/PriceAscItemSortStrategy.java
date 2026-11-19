package edu.campus.recycle.util;

/**
 * 排序策略：价格从低到高。
 */
public class PriceAscItemSortStrategy implements ItemSortStrategy {

    @Override
    public String getCode() {
        return "PRICE_ASC";
    }

    @Override
    public String getDisplayName() {
        return "价格升序";
    }

    @Override
    public String orderByClause() {
        return "i.price ASC, i.id DESC";
    }
}
