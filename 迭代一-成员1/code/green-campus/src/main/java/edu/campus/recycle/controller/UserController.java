package edu.campus.recycle.controller;

import edu.campus.recycle.dto.LoginResult;
import edu.campus.recycle.dto.UserCreditDTO;
import edu.campus.recycle.entity.User;
import edu.campus.recycle.exception.AppException;
import edu.campus.recycle.service.UserService;
import edu.campus.recycle.util.ServiceFactory;

import java.util.List;

/**
 * 用户控制器（薄壳，第 3 轮裁决 v1.1 §13-15）：注册、登录、改密、冻结/解冻、用户查询与信用视图。
 *
 * <p>只做参数校验、调用 {@link UserService}、把 {@link AppException} 转成用户文案；
 * 不访问 DAO，界面层（Swing）只依赖本类与其它控制器。</p>
 */
public class UserController {

    private final UserService userService;

    public UserController() {
        this(ServiceFactory.getInstance().getUserService());
    }

    /**
     * 构造控制器（允许注入自定义服务实现，便于界面层测试）。
     *
     * @param userService 用户服务
     */
    public UserController(UserService userService) {
        ControllerSupport.require(userService != null, "userService 不能为空");
        this.userService = userService;
    }

    /**
     * 注册新用户。
     *
     * @return 用户可读结果文案
     */
    public String register(String username, String rawPassword, String realName, String studentNo,
                           String role, String college, String contact) {
        try {
            User user = userService.register(username, rawPassword, realName, studentNo, role, college, contact);
            return "注册成功：userId=" + user.getId() + "，用户名=" + user.getUsername()
                    + "，初始信用分=" + user.getCreditScore();
        } catch (AppException e) {
            return ControllerSupport.text(e);
        }
    }

    /**
     * 登录：失败时返回 {@code success=false} 的结果对象并由 {@code message} 携带文案。
     *
     * @return 登录结果（永不返回 null）
     */
    public LoginResult login(String username, String rawPassword) {
        ControllerSupport.require(ControllerSupport.hasText(username), "用户名不能为空");
        ControllerSupport.require(ControllerSupport.hasText(rawPassword), "密码不能为空");
        try {
            return userService.login(username, rawPassword);
        } catch (AppException e) {
            return new LoginResult(false, null, username, null, null, null, null, ControllerSupport.text(e));
        }
    }

    /**
     * 修改密码。
     *
     * @return 用户可读结果文案
     */
    public String changePassword(int userId, String oldPwd, String newPwd) {
        ControllerSupport.require(userId > 0, "用户ID非法");
        try {
            userService.changePassword(userId, oldPwd, newPwd);
            return "密码修改成功";
        } catch (AppException e) {
            return ControllerSupport.text(e);
        }
    }

    /**
     * 冻结用户（仅管理员）。
     *
     * @return 用户可读结果文案
     */
    public String freezeUser(int operatorId, int userId) {
        try {
            userService.freezeUser(operatorId, userId);
            return "已冻结用户：userId=" + userId;
        } catch (AppException e) {
            return ControllerSupport.text(e);
        }
    }

    /**
     * 解冻用户（仅管理员）。
     *
     * @return 用户可读结果文案
     */
    public String unfreezeUser(int operatorId, int userId) {
        try {
            userService.unfreezeUser(operatorId, userId);
            return "已解冻用户：userId=" + userId;
        } catch (AppException e) {
            return ControllerSupport.text(e);
        }
    }

    /**
     * 分页查询用户（管理端）。
     */
    public List<User> queryUsers(String keyword, String role, int pageNo, int pageSize) {
        return userService.queryUsers(keyword, role, Math.max(1, pageNo), Math.min(Math.max(1, pageSize), 100));
    }

    /**
     * 查询用户信用视图（信用分/等级/变更次数）。
     *
     * @return 信用视图，用户不存在时返回 null
     */
    public UserCreditDTO getCredit(int userId) {
        ControllerSupport.require(userId > 0, "用户ID非法");
        try {
            return userService.getCredit(userId);
        } catch (AppException e) {
            return null;
        }
    }
}
