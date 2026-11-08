package edu.campus.recycle.util;

import java.util.EnumMap;
import java.util.Map;
import java.util.concurrent.atomic.AtomicLong;

/**
 * 统计监听器：在内存中累计领域事件次数，供控制台/统计页快速展示，
 * 避免每次刷新都做 COUNT 聚合查询；持久化统计仍以 {@code trade_flow} 为准。
 */
public class StatisticListener implements ItemEventListener {

    private final Map<ItemEvent.Type, AtomicLong> counters = new EnumMap<>(ItemEvent.Type.class);

    public StatisticListener() {
        for (ItemEvent.Type type : ItemEvent.Type.values()) {
            counters.put(type, new AtomicLong());
        }
    }

    @Override
    public void onEvent(ItemEvent event) {
        AtomicLong counter = counters.get(event.getType());
        if (counter != null) {
            counter.incrementAndGet();
        }
    }

    /**
     * 某类事件累计次数。
     *
     * @param type 事件类型
     * @return 次数
     */
    public long count(ItemEvent.Type type) {
        AtomicLong counter = counters.get(type);
        return counter == null ? 0L : counter.get();
    }

    /**
     * 事件计数快照，形如 {@code ITEM_PUBLISHED=3, FLOW_DONE=1}。
     *
     * @return 快照文本
     */
    public String snapshot() {
        StringBuilder builder = new StringBuilder();
        for (Map.Entry<ItemEvent.Type, AtomicLong> entry : counters.entrySet()) {
            if (entry.getValue().get() > 0) {
                if (builder.length() > 0) {
                    builder.append(", ");
                }
                builder.append(entry.getKey()).append('=').append(entry.getValue().get());
            }
        }
        return builder.length() == 0 ? "(无事件)" : builder.toString();
    }
}
