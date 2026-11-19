package edu.campus.recycle.service;

import edu.campus.recycle.dto.LoginResult;
import edu.campus.recycle.dto.UserCreditDTO;
import edu.campus.recycle.entity.User;
import edu.campus.recycle.exception.AccountLockedException;
import edu.campus.recycle.exception.AuthenticationException;
import edu.campus.recycle.exception.BusinessRuleException;
import edu.campus.recycle.exception.DuplicateEntityException;
import edu.campus.recycle.exception.EntityNotFoundException;
import edu.campus.recycle.exception.PermissionDeniedException;
import edu.campus.recycle.exception.ValidationException;

import java.util.List;

/**
 * 用户服务：注册、登录、改密、查询、冻结/解冻、信用分调整。
 *
 * <p>方法签名逐字对齐《共享契约-实体与接口基线》第 6 节。</p>
 */
public interface UserService {

    /**
     * 注册新用户（BR-01 校验、BR-02 口令哈希、用户名/学号唯一）。
     *
     * @param username    用户名 4-20 位，仅字母数字下划线
     * @param rawPassword 明文密码 8-20 位且同时包含字母与数字
     * @param realName    真实姓名
     * @param studentNo   学号 8-12 位数字，教师/管理员可为空
     * @param role        角色编码 STUDENT/TEACHER/ADMIN，为空时默认 STUDENT
     * @param college     学院
     * @param contact     联系方式
     * @return 已回填主键的用户对象（不含明文口令）
     * @throws ValidationException      字段校验失败
     * @throws DuplicateEntityException 用户名或学号已存在
     */
    User register(String username, String rawPassword, String realName, String studentNo,
                  String role, String college, String contact)
            throws ValidationException, DuplicateEntityException;

    /**
     * 登录（BR-03：连续失败 5 次锁定 15 分钟）。
     *
     * @throws AuthenticationException 用户名或密码错误、账号非正常状态
     * @throws AccountLockedException  账号处于锁定期
     */
    LoginResult login(String username, String rawPassword)
            throws AuthenticationException, AccountLockedException;

    /**
     * 修改密码。
     */
    void changePassword(int userId, String oldPwd, String newPwd)
            throws AuthenticationException, ValidationException;

    User findById(int userId) throws EntityNotFoundException;

    List<User> queryUsers(String keyword, String role, int pageNo, int pageSize);

    void freezeUser(int operatorId, int userId) throws PermissionDeniedException, BusinessRuleException;

    void unfreezeUser(int operatorId, int userId) throws PermissionDeniedException;

    void updateCredit(int userId, int delta, Integer flowId, String reason) throws BusinessRuleException;

    /**
     * 查询用户信用视图（第 3 轮裁决 v1.1 §13-14）：信用分、信用等级与变更次数，
     * 供界面层展示，不参与持久化。
     *
     * @param userId 用户ID
     * @return 信用视图对象
     * @throws EntityNotFoundException 用户不存在
     */
    UserCreditDTO getCredit(int userId) throws EntityNotFoundException;
}
