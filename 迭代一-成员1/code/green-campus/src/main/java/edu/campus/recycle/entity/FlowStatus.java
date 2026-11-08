package edu.campus.recycle.entity;

/**
 * 流转状态，对应 {@code trade_flow.status} 的 CHECK 取值。
 *
 * <p>枚举 {@code code()} 与数据库 TEXT 列取值逐字符一致，数据库写入统一使用
 * {@link #getCode()}，读取统一使用 {@link #fromCode(String)} 转换。</p>
 */
public enum FlowStatus {

    APPLYING("申请中"),
    AGREED("已同意"),
    DONE("已完成"),
    CANCELLED("已取消");

    private final String label;

    FlowStatus(String label) {
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
    public static FlowStatus fromCode(String code) {
        if (code == null) {
            throw new IllegalArgumentException("FlowStatus 取值不能为空");
        }
        for (FlowStatus value : values()) {
            if (value.name().equalsIgnoreCase(code.trim())) {
                return value;
            }
        }
        throw new IllegalArgumentException("非法的 FlowStatus 取值: " + code);
    }

    /** 解析失败时返回默认值，供历史脏数据容错使用。 */
    public static FlowStatus fromCode(String code, FlowStatus defaultValue) {
        try {
            return fromCode(code);
        } catch (IllegalArgumentException e) {
            return defaultValue;
        }
    }
}
