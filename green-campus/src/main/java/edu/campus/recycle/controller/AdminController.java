package edu.campus.recycle.controller;

import edu.campus.recycle.entity.OperationLog;
import edu.campus.recycle.exception.AppException;
import edu.campus.recycle.service.AdminService;
import edu.campus.recycle.util.ServiceFactory;

import java.util.List;

/**
 * 管理员控制器（薄壳，第 3 轮裁决 v1.1 §13-15）：两级分类维护与操作日志查询（BR-10/BR-11）。
 *
 * <p>只做参数校验、调用 {@link AdminService}、把 {@link AppException} 转成用户文案。</p>
 */
public class AdminController {

    private final AdminService adminService;

    public AdminController() {
        this(ServiceFactory.getInstance().getAdminService());
    }

    /**
     * 构造控制器（允许注入自定义服务实现）。
     *
     * @param adminService 管理服务
     */
    public AdminController(AdminService adminService) {
        ControllerSupport.require(adminService != null, "adminService 不能为空");
        this.adminService = adminService;
    }

    /**
     * 新增分类（父分类为空表示一级分类）。
     *
     * @return 用户可读结果文案
     */
    public String addCategory(int operatorId, String name, Integer parentId) {
        ControllerSupport.require(ControllerSupport.hasText(name), "分类名称不能为空");
        try {
            adminService.addCategory(operatorId, name, parentId);
            return "分类创建成功：" + name;
        } catch (AppException e) {
            return ControllerSupport.text(e);
        }
    }

    /**
     * 启用/停用分类。
     *
     * @return 用户可读结果文案
     */
    public String toggleCategory(int operatorId, int categoryId, boolean enabled) {
        ControllerSupport.require(categoryId > 0, "分类ID非法");
        try {
            adminService.toggleCategory(operatorId, categoryId, enabled);
            return (enabled ? "分类已启用：" : "分类已停用：") + categoryId;
        } catch (AppException e) {
            return ControllerSupport.text(e);
        }
    }

    /**
     * 最近操作日志（limit 限制在 1-200）。
     */
    public List<OperationLog> recentLogs(int limit) {
        return adminService.recentLogs(Math.min(Math.max(1, limit), 200));
    }
}
