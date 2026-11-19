package edu.campus.recycle.controller;

import edu.campus.recycle.exception.AppException;

/**
 * 控制器层公用小工具（包内可见，不对外暴露 API）。
 *
 * <p>控制器是 UI 与 Service 之间的薄壳：只做参数校验、调用 Service、把业务异常
 * 转成可直接展示给用户的中文文案，<b>不访问 DAO、不拼接 SQL</b>（第 3 轮裁决 v1.1 §13-15）。</p>
 */
final class ControllerSupport {

    private ControllerSupport() {
    }

    /**
     * 把业务异常转成用户可读文案，格式为 {@code [错误码] 用户提示}。
     *
     * @param e 业务异常
     * @return 用户文案
     */
    static String text(AppException e) {
        return "[" + e.getCode() + "] " + e.getUserMessage();
    }

    /**
     * 断言参数条件，失败时抛出参数异常（属于调用方编程错误，不是业务异常）。
     *
     * @param condition 条件
     * @param message   说明
     */
    static void require(boolean condition, String message) {
        if (!condition) {
            throw new IllegalArgumentException(message);
        }
    }

    /**
     * 非空判断。
     *
     * @param value 字符串
     * @return 非 null 且去空格后非空返回 true
     */
    static boolean hasText(String value) {
        return value != null && !value.trim().isEmpty();
    }
}
