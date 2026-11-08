package edu.campus.recycle.ui;

/**
 * Swing 界面占位类。
 *
 * <p>迭代一交付中，图形界面（登录、物品列表、发布表单、流转与统计面板）由成员3实现，
 * 本类仅用于占位并声明 ui 包的职责边界：界面层只依赖 controller 与 service 接口，
 * 不得出现任何 SQL 或 JDBC 代码。</p>
 */
public final class SwingUiPlaceholder {

    private SwingUiPlaceholder() {
    }

    /**
     * 界面模块职责说明（供类图与文档引用）。
     *
     * @return 职责说明
     */
    public static String responsibility() {
        return "Swing 界面层：负责视图渲染与用户交互，通过 AppController 调用服务层，不含 SQL/JDBC。";
    }
}
