package edu.campus.recycle.exception;

/**
 * 实体不存在异常：按主键查询无结果（或已被删除）时抛出。
 */
public class EntityNotFoundException extends AppException {

    private static final long serialVersionUID = 1L;

    /** 默认错误码前缀（子类可传入更细粒度的错误码） */
    public static final String DEFAULT_CODE = "NF-001";

    public EntityNotFoundException(String userMessage) {
        super(DEFAULT_CODE, userMessage);
    }

    public EntityNotFoundException(String userMessage, Throwable cause) {
        super(DEFAULT_CODE, userMessage, cause);
    }

    public EntityNotFoundException(String code, String userMessage) {
        super(code, userMessage);
    }

    /**
     * 使用默认错误码构造异常。
     *
     * @param userMessage 用户提示文案
     * @return 异常实例
     */
    public static EntityNotFoundException of(String userMessage) {
        return new EntityNotFoundException(userMessage);
    }

    /**
     * 使用默认错误码构造异常并保留根因。
     *
     * @param userMessage 用户提示文案
     * @param cause       根因
     * @return 异常实例
     */
    public static EntityNotFoundException of(String userMessage, Throwable cause) {
        return new EntityNotFoundException(userMessage, cause);
    }

    /**
     * 使用指定错误码构造异常。
     *
     * @param code        错误码
     * @param userMessage 用户提示文案
     * @return 异常实例
     */
    public static EntityNotFoundException ofCode(String code, String userMessage) {
        return new EntityNotFoundException(code, userMessage);
    }
}
