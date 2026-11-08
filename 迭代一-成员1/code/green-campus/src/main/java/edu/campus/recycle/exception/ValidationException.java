package edu.campus.recycle.exception;

/**
 * 校验类异常：用户输入不符合 BR-01/BR-12 等规则时抛出，携带具体字段与规则说明。
 */
public class ValidationException extends AppException {

    private static final long serialVersionUID = 1L;

    /** 默认错误码前缀（子类可传入更细粒度的错误码） */
    public static final String DEFAULT_CODE = "VAL-001";

    public ValidationException(String userMessage) {
        super(DEFAULT_CODE, userMessage);
    }

    public ValidationException(String userMessage, Throwable cause) {
        super(DEFAULT_CODE, userMessage, cause);
    }

    public ValidationException(String code, String userMessage) {
        super(code, userMessage);
    }

    /**
     * 使用默认错误码构造异常。
     *
     * @param userMessage 用户提示文案
     * @return 异常实例
     */
    public static ValidationException of(String userMessage) {
        return new ValidationException(userMessage);
    }

    /**
     * 使用默认错误码构造异常并保留根因。
     *
     * @param userMessage 用户提示文案
     * @param cause       根因
     * @return 异常实例
     */
    public static ValidationException of(String userMessage, Throwable cause) {
        return new ValidationException(userMessage, cause);
    }

    /**
     * 使用指定错误码构造异常。
     *
     * @param code        错误码
     * @param userMessage 用户提示文案
     * @return 异常实例
     */
    public static ValidationException ofCode(String code, String userMessage) {
        return new ValidationException(code, userMessage);
    }
}
