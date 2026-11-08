package edu.campus.recycle.exception;

/**
 * 业务规则异常：违反 BR-01..BR-12 时抛出，{@code code} 携带被违反的 BR 编号
 * （如 {@code BR-04}），便于界面直接展示"信用分不足"等明确原因。
 */
public class BusinessRuleException extends AppException {

    private static final long serialVersionUID = 1L;

    /** 被违反的业务规则编号，形如 BR-04 */
    private final String brCode;

    /**
     * 构造业务规则异常。
     *
     * @param brCode      业务规则编号，允许传 "BR-04" 或 "04"
     * @param userMessage 用户提示文案
     */
    public BusinessRuleException(String brCode, String userMessage) {
        super(normalize(brCode), userMessage);
        this.brCode = normalize(brCode);
    }

    public BusinessRuleException(String brCode, String userMessage, Throwable cause) {
        super(normalize(brCode), userMessage, cause);
        this.brCode = normalize(brCode);
    }

    private static String normalize(String brCode) {
        if (brCode == null || brCode.isBlank()) {
            return "BR-000";
        }
        String trimmed = brCode.trim().toUpperCase();
        return trimmed.startsWith("BR-") ? trimmed : "BR-" + trimmed;
    }

    /**
     * 构造业务规则异常（无根因）。
     *
     * @param brCode      业务规则编号
     * @param userMessage 用户提示文案
     * @return 异常实例
     */
    public static BusinessRuleException of(String brCode, String userMessage) {
        return new BusinessRuleException(brCode, userMessage);
    }

    /**
     * 构造业务规则异常（保留根因）。
     *
     * @param brCode      业务规则编号
     * @param userMessage 用户提示文案
     * @param cause       根因
     * @return 异常实例
     */
    public static BusinessRuleException of(String brCode, String userMessage, Throwable cause) {
        return new BusinessRuleException(brCode, userMessage, cause);
    }

    public String getBrCode() {
        return brCode;
    }
}
