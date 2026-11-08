package edu.campus.recycle.util;

import edu.campus.recycle.exception.ValidationException;

import java.math.BigDecimal;
import java.util.regex.Pattern;

/**
 * 输入校验器（BR-01、BR-12）：集中管理用户名、口令、学号、价格、图片等规则，
 * 避免各层重复编写正则导致口径漂移。
 */
public final class Validator {

    /** 用户名：4–20 位字母、数字、下划线（BR-01） */
    public static final Pattern USERNAME = Pattern.compile("^[A-Za-z0-9_]{4,20}$");
    /** 口令：8–20 位且同时包含字母与数字（BR-01） */
    public static final Pattern PASSWORD = Pattern.compile("^(?=.*[A-Za-z])(?=.*\\d)\\S{8,20}$");
    /** 学号/工号：8–12 位数字（BR-01） */
    public static final Pattern STUDENT_NO = Pattern.compile("^\\d{8,12}$");
    /** 图片扩展名：仅 jpg/jpeg/png（BR-12） */
    public static final Pattern IMAGE_FILE = Pattern.compile("(?i)^[^\\\\/:*?\"<>|]+\\.(jpg|jpeg|png)$");
    /** 手机号（可选联系方式，11 位数字） */
    public static final Pattern MOBILE = Pattern.compile("^1[3-9]\\d{9}$");

    /** 单张图片上限 2MB（BR-12） */
    public static final long MAX_IMAGE_BYTES = 2L * 1024L * 1024L;
    /** 单物品最多 5 张图（BR-12） */
    public static final int MAX_IMAGE_COUNT = 5;
    /** 标题 2–50 字 */
    public static final int TITLE_MIN = 2;
    public static final int TITLE_MAX = 50;
    /** 描述 ≤500 字 */
    public static final int DESCRIPTION_MAX = 500;
    /** 消息 ≤300 字 */
    public static final int MESSAGE_MAX = 300;

    private Validator() {
    }

    // ------------------------------------------------------------------ 布尔判定

    public static boolean isValidUsername(String username) {
        return username != null && USERNAME.matcher(username).matches();
    }

    public static boolean isValidPassword(String rawPassword) {
        return rawPassword != null && PASSWORD.matcher(rawPassword).matches();
    }

    public static boolean isValidStudentNo(String studentNo) {
        return studentNo != null && STUDENT_NO.matcher(studentNo).matches();
    }

    public static boolean isValidImageFileName(String fileName) {
        return fileName != null && IMAGE_FILE.matcher(fileName).matches();
    }

    public static boolean isValidImageSize(long bytes) {
        return bytes > 0 && bytes <= MAX_IMAGE_BYTES;
    }

    public static boolean isValidImageCount(int count) {
        return count >= 0 && count <= MAX_IMAGE_COUNT;
    }

    public static boolean isValidPrice(BigDecimal price) {
        return price != null && price.compareTo(BigDecimal.ZERO) >= 0;
    }

    public static boolean isValidTitle(String title) {
        return title != null && title.length() >= TITLE_MIN && title.length() <= TITLE_MAX;
    }

    public static boolean isValidDescription(String description) {
        return description != null && description.length() <= DESCRIPTION_MAX;
    }

    public static boolean isValidCreditScore(int score) {
        return score >= 0 && score <= 150;
    }

    // ------------------------------------------------------------------ 断言式校验

    /**
     * 校验用户名，不合法时抛出 {@link ValidationException}。
     *
     * @param username 用户名
     */
    public static void checkUsername(String username) {
        if (!isValidUsername(username)) {
            throw ValidationException.of("用户名必须为 4–20 位字母、数字或下划线");
        }
    }

    /**
     * 校验口令强度，不合法时抛出 {@link ValidationException}。
     *
     * @param rawPassword 明文口令
     */
    public static void checkPassword(String rawPassword) {
        if (!isValidPassword(rawPassword)) {
            throw ValidationException.of("口令必须为 8–20 位且同时包含字母与数字");
        }
    }

    /**
     * 校验学号，不合法时抛出 {@link ValidationException}。
     *
     * @param studentNo 学号/工号
     */
    public static void checkStudentNo(String studentNo) {
        if (!isValidStudentNo(studentNo)) {
            throw ValidationException.of("学号必须为 8–12 位数字");
        }
    }

    /**
     * 校验标题，不合法时抛出 {@link ValidationException}。
     *
     * @param title 标题
     */
    public static void checkTitle(String title) {
        if (!isValidTitle(title)) {
            throw ValidationException.of("标题长度必须为 2–50 字");
        }
    }

    /**
     * 校验图片文件名、大小与张数（BR-12）。
     *
     * @param fileName 文件名（含扩展名）
     * @param bytes    文件字节数
     * @param count    已选图片张数
     */
    public static void checkImage(String fileName, long bytes, int count) {
        if (!isValidImageFileName(fileName)) {
            throw ValidationException.of("图片仅支持 jpg/jpeg/png 格式");
        }
        if (!isValidImageSize(bytes)) {
            throw ValidationException.of("单张图片不得超过 2MB");
        }
        if (!isValidImageCount(count)) {
            throw ValidationException.of("每个物品最多上传 5 张图片");
        }
    }
}
