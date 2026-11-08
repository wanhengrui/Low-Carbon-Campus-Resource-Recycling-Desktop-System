package edu.campus.recycle.util;

import javax.crypto.SecretKeyFactory;
import javax.crypto.spec.PBEKeySpec;
import java.nio.charset.StandardCharsets;
import java.security.GeneralSecurityException;
import java.security.MessageDigest;
import java.security.SecureRandom;
import java.util.Base64;

/**
 * 口令工具类（BR-02）：PBKDF2WithHmacSHA256，100000 次迭代、16 字节随机盐、256 位密钥，Base64 编码。
 *
 * <p>存储格式：{@code user.password_hash} 存 Base64 摘要，{@code user.salt} 存 Base64 盐；
 * 任何日志、界面、异常信息均不得输出明文口令或盐。</p>
 */
public final class PasswordUtil {

    /** 摘要算法 */
    public static final String ALGORITHM = "PBKDF2WithHmacSHA256";
    /** 迭代次数（BR-02） */
    public static final int ITERATIONS = 100_000;
    /** 盐字节数（BR-02） */
    public static final int SALT_BYTES = 16;
    /** 密钥位数（BR-02） */
    public static final int KEY_BITS = 256;

    private static final SecureRandom RANDOM = new SecureRandom();
    private static final Base64.Encoder ENCODER = Base64.getEncoder();
    private static final Base64.Decoder DECODER = Base64.getDecoder();

    private PasswordUtil() {
    }

    /**
     * 生成 16 字节随机盐并 Base64 编码。
     *
     * @return Base64 盐字符串
     */
    public static String generateSalt() {
        byte[] salt = new byte[SALT_BYTES];
        RANDOM.nextBytes(salt);
        return ENCODER.encodeToString(salt);
    }

    /**
     * 计算口令摘要。
     *
     * @param rawPassword 明文口令
     * @param saltBase64  Base64 盐
     * @return Base64 摘要
     */
    public static String hash(String rawPassword, String saltBase64) {
        if (rawPassword == null || saltBase64 == null) {
            throw new IllegalArgumentException("口令与盐不能为空");
        }
        char[] chars = rawPassword.toCharArray();
        byte[] salt = DECODER.decode(saltBase64);
        PBEKeySpec spec = new PBEKeySpec(chars, salt, ITERATIONS, KEY_BITS);
        try {
            SecretKeyFactory factory = SecretKeyFactory.getInstance(ALGORITHM);
            byte[] encoded = factory.generateSecret(spec).getEncoded();
            return ENCODER.encodeToString(encoded);
        } catch (GeneralSecurityException e) {
            throw new IllegalStateException("口令摘要计算失败", e);
        } finally {
            spec.clearPassword();
            java.util.Arrays.fill(chars, '\0');
        }
    }

    /**
     * 校验口令：对候选口令重新做 PBKDF2 后与存储摘要做常量时间比较。
     *
     * @param rawPassword  明文口令
     * @param saltBase64   Base64 盐
     * @param expectedHash 存储的 Base64 摘要
     * @return 一致返回 true
     */
    public static boolean verify(String rawPassword, String saltBase64, String expectedHash) {
        if (rawPassword == null || saltBase64 == null || expectedHash == null) {
            return false;
        }
        String actual = hash(rawPassword, saltBase64);
        return MessageDigest.isEqual(actual.getBytes(StandardCharsets.UTF_8),
                expectedHash.getBytes(StandardCharsets.UTF_8));
    }

    /**
     * 为 {@code admin/Admin@123} 等演示数据生成"盐:摘要"格式字符串的辅助方法，
     * 仅供种子数据生成脚本与单元测试使用。
     *
     * @param rawPassword 明文口令
     * @return {@code salt:hash} 形式的演示串
     */
    public static String encodeDemo(String rawPassword) {
        String salt = generateSalt();
        return salt + ":" + hash(rawPassword, salt);
    }
}
