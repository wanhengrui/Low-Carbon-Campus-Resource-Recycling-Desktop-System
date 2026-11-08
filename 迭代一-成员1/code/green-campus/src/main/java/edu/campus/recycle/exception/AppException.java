package edu.campus.recycle.exception;

/**
 * 业务异常基类（契约第 7 节）。
 *
 * <p>所有可预期异常均继承本类，携带机器可读的 {@code code} 与面向用户的
 * {@code userMessage}；UI 层只捕获本类并按 {@code code} 映射提示文案，
 * 未捕获异常由全局处理器写 {@code operation_log} 与日志文件。</p>
 */
public class AppException extends RuntimeException {

    private static final long serialVersionUID = 1L;

    /** 错误码，形如 VAL-001 / BR-04 / DB-001 */
    private final String code;

    /** 面向用户的提示文案（不含堆栈与内部细节） */
    private final String userMessage;

    public AppException(String code, String userMessage) {
        super(userMessage);
        this.code = code;
        this.userMessage = userMessage;
    }

    public AppException(String code, String userMessage, Throwable cause) {
        super(userMessage, cause);
        this.code = code;
        this.userMessage = userMessage;
    }

    /**
     * 统一工厂方法（契约第 7 节）。
     *
     * @param code        错误码
     * @param userMessage 用户提示文案
     * @param cause       根因
     * @return 业务异常实例
     */
    public static AppException of(String code, String userMessage, Throwable cause) {
        return new AppException(code, userMessage, cause);
    }

    public String getCode() {
        return code;
    }

    public String getUserMessage() {
        return userMessage;
    }
}
