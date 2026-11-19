package edu.campus.recycle.util;

/**
 * 物品/流转事件监听器（观察者模式观察者接口）。
 */
@FunctionalInterface
public interface ItemEventListener {

    /**
     * 处理事件。
     *
     * @param event 事件
     */
    void onEvent(ItemEvent event);
}
