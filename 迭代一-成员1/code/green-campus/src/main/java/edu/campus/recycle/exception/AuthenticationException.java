package edu.campus.recycle.exception;

/**
 * 认证异常：用户名或口令错误、旧口令校验失败时抛出；提示文案不得暴露口令信息（BR-02）。
 */
public class AuthenticationException extends AppException {

    private static final long serialVersionUID = 1L;

    /** 默认错误码前缀（子类可传入更细粒度的错误码） */
    public static final String DEFAULT_CODE = "AUTH-001";

    public AuthenticationException(String userMessage) {
        super(DEFAULT_CODE, userMessage);
    }

    public AuthenticationException(String userMessage, Throwable cause) {
        super(DEFAULT_CODE, userMessage, cause);
    }

    public AuthenticationException(String code, String userMessage) {
        super(code, userMessage);
    }

    /**
     * 使用默认错误码构造异常。
     *
     * @param userMessage 用户提示文案
     * @return 异常实例
     */
    public static AuthenticationException of(String userMessage) {
        return new AuthenticationException(userMessage);
    }

    /**
     * 使用默认错误码构造异常并保留根因。
     *
     * @param userMessage 用户提示文案
     * @param cause       根因
     * @return 异常实例
     */
    public static AuthenticationException of(String userMessage, Throwable cause) {
        return new AuthenticationException(userMessage, cause);
    }

    /**
     * 使用指定错误码构造异常。
     *
     * @param code        错误码
     * @param userMessage 用户提示文案
     * @return 异常实例
     */
    public static AuthenticationException ofCode(String code, String userMessage) {
        return new AuthenticationException(code, userMessage);
    }
}
