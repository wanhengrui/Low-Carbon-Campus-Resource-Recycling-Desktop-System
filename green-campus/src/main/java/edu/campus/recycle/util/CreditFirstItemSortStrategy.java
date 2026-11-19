package edu.campus.recycle.util;

/**
 * 排序策略：卖家信用优先（第 3 轮裁决 v1.1 §4-4 / §13-16）。
 *
 * <p>按卖家 {@code user.credit_score} 降序排列，信用分相同时按上架时间倒序，
 * 保证高信用卖家及其最新物品优先展示，降低交易风险。信用分通过关联子查询读取，
 * 不产生额外往返查询。</p>
 */
public class CreditFirstItemSortStrategy implements ItemSortStrategy {

    @Override
    public String getCode() {
        return "CREDIT_FIRST";
    }

    @Override
    public String getDisplayName() {
        return "信用优先";
    }

    @Override
    public String orderByClause() {
        return "(SELECT u.credit_score FROM \"user\" u WHERE u.id = i.owner_id) DESC,"
                + " i.published_at DESC, i.id DESC";
    }
}
