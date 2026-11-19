package edu.campus.recycle.util;

/**
 * 碳减排系数策略（策略模式）：不同分类的物品"再使用一次"折算的减排量不同，
 * 由策略集中维护，便于后续接入更精确的碳排放因子表而不改统计服务。
 */
public interface CarbonFactorStrategy {

    /**
     * 按分类名称返回单次完成的减排系数（kgCO2e）。
     *
     * @param categoryName 分类名称，可为 null
     * @return 减排系数，未知分类返回缺省系数
     */
    double factorOf(String categoryName);

    /**
     * 策略名称。
     *
     * @return 名称
     */
    String getName();
}
