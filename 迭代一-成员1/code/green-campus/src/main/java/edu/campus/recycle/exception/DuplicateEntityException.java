package edu.campus.recycle.exception;

/**
 * 唯一性冲突异常：用户名、学号、收藏、评价、配置键等唯一约束冲突时抛出。
 */
public class DuplicateEntityException extends AppException {

    private static final long serialVersionUID = 1L;

    /** 默认错误码前缀（子类可传入更细粒度的错误码） */
    public static final String DEFAULT_CODE = "DUP-001";

    public DuplicateEntityException(String userMessage) {
        super(DEFAULT_CODE, userMessage);
    }

    public DuplicateEntityException(String userMessage, Throwable cause) {
        super(DEFAULT_CODE, userMessage, cause);
    }

    public DuplicateEntityException(String code, String userMessage) {
        super(code, userMessage);
    }

    /**
     * 使用默认错误码构造异常。
     *
     * @param userMessage 用户提示文案
     * @return 异常实例
     */
    public static DuplicateEntityException of(String userMessage) {
        return new DuplicateEntityException(userMessage);
    }

    /**
     * 使用默认错误码构造异常并保留根因。
     *
     * @param userMessage 用户提示文案
     * @param cause       根因
     * @return 异常实例
     */
    public static DuplicateEntityException of(String userMessage, Throwable cause) {
        return new DuplicateEntityException(userMessage, cause);
    }

    /**
     * 使用指定错误码构造异常。
     *
     * @param code        错误码
     * @param userMessage 用户提示文案
     * @return 异常实例
     */
    public static DuplicateEntityException ofCode(String code, String userMessage) {
        return new DuplicateEntityException(code, userMessage);
    }
}
