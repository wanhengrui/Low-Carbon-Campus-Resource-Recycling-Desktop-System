package edu.campus.recycle.util;

/**
 * 排序策略：最新发布优先（默认策略）。
 */
public class LatestItemSortStrategy implements ItemSortStrategy {

    @Override
    public String getCode() {
        return "LATEST";
    }

    @Override
    public String getDisplayName() {
        return "最新发布";
    }

    @Override
    public String orderByClause() {
        return "i.created_at DESC, i.id DESC";
    }
}
