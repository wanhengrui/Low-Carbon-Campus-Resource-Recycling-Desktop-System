package edu.campus.recycle.util;

import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Test;

import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertNotEquals;
import static org.junit.jupiter.api.Assertions.assertTrue;

/**
 * {@link PasswordUtil} 单元测试：PBKDF2WithHmacSHA256 加盐哈希与校验。
 */
class PasswordUtilTest {

    @Test
    @DisplayName("盐应为 16 字节随机数的 Base64 文本")
    void generateSaltShouldBeBase64Of16Bytes() {
        String salt = PasswordUtil.generateSalt();
        assertNotEquals(salt, PasswordUtil.generateSalt(), "两次生成的盐不应相同");
        byte[] decoded = java.util.Base64.getDecoder().decode(salt);
        assertTrue(decoded.length == PasswordUtil.SALT_BYTES,
                "盐解码后长度应为 " + PasswordUtil.SALT_BYTES + " 字节");
    }

    @Test
    @DisplayName("相同口令与盐应得到相同摘要（确定性）")
    void hashShouldBeDeterministic() {
        String salt = PasswordUtil.generateSalt();
        assertTrue(PasswordUtil.hash("Demo@12345", salt).equals(PasswordUtil.hash("Demo@12345", salt)));
    }

    @Test
    @DisplayName("正确口令应通过校验")
    void verifyShouldAcceptCorrectPassword() {
        String salt = PasswordUtil.generateSalt();
        String hash = PasswordUtil.hash("Demo@12345", salt);
        assertTrue(PasswordUtil.verify("Demo@12345", salt, hash));
    }

    @Test
    @DisplayName("错误口令应校验失败")
    void verifyShouldRejectWrongPassword() {
        String salt = PasswordUtil.generateSalt();
        String hash = PasswordUtil.hash("Demo@12345", salt);
        assertFalse(PasswordUtil.verify("Demo@12346", salt, hash));
    }

    @Test
    @DisplayName("encodeDemo 应返回 salt:hash 两段结构")
    void encodeDemoShouldReturnSaltAndHash() {
        String encoded = PasswordUtil.encodeDemo("Admin@123");
        String[] parts = encoded.split(":");
        assertTrue(parts.length == 2, "encodeDemo 结果应包含盐与摘要两段");
        assertTrue(PasswordUtil.verify("Admin@123", parts[0], parts[1]));
    }
}
