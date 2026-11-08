package edu.campus.recycle.util;

/**
 * 物品检索排序策略（策略模式，契约第 8 节）。
 *
 * <p>{@code ORDER BY} 片段由策略提供，而不是由前端字符串拼接，
 * 因而既满足"排序可插拔"，也避免 SQL 注入（排序字段不可参数化，只能白名单化）。</p>
 */
public interface ItemSortStrategy {

    /**
     * 策略编码，与 {@code ItemQuery.sortBy} 的取值一致。
     *
     * @return 编码
     */
    String getCode();

    /**
     * 展示名称。
     *
     * @return 中文名称
     */
    String getDisplayName();

    /**
     * 返回 ORDER BY 子句片段（不含 {@code ORDER BY} 关键字，仅白名单常量拼接）。
     *
     * @return 例如 {@code "i.price ASC, i.id DESC"}
     */
    String orderByClause();
}
