package edu.campus.recycle.exception;

/**
 * 事务异常：提交或回滚失败、事务嵌套异常时抛出；业务规则拒绝使用 BusinessRuleException。
 */
public class TransactionException extends AppException {

    private static final long serialVersionUID = 1L;

    /** 默认错误码前缀（子类可传入更细粒度的错误码） */
    public static final String DEFAULT_CODE = "TX-001";

    public TransactionException(String userMessage) {
        super(DEFAULT_CODE, userMessage);
    }

    public TransactionException(String userMessage, Throwable cause) {
        super(DEFAULT_CODE, userMessage, cause);
    }

    public TransactionException(String code, String userMessage) {
        super(code, userMessage);
    }

    /**
     * 使用默认错误码构造异常。
     *
     * @param userMessage 用户提示文案
     * @return 异常实例
     */
    public static TransactionException of(String userMessage) {
        return new TransactionException(userMessage);
    }

    /**
     * 使用默认错误码构造异常并保留根因。
     *
     * @param userMessage 用户提示文案
     * @param cause       根因
     * @return 异常实例
     */
    public static TransactionException of(String userMessage, Throwable cause) {
        return new TransactionException(userMessage, cause);
    }

    /**
     * 使用指定错误码构造异常。
     *
     * @param code        错误码
     * @param userMessage 用户提示文案
     * @return 异常实例
     */
    public static TransactionException ofCode(String code, String userMessage) {
        return new TransactionException(code, userMessage);
    }
}
