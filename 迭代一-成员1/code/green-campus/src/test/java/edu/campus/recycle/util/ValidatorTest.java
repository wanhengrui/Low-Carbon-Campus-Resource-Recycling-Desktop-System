package edu.campus.recycle.util;

import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Test;

import java.math.BigDecimal;

import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;

/**
 * {@link Validator} 单元测试：BR-01 用户名/口令/学号规则与 BR-12 图片规则。
 */
class ValidatorTest {

    @Test
    @DisplayName("合法用户名应通过（4-20 位字母数字下划线）")
    void validUsernameShouldPass() {
        assertTrue(Validator.isValidUsername("zhang_san01"));
        assertTrue(Validator.isValidUsername("abcd"));
    }

    @Test
    @DisplayName("非法用户名应被拒绝")
    void invalidUsernameShouldFail() {
        assertFalse(Validator.isValidUsername("ab"));
        assertFalse(Validator.isValidUsername("张三同学"));
        assertFalse(Validator.isValidUsername("bad-name"));
    }

    @Test
    @DisplayName("口令必须同时包含字母与数字且长度 8-20")
    void passwordShouldRequireLetterAndDigit() {
        assertTrue(Validator.isValidPassword("Demo@12345"));
        assertFalse(Validator.isValidPassword("12345678"));
        assertFalse(Validator.isValidPassword("abcdefgh"));
        assertFalse(Validator.isValidPassword("Ab1"));
    }

    @Test
    @DisplayName("学号必须为 8-12 位数字")
    void studentNoShouldBe8To12Digits() {
        assertTrue(Validator.isValidStudentNo("20239901"));
        assertFalse(Validator.isValidStudentNo("2023"));
        assertFalse(Validator.isValidStudentNo("2023990X"));
    }

    @Test
    @DisplayName("图片仅允许 jpg/jpeg/png 后缀")
    void imageFileNameShouldOnlyAllowCommonSuffixes() {
        assertTrue(Validator.isValidImageFileName("book.jpg"));
        assertTrue(Validator.isValidImageFileName("photo.JPEG"));
        assertTrue(Validator.isValidImageFileName("cover.png"));
        assertFalse(Validator.isValidImageFileName("cover.gif"));
    }

    @Test
    @DisplayName("价格不得为负，描述长度受 500 字限制")
    void priceAndDescriptionShouldBeValidated() {
        assertTrue(Validator.isValidPrice(new BigDecimal("45.00")));
        assertFalse(Validator.isValidPrice(new BigDecimal("-1")));
        assertTrue(Validator.isValidDescription("九成新教材"));
        assertThrows(RuntimeException.class, () -> Validator.checkUsername("a"));
    }
}
