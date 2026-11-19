package edu.campus.recycle.util;

import edu.campus.recycle.entity.Item;
import edu.campus.recycle.entity.TradeFlow;

import java.time.LocalDateTime;
import java.util.Objects;

/**
 * 物品/流转领域事件（观察者模式被观察对象，契约第 8 节）。
 *
 * <p>事件在业务事务内部发布，监听器与主流程共用同一个 JDBC 连接，
 * 因此"改物品状态 / 记信用 / 写日志 / 统计"可以保持在同一事务内（BR-07）。</p>
 */
public final class ItemEvent {

    /** 事件类型 */
    public enum Type {
        /** 发布物品 */
        ITEM_PUBLISHED,
        /** 下架物品 */
        ITEM_OFF_SHELF,
        /** 审核物品 */
        ITEM_AUDITED,
        /** 发起流转申请 */
        FLOW_APPLIED,
        /** 出让方同意 */
        FLOW_AGREED,
        /** 流转完成 */
        FLOW_DONE,
        /** 取消流转 */
        FLOW_CANCELLED,
        /** 新增评价 */
        REVIEW_CREATED
    }

    private final Type type;

    private final Integer itemId;

    private final Integer flowId;

    private final Integer operatorId;

    private final String detail;

    private final LocalDateTime occurredAt;

    private ItemEvent(Type type, Integer itemId, Integer flowId, Integer operatorId,
                      String detail, LocalDateTime occurredAt) {
        this.type = Objects.requireNonNull(type, "type");
        this.itemId = itemId;
        this.flowId = flowId;
        this.operatorId = operatorId;
        this.detail = detail;
        this.occurredAt = occurredAt == null ? LocalDateTime.now() : occurredAt;
    }

    /**
     * 创建事件。
     *
     * @param type       类型
     * @param itemId     物品ID，可为 null
     * @param flowId     流转ID，可为 null
     * @param operatorId 操作人ID，可为 null（系统）
     * @param detail     详情描述
     * @return 事件
     */
    public static ItemEvent of(Type type, Integer itemId, Integer flowId, Integer operatorId, String detail) {
        return new ItemEvent(type, itemId, flowId, operatorId, detail, LocalDateTime.now());
    }

    /**
     * 便捷工厂：物品事件。
     *
     * @param type       类型
     * @param item       物品，可为 null
     * @param operatorId 操作人
     * @param detail     详情
     * @return 事件
     */
    public static ItemEvent item(Type type, Item item, Integer operatorId, String detail) {
        return new ItemEvent(type, item == null ? null : item.getId(), null, operatorId, detail,
                LocalDateTime.now());
    }

    /**
     * 便捷工厂：流转事件。
     *
     * @param type       类型
     * @param flow       流转
     * @param operatorId 操作人
     * @param detail     详情
     * @return 事件
     */
    public static ItemEvent flow(Type type, TradeFlow flow, Integer operatorId, String detail) {
        return new ItemEvent(type, flow == null ? null : flow.getItemId(),
                flow == null ? null : flow.getId(), operatorId, detail, LocalDateTime.now());
    }

    public Type getType() {
        return type;
    }

    public Integer getItemId() {
        return itemId;
    }

    public Integer getFlowId() {
        return flowId;
    }

    public Integer getOperatorId() {
        return operatorId;
    }

    public String getDetail() {
        return detail;
    }

    public LocalDateTime getOccurredAt() {
        return occurredAt;
    }

    @Override
    public String toString() {
        return "ItemEvent{" + type + ", itemId=" + itemId + ", flowId=" + flowId
                + ", operatorId=" + operatorId + ", detail=" + detail + "}";
    }
}
