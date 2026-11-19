package edu.campus.recycle.entity;

/**
 * 交易方式，对应 {@code item.trade_type} / {@code trade_flow.flow_type}。
 *
 * <p>枚举 {@code code()} 与数据库 TEXT 列取值逐字符一致，数据库写入统一使用
 * {@link #getCode()}，读取统一使用 {@link #fromCode(String)} 转换。</p>
 */
public enum TradeType {

    SELL("售卖"),
    EXCHANGE("交换"),
    FREE("赠送");

    private final String label;

    TradeType(String label) {
        this.label = label;
    }

    /** 中文展示名。 */
    public String getLabel() {
        return label;
    }

    /** 数据库存储值（与枚举常量名一致）。 */
    public String getCode() {
        return name();
    }

    /**
     * 按数据库取值解析枚举，无法匹配时抛出 {@link IllegalArgumentException}。
     *
     * @param code 数据库 TEXT 列取值
     * @return 对应枚举常量
     */
    public static TradeType fromCode(String code) {
        if (code == null) {
            throw new IllegalArgumentException("TradeType 取值不能为空");
        }
        for (TradeType value : values()) {
            if (value.name().equalsIgnoreCase(code.trim())) {
                return value;
            }
        }
        throw new IllegalArgumentException("非法的 TradeType 取值: " + code);
    }

    /** 解析失败时返回默认值，供历史脏数据容错使用。 */
    public static TradeType fromCode(String code, TradeType defaultValue) {
        try {
            return fromCode(code);
        } catch (IllegalArgumentException e) {
            return defaultValue;
        }
    }
}
