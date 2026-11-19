package edu.campus.recycle.exception;

/**
 * 权限异常：非本人/非管理员执行受限操作时抛出（BR-06、BR-10）。
 */
public class PermissionDeniedException extends AppException {

    private static final long serialVersionUID = 1L;

    /** 默认错误码前缀（子类可传入更细粒度的错误码） */
    public static final String DEFAULT_CODE = "PERM-001";

    public PermissionDeniedException(String userMessage) {
        super(DEFAULT_CODE, userMessage);
    }

    public PermissionDeniedException(String userMessage, Throwable cause) {
        super(DEFAULT_CODE, userMessage, cause);
    }

    public PermissionDeniedException(String code, String userMessage) {
        super(code, userMessage);
    }

    /**
     * 使用默认错误码构造异常。
     *
     * @param userMessage 用户提示文案
     * @return 异常实例
     */
    public static PermissionDeniedException of(String userMessage) {
        return new PermissionDeniedException(userMessage);
    }

    /**
     * 使用默认错误码构造异常并保留根因。
     *
     * @param userMessage 用户提示文案
     * @param cause       根因
     * @return 异常实例
     */
    public static PermissionDeniedException of(String userMessage, Throwable cause) {
        return new PermissionDeniedException(userMessage, cause);
    }

    /**
     * 使用指定错误码构造异常。
     *
     * @param code        错误码
     * @param userMessage 用户提示文案
     * @return 异常实例
     */
    public static PermissionDeniedException ofCode(String code, String userMessage) {
        return new PermissionDeniedException(code, userMessage);
    }
}
