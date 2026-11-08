package edu.campus.recycle.util;

import java.util.List;
import java.util.concurrent.CopyOnWriteArrayList;
import java.util.logging.Level;
import java.util.logging.Logger;

/**
 * 事件总线（观察者模式主题/被观察者，单例）。
 *
 * <p>流转完成的副作用（信用分、操作日志、统计）通过监听器解耦，
 * 主流程只发布事件。监听器抛出异常时向上传播，使外层事务整体回滚，
 * 保证 BR-07"完成 + 信用 + 日志同事务"。</p>
 */
public final class ItemEventBus {

    private static final Logger LOG = Logger.getLogger(ItemEventBus.class.getName());

    private static final ItemEventBus INSTANCE = new ItemEventBus();

    private final List<ItemEventListener> listeners = new CopyOnWriteArrayList<>();

    private ItemEventBus() {
        DaoFactory factory = DaoFactory.getInstance();
        register(new OperationLogListener(factory.getOperationLogDao()));
        register(new CreditChangeListener(factory.getUserDao(), factory.getCreditLogDao(),
                factory.getTradeFlowDao()));
        register(new StatisticListener());
    }

    /**
     * 全局单例。
     *
     * @return 事件总线
     */
    public static ItemEventBus getInstance() {
        return INSTANCE;
    }

    /**
     * 注册监听器。
     *
     * @param listener 监听器
     */
    public void register(ItemEventListener listener) {
        if (listener != null) {
            listeners.add(listener);
        }
    }

    /**
     * 注销监听器。
     *
     * @param listener 监听器
     * @return 是否注销成功
     */
    public boolean unregister(ItemEventListener listener) {
        return listeners.remove(listener);
    }

    /**
     * 当前监听器快照。
     *
     * @return 监听器列表
     */
    public List<ItemEventListener> getListeners() {
        return List.copyOf(listeners);
    }

    /**
     * 发布事件：依次同步通知所有监听器。
     *
     * @param event 事件
     */
    public void publish(ItemEvent event) {
        if (event == null) {
            return;
        }
        for (ItemEventListener listener : listeners) {
            try {
                listener.onEvent(event);
            } catch (RuntimeException e) {
                LOG.log(Level.SEVERE, "事件监听器执行失败：" + listener.getClass().getSimpleName()
                        + "，事件=" + event, e);
                throw e;
            }
        }
    }
}
