package edu.campus.recycle.entity;

import java.time.LocalDateTime;

/**
 * 用户实体，与数据库表 {@code user} 一一对应（契约第 3.1 节，字段不得增删）。
 *
 * <p>字段名由表字段下划线形式转驼峰，金额使用 {@link java.math.BigDecimal}，
 * 时间使用 {@link java.time.LocalDateTime}，布尔语义字段使用 {@link Boolean}。</p>
 */
public class User {

    /** 用户ID（主键） */
    private Integer id;

    /** 登录名，4–20 位字母数字下划线 */
    private String username;

    /** PBKDF2WithHmacSHA256 Base64 摘要 */
    private String passwordHash;

    /** 16 字节随机盐 Base64 */
    private String salt;

    /** 真实姓名 */
    private String realName;

    /** 学号/工号，8–12 位数字 */
    private String studentNo;

    /** 角色：STUDENT/TEACHER/ADMIN */
    private String role;

    /** 学院 */
    private String college;

    /** 联系方式（手机/邮箱） */
    private String contact;

    /** 信用分，0–150，默认 100 */
    private Integer creditScore;

    /** 账号状态：ACTIVE/FROZEN/CANCELLED */
    private String status;

    /** 连续登录失败次数 */
    private Integer failCount;

    /** 锁定截止时间（失败 5 次锁 15 分钟） */
    private LocalDateTime lockedUntil;

    /** 注册时间 */
    private LocalDateTime createdAt;

    /** 更新时间 */
    private LocalDateTime updatedAt;

    /** 最近登录时间 */
    private LocalDateTime lastLoginAt;

    /** 无参构造器，供 DAO 与框架反射使用。 */
    public User() {
    }

    /** 全参构造器。 */
    public User(Integer id, String username, String passwordHash, String salt, String realName, String studentNo, String role, String college, String contact, Integer creditScore, String status, Integer failCount, LocalDateTime lockedUntil, LocalDateTime createdAt, LocalDateTime updatedAt, LocalDateTime lastLoginAt) {
        this.id = id;
        this.username = username;
        this.passwordHash = passwordHash;
        this.salt = salt;
        this.realName = realName;
        this.studentNo = studentNo;
        this.role = role;
        this.college = college;
        this.contact = contact;
        this.creditScore = creditScore;
        this.status = status;
        this.failCount = failCount;
        this.lockedUntil = lockedUntil;
        this.createdAt = createdAt;
        this.updatedAt = updatedAt;
        this.lastLoginAt = lastLoginAt;
    }

    public Integer getId() {
        return id;
    }

    public void setId(Integer id) {
        this.id = id;
    }

    public String getUsername() {
        return username;
    }

    public void setUsername(String username) {
        this.username = username;
    }

    public String getPasswordHash() {
        return passwordHash;
    }

    public void setPasswordHash(String passwordHash) {
        this.passwordHash = passwordHash;
    }

    public String getSalt() {
        return salt;
    }

    public void setSalt(String salt) {
        this.salt = salt;
    }

    public String getRealName() {
        return realName;
    }

    public void setRealName(String realName) {
        this.realName = realName;
    }

    public String getStudentNo() {
        return studentNo;
    }

    public void setStudentNo(String studentNo) {
        this.studentNo = studentNo;
    }

    public String getRole() {
        return role;
    }

    public void setRole(String role) {
        this.role = role;
    }

    public String getCollege() {
        return college;
    }

    public void setCollege(String college) {
        this.college = college;
    }

    public String getContact() {
        return contact;
    }

    public void setContact(String contact) {
        this.contact = contact;
    }

    public Integer getCreditScore() {
        return creditScore;
    }

    public void setCreditScore(Integer creditScore) {
        this.creditScore = creditScore;
    }

    public String getStatus() {
        return status;
    }

    public void setStatus(String status) {
        this.status = status;
    }

    public Integer getFailCount() {
        return failCount;
    }

    public void setFailCount(Integer failCount) {
        this.failCount = failCount;
    }

    public LocalDateTime getLockedUntil() {
        return lockedUntil;
    }

    public void setLockedUntil(LocalDateTime lockedUntil) {
        this.lockedUntil = lockedUntil;
    }

    public LocalDateTime getCreatedAt() {
        return createdAt;
    }

    public void setCreatedAt(LocalDateTime createdAt) {
        this.createdAt = createdAt;
    }

    public LocalDateTime getUpdatedAt() {
        return updatedAt;
    }

    public void setUpdatedAt(LocalDateTime updatedAt) {
        this.updatedAt = updatedAt;
    }

    public LocalDateTime getLastLoginAt() {
        return lastLoginAt;
    }

    public void setLastLoginAt(LocalDateTime lastLoginAt) {
        this.lastLoginAt = lastLoginAt;
    }

    @Override
    public String toString() {
        return "User{" + "id=" + id + ", " + "username=" + username + ", " + "passwordHash=<hidden>" + ", " + "salt=<hidden>" + ", " + "realName=" + realName + ", " + "studentNo=" + studentNo + ", " + "role=" + role + ", " + "college=" + college + ", " + "contact=" + contact + ", " + "creditScore=" + creditScore + ", " + "status=" + status + ", " + "failCount=" + failCount + ", " + "lockedUntil=" + lockedUntil + ", " + "createdAt=" + createdAt + ", " + "updatedAt=" + updatedAt + ", " + "lastLoginAt=" + lastLoginAt + '}';
    }
}
