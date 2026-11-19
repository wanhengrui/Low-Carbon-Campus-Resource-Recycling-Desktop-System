package edu.campus.recycle.exception;

/**
 * 账号锁定异常：连续登录失败达到阈值（BR-03）时抛出，携带剩余锁定时间。
 */
public class AccountLockedException extends AppException {

    private static final long serialVersionUID = 1L;

    /** 默认错误码前缀（子类可传入更细粒度的错误码） */
    public static final String DEFAULT_CODE = "LOCK-001";

    public AccountLockedException(String userMessage) {
        super(DEFAULT_CODE, userMessage);
    }

    public AccountLockedException(String userMessage, Throwable cause) {
        super(DEFAULT_CODE, userMessage, cause);
    }

    public AccountLockedException(String code, String userMessage) {
        super(code, userMessage);
    }

    /**
     * 使用默认错误码构造异常。
     *
     * @param userMessage 用户提示文案
     * @return 异常实例
     */
    public static AccountLockedException of(String userMessage) {
        return new AccountLockedException(userMessage);
    }

    /**
     * 使用默认错误码构造异常并保留根因。
     *
     * @param userMessage 用户提示文案
     * @param cause       根因
     * @return 异常实例
     */
    public static AccountLockedException of(String userMessage, Throwable cause) {
        return new AccountLockedException(userMessage, cause);
    }

    /**
     * 使用指定错误码构造异常。
     *
     * @param code        错误码
     * @param userMessage 用户提示文案
     * @return 异常实例
     */
    public static AccountLockedException ofCode(String code, String userMessage) {
        return new AccountLockedException(code, userMessage);
    }
}
