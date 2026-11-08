package edu.campus.recycle.service.impl;

import edu.campus.recycle.dao.CategoryDao;
import edu.campus.recycle.dao.OperationLogDao;
import edu.campus.recycle.dao.UserDao;
import edu.campus.recycle.entity.Category;
import edu.campus.recycle.entity.OperationLog;
import edu.campus.recycle.entity.Role;
import edu.campus.recycle.entity.User;
import edu.campus.recycle.exception.DuplicateEntityException;
import edu.campus.recycle.exception.EntityNotFoundException;
import edu.campus.recycle.exception.PermissionDeniedException;
import edu.campus.recycle.exception.ValidationException;
import edu.campus.recycle.service.AdminService;
import edu.campus.recycle.util.DbUtil;

import java.time.LocalDateTime;
import java.util.List;
import java.util.Objects;

/**
 * 管理服务实现：两级分类维护（BR-10）与操作日志查询（BR-11）。
 */
public class AdminServiceImpl implements AdminService {

    private static final int CATEGORY_NAME_MIN = 2;
    private static final int CATEGORY_NAME_MAX = 20;
    private static final int DEFAULT_RECENT_LIMIT = 20;

    private final CategoryDao categoryDao;
    private final OperationLogDao operationLogDao;
    private final UserDao userDao;

    public AdminServiceImpl(CategoryDao categoryDao, OperationLogDao operationLogDao, UserDao userDao) {
        this.categoryDao = Objects.requireNonNull(categoryDao, "categoryDao");
        this.operationLogDao = Objects.requireNonNull(operationLogDao, "operationLogDao");
        this.userDao = Objects.requireNonNull(userDao, "userDao");
    }

    @Override
    public void addCategory(int operatorId, String name, Integer parentId) throws DuplicateEntityException {
        requireAdmin(operatorId);
        String trimmed = name == null ? "" : name.trim();
        if (trimmed.length() < CATEGORY_NAME_MIN || trimmed.length() > CATEGORY_NAME_MAX) {
            throw ValidationException.of("分类名称长度需为 " + CATEGORY_NAME_MIN + "-" + CATEGORY_NAME_MAX + " 个字符");
        }
        if (parentId != null) {
            Category parent = categoryDao.findById(parentId)
                    .orElseThrow(() -> EntityNotFoundException.of("父分类不存在：id=" + parentId));
            if (parent.getParentId() != null) {
                throw ValidationException.of("分类最多支持两级，父分类必须是一级分类");
            }
        }
        if (categoryDao.existsByName(parentId, trimmed)) {
            throw DuplicateEntityException.of("同级分类名称已存在：" + trimmed);
        }
        Category category = new Category();
        category.setName(trimmed);
        category.setParentId(parentId);
        category.setSortOrder(99);
        category.setEnabled(Boolean.TRUE);
        category.setCreatedAt(LocalDateTime.now().withNano(0));
        DbUtil.getInstance().executeInTransaction(conn -> {
            categoryDao.insert(category);
            writeLog(operatorId, "ADD_CATEGORY", "CATEGORY", category.getId(), "新增分类：" + trimmed);
            return null;
        });
    }

    @Override
    public void toggleCategory(int operatorId, int categoryId, boolean enabled) {
        requireAdmin(operatorId);
        Category category = categoryDao.findById(categoryId)
                .orElseThrow(() -> EntityNotFoundException.of("分类不存在：id=" + categoryId));
        DbUtil.getInstance().executeInTransaction(conn -> {
            categoryDao.updateEnabled(categoryId, enabled);
            writeLog(operatorId, enabled ? "ENABLE_CATEGORY" : "DISABLE_CATEGORY",
                    "CATEGORY", categoryId, (enabled ? "启用分类：" : "停用分类：") + category.getName());
            return null;
        });
    }

    @Override
    public List<OperationLog> recentLogs(int limit) {
        int safeLimit = limit <= 0 ? DEFAULT_RECENT_LIMIT : Math.min(limit, 200);
        return operationLogDao.findRecent(safeLimit);
    }

    private User requireAdmin(int operatorId) throws PermissionDeniedException {
        User operator = userDao.findById(operatorId)
                .orElseThrow(() -> EntityNotFoundException.of("操作用户不存在：id=" + operatorId));
        if (!Role.ADMIN.getCode().equals(operator.getRole())) {
            throw PermissionDeniedException.of("仅管理员可执行该操作");
        }
        return operator;
    }

    private void writeLog(Integer operatorId, String operation, String targetType, Integer targetId, String detail) {
        OperationLog log = new OperationLog();
        log.setOperatorId(operatorId);
        log.setOperation(operation);
        log.setTargetType(targetType);
        log.setTargetId(targetId);
        log.setDetail(detail);
        log.setIp("127.0.0.1");
        log.setCreatedAt(LocalDateTime.now().withNano(0));
        operationLogDao.insert(log);
    }
}
