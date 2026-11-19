package edu.campus.recycle.exception;

/**
 * 数据访问异常：JDBC 操作失败时由模板方法统一转换，屏蔽底层 SQLException 细节。
 */
public class DataAccessException extends AppException {

    private static final long serialVersionUID = 1L;

    /** 默认错误码前缀（子类可传入更细粒度的错误码） */
    public static final String DEFAULT_CODE = "DB-001";

    public DataAccessException(String userMessage) {
        super(DEFAULT_CODE, userMessage);
    }

    public DataAccessException(String userMessage, Throwable cause) {
        super(DEFAULT_CODE, userMessage, cause);
    }

    public DataAccessException(String code, String userMessage) {
        super(code, userMessage);
    }

    /**
     * 使用默认错误码构造异常。
     *
     * @param userMessage 用户提示文案
     * @return 异常实例
     */
    public static DataAccessException of(String userMessage) {
        return new DataAccessException(userMessage);
    }

    /**
     * 使用默认错误码构造异常并保留根因。
     *
     * @param userMessage 用户提示文案
     * @param cause       根因
     * @return 异常实例
     */
    public static DataAccessException of(String userMessage, Throwable cause) {
        return new DataAccessException(userMessage, cause);
    }

    /**
     * 使用指定错误码构造异常。
     *
     * @param code        错误码
     * @param userMessage 用户提示文案
     * @return 异常实例
     */
    public static DataAccessException ofCode(String code, String userMessage) {
        return new DataAccessException(code, userMessage);
    }
}
