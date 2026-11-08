package edu.campus.recycle.dto;

import java.math.BigDecimal;

/**
 * 分类统计结果（契约第 4 节）：完成流转笔数、成交总额与碳减排量。
 */
public class StatisticsDTO {

    /** 分类名 */
    private String categoryName;
    /** 已完成流转笔数 */
    private long flowCount;
    /** 成交总额（元） */
    private BigDecimal totalAmount = BigDecimal.ZERO;
    /** 碳减排量（kgCO₂e） */
    private double carbonReduction;

    public StatisticsDTO() {
    }

    public StatisticsDTO(String categoryName, long flowCount, BigDecimal totalAmount, double carbonReduction) {
        this.categoryName = categoryName;
        this.flowCount = flowCount;
        this.totalAmount = totalAmount == null ? BigDecimal.ZERO : totalAmount;
        this.carbonReduction = carbonReduction;
    }

    public String getCategoryName() {
        return categoryName;
    }

    public void setCategoryName(String categoryName) {
        this.categoryName = categoryName;
    }

    public long getFlowCount() {
        return flowCount;
    }

    public void setFlowCount(long flowCount) {
        this.flowCount = flowCount;
    }

    public BigDecimal getTotalAmount() {
        return totalAmount;
    }

    public void setTotalAmount(BigDecimal totalAmount) {
        this.totalAmount = totalAmount;
    }

    public double getCarbonReduction() {
        return carbonReduction;
    }

    public void setCarbonReduction(double carbonReduction) {
        this.carbonReduction = carbonReduction;
    }

    @Override
    public String toString() {
        return "StatisticsDTO{categoryName=" + categoryName + ", flowCount=" + flowCount
                + ", totalAmount=" + totalAmount + ", carbonReduction=" + carbonReduction + '}';
    }
}
