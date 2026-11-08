package edu.campus.recycle.util;

import java.util.HashMap;
import java.util.Map;

/**
 * 缺省碳减排系数策略：按一级分类给定经验系数（单位：kgCO2e/次），
 * 未登记分类使用 {@link #DEFAULT_FACTOR}。
 *
 * <p>系数取值说明（用于统计页展示与课程报告说明）：
 * 数码配件再流通减排最高（3.2），教材书籍最低（0.6），
 * 该值后续可替换为生态环境部门发布的因子表（实现类可替换，调用方不变）。</p>
 */
public class DefaultCarbonFactorStrategy implements CarbonFactorStrategy {

    /** 未登记分类的缺省系数（kgCO2e/次） */
    public static final double DEFAULT_FACTOR = 1.0D;

    private final Map<String, Double> factors = new HashMap<>();

    private final double defaultFactor;

    public DefaultCarbonFactorStrategy() {
        this(DEFAULT_FACTOR);
    }

    public DefaultCarbonFactorStrategy(double defaultFactor) {
        this.defaultFactor = defaultFactor;
        factors.put("教材书籍", 0.6D);
        factors.put("考研考证", 0.6D);
        factors.put("公共课教材", 0.6D);
        factors.put("数码配件", 3.2D);
        factors.put("手机配件", 2.4D);
        factors.put("电脑外设", 3.2D);
        factors.put("文体用品", 1.1D);
        factors.put("球类器材", 1.1D);
        factors.put("生活物资", 1.8D);
        factors.put("宿舍用品", 1.8D);
    }

    @Override
    public double factorOf(String categoryName) {
        if (categoryName == null || categoryName.isBlank()) {
            return defaultFactor;
        }
        Double factor = factors.get(categoryName.trim());
        return factor == null ? defaultFactor : factor;
    }

    @Override
    public String getName() {
        return "默认分类减排系数";
    }
}
