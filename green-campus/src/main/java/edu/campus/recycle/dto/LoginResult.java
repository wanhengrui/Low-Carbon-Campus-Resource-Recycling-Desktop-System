package edu.campus.recycle.dto;

import edu.campus.recycle.entity.User;

import java.time.LocalDateTime;

/**
 * 登录结果（契约第 4 节）：登录成功后回填用户概要信息与最近登录时间，
 * 供控制台/界面提示与后续页面数据加载使用。
 */
public class LoginResult {

    /** 是否成功 */
    private boolean success;
    /** 用户ID */
    private Integer userId;
    /** 登录名 */
    private String username;
    /** 真实姓名 */
    private String realName;
    /** 角色：STUDENT/TEACHER/ADMIN */
    private String role;
    /** 信用分 */
    private Integer creditScore;
    /** 本次登录时间 */
    private LocalDateTime loginAt;
    /** 提示信息 */
    private String message;

    public LoginResult() {
    }

    public LoginResult(boolean success, Integer userId, String username, String realName,
                       String role, Integer creditScore, LocalDateTime loginAt, String message) {
        this.success = success;
        this.userId = userId;
        this.username = username;
        this.realName = realName;
        this.role = role;
        this.creditScore = creditScore;
        this.loginAt = loginAt;
        this.message = message;
    }

    /**
     * 由用户实体构建登录成功结果。
     *
     * @param user     登录成功的用户
     * @param loginAt  登录时间
     * @return 登录结果
     */
    public static LoginResult ofSuccess(User user, LocalDateTime loginAt) {
        return new LoginResult(true, user.getId(), user.getUsername(), user.getRealName(),
                user.getRole(), user.getCreditScore(), loginAt, "登录成功");
    }

    public boolean isSuccess() {
        return success;
    }

    public void setSuccess(boolean success) {
        this.success = success;
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

    public String getRole() {
        return role;
    }

    public void setRole(String role) {
        this.role = role;
    }

    public Integer getCreditScore() {
        return creditScore;
    }

    public void setCreditScore(Integer creditScore) {
        this.creditScore = creditScore;
    }

    public LocalDateTime getLoginAt() {
        return loginAt;
    }

    public void setLoginAt(LocalDateTime loginAt) {
        this.loginAt = loginAt;
    }

    public String getMessage() {
        return message;
    }

    public void setMessage(String message) {
        this.message = message;
    }

    @Override
    public String toString() {
        return "LoginResult{success=" + success + ", userId=" + userId + ", username=" + username
                + ", role=" + role + ", creditScore=" + creditScore + ", message=" + message + '}';
    }
}
