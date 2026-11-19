package edu.campus.recycle.dto;

/**
 * 用户信用视图对象（契约第 4 节），用于控制台/界面展示信用分与信用等级，
 * 不参与持久化，由 Service 依据 {@code user.credit_score} 实时组装。
 */
public class UserCreditDTO {

    /** 用户ID */
    private Integer userId;
    /** 登录名 */
    private String username;
    /** 真实姓名 */
    private String realName;
    /** 信用分 */
    private Integer creditScore;
    /** 信用等级：优秀/良好/正常/受限 */
    private String creditLevel;
    /** 信用分变更次数（来自 credit_log 统计） */
    private int changeCount;

    public UserCreditDTO() {
    }

    public UserCreditDTO(Integer userId, String username, String realName, Integer creditScore,
                         String creditLevel, int changeCount) {
        this.userId = userId;
        this.username = username;
        this.realName = realName;
        this.creditScore = creditScore;
        this.creditLevel = creditLevel;
        this.changeCount = changeCount;
    }

    /**
     * 按信用分区间推导信用等级：≥120 优秀、≥100 良好、≥60 正常、&lt;60 受限。
     *
     * @param score 信用分
     * @return 信用等级中文名
     */
    public static String levelOf(Integer score) {
        int value = score == null ? 0 : score;
        if (value >= 120) {
            return "优秀";
        }
        if (value >= 100) {
            return "良好";
        }
        if (value >= 60) {
            return "正常";
        }
        return "受限";
    }

    public Integer getUserId() {
        return userId;
    }

    public void setUserId(Integer userId) {
        this.userId = userId;
    }

    public String getUsername() {
        return username;
    }

    public void setUsername(String username) {
        this.username = username;
    }

    public String getRealName() {
        return realName;
    }

    public void setRealName(String realName) {
        this.realName = realName;
    }

    public Integer getCreditScore() {
        return creditScore;
    }

    public void setCreditScore(Integer creditScore) {
        this.creditScore = creditScore;
    }

    public String getCreditLevel() {
        return creditLevel;
    }

    public void setCreditLevel(String creditLevel) {
        this.creditLevel = creditLevel;
    }

    public int getChangeCount() {
        return changeCount;
    }

    public void setChangeCount(int changeCount) {
        this.changeCount = changeCount;
    }

    @Override
    public String toString() {
        return "UserCreditDTO{userId=" + userId + ", username=" + username + ", realName=" + realName
                + ", creditScore=" + creditScore + ", creditLevel=" + creditLevel
                + ", changeCount=" + changeCount + '}';
    }
}
