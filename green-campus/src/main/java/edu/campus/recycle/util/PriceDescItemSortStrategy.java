package edu.campus.recycle.util;

/**
 * 排序策略：价格从高到低。
 */
public class PriceDescItemSortStrategy implements ItemSortStrategy {

    @Override
    public String getCode() {
        return "PRICE_DESC";
    }

    @Override
    public String getDisplayName() {
        return "价格降序";
    }

    @Override
    public String orderByClause() {
        return "i.price DESC, i.id DESC";
    }
}
