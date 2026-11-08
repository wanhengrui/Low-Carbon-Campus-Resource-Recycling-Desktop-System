# -*- coding: utf-8 -*-
"""D7 part4b：Service 接口 7 个 + 实现类 7 个 + ServiceFactory（工厂模式装配）。

生成目标：C:\\Users\\wanhe\\Desktop\\软件构造\\迭代一-成员1\\code\\green-campus\\src\\main\\java\\edu\\campus\\recycle
"""
import os

BASE = r"C:\Users\wanhe\Desktop\软件构造\迭代一-成员1\code\green-campus\src\main\java\edu\campus\recycle"
files = {}


def add(rel, text):
    files[rel] = text.lstrip("\n")


# ---------------------------------------------------------------------------
# service 接口（逐字对齐契约 §6）
# ---------------------------------------------------------------------------
add("service/UserService.java", r'''
package edu.campus.recycle.service;

import edu.campus.recycle.dto.LoginResult;
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
}
''')

add("service/ItemService.java", r'''
package edu.campus.recycle.service;

import edu.campus.recycle.dto.ItemQuery;
import edu.campus.recycle.dto.PageResult;
import edu.campus.recycle.entity.Item;
import edu.campus.recycle.exception.BusinessRuleException;
import edu.campus.recycle.exception.EntityNotFoundException;
import edu.campus.recycle.exception.PermissionDeniedException;
import edu.campus.recycle.exception.ValidationException;

import java.util.List;

/**
 * 物品服务：发布（含图片，同一事务）、修改、下架、检索、详情、审核。
 *
 * <p>方法签名逐字对齐《共享契约-实体与接口基线》第 6 节。</p>
 */
public interface ItemService {

    /**
     * 发布物品并批量保存图片（BR-04 信用分门槛、BR-12 图片规则）。
     *
     * @param item       物品实体（ownerId/categoryId/title 必填）
     * @param imagePaths 图片相对路径列表，可为空
     * @return 已回填主键的物品
     */
    Item publish(Item item, List<String> imagePaths) throws ValidationException, BusinessRuleException;

    void updateItem(Item item, int operatorId) throws PermissionDeniedException, EntityNotFoundException;

    void offShelf(int itemId, int operatorId) throws PermissionDeniedException;

    PageResult<Item> search(ItemQuery query);

    Item detail(int itemId) throws EntityNotFoundException;

    void audit(int operatorId, int itemId, boolean pass, String remark) throws PermissionDeniedException;
}
''')

add("service/FavoriteService.java", r'''
package edu.campus.recycle.service;

import edu.campus.recycle.entity.Item;

import java.util.List;

/**
 * 收藏服务（BR-09：同一用户对同一物品收藏为开关式切换）。
 */
public interface FavoriteService {

    /**
     * 收藏/取消收藏，返回切换后的收藏状态。
     *
     * @return {@code true} 表示已收藏，{@code false} 表示已取消
     */
    boolean toggle(int userId, int itemId);

    List<Item> listByUser(int userId);
}
''')

add("service/TradeService.java", r'''
package edu.campus.recycle.service;

import edu.campus.recycle.entity.TradeFlow;
import edu.campus.recycle.exception.BusinessRuleException;
import edu.campus.recycle.exception.EntityNotFoundException;
import edu.campus.recycle.exception.PermissionDeniedException;

import java.util.List;

/**
 * 流转服务：申请 → 同意 → 确认成交 → 取消，及历史查询。
 *
 * <p>方法签名逐字对齐《共享契约-实体与接口基线》第 6 节。</p>
 */
public interface TradeService {

    TradeFlow apply(int itemId, int buyerId, String remark) throws BusinessRuleException, EntityNotFoundException;

    void agree(int flowId, int operatorId) throws PermissionDeniedException, BusinessRuleException;

    /**
     * 确认成交：物品置 SOLD、流转置 DONE、信用分变更、操作日志、统计事件全部在同一事务内完成（BR-07）。
     */
    void confirm(int flowId, int operatorId) throws PermissionDeniedException, BusinessRuleException;

    void cancel(int flowId, int operatorId, String reason) throws PermissionDeniedException;

    List<TradeFlow> history(int userId, String status, int pageNo, int pageSize);
}
''')

add("service/ReviewService.java", r'''
package edu.campus.recycle.service;

import edu.campus.recycle.entity.Review;
import edu.campus.recycle.exception.BusinessRuleException;
import edu.campus.recycle.exception.DuplicateEntityException;

/**
 * 评价服务（BR-08：仅已完成流转可评价，每人每流转一次）。
 */
public interface ReviewService {

    Review review(int flowId, int reviewerId, int score, String content)
            throws BusinessRuleException, DuplicateEntityException;
}
''')

add("service/StatisticService.java", r'''
package edu.campus.recycle.service;

import edu.campus.recycle.dto.StatisticsDTO;

import java.io.IOException;
import java.nio.file.Path;
import java.time.LocalDateTime;
import java.util.List;

/**
 * 统计服务：按分类统计完成流转的笔数、成交金额与碳减排量，并支持导出 CSV。
 */
public interface StatisticService {

    List<StatisticsDTO> statisticsByCategory(LocalDateTime from, LocalDateTime to);

    double carbonReduction(LocalDateTime from, LocalDateTime to);

    String exportCsv(Path target, LocalDateTime from, LocalDateTime to) throws IOException;
}
''')

add("service/AdminService.java", r'''
package edu.campus.recycle.service;

import edu.campus.recycle.entity.OperationLog;
import edu.campus.recycle.exception.DuplicateEntityException;

import java.util.List;

/**
 * 管理服务：两级分类维护与操作日志查询（BR-10 / BR-11）。
 */
public interface AdminService {

    void addCategory(int operatorId, String name, Integer parentId) throws DuplicateEntityException;

    void toggleCategory(int operatorId, int categoryId, boolean enabled);

    List<OperationLog> recentLogs(int limit);
}
''')

# ---------------------------------------------------------------------------
# service.impl
# ---------------------------------------------------------------------------
add("service/impl/UserServiceImpl.java", r'''
package edu.campus.recycle.service.impl;

import edu.campus.recycle.dao.CreditLogDao;
import edu.campus.recycle.dao.OperationLogDao;
import edu.campus.recycle.dao.SystemConfigDao;
import edu.campus.recycle.dao.UserDao;
import edu.campus.recycle.dto.LoginResult;
import edu.campus.recycle.entity.OperationLog;
import edu.campus.recycle.entity.Role;
import edu.campus.recycle.entity.User;
import edu.campus.recycle.entity.UserStatus;
import edu.campus.recycle.exception.AccountLockedException;
import edu.campus.recycle.exception.AuthenticationException;
import edu.campus.recycle.exception.BusinessRuleException;
import edu.campus.recycle.exception.DuplicateEntityException;
import edu.campus.recycle.exception.EntityNotFoundException;
import edu.campus.recycle.exception.PermissionDeniedException;
import edu.campus.recycle.exception.ValidationException;
import edu.campus.recycle.service.UserService;
import edu.campus.recycle.util.CreditRules;
import edu.campus.recycle.util.DbUtil;
import edu.campus.recycle.util.PasswordUtil;
import edu.campus.recycle.util.Validator;

import java.time.Duration;
import java.time.LocalDateTime;
import java.util.List;
import java.util.Objects;
import java.util.logging.Level;
import java.util.logging.Logger;

/**
 * 用户服务实现。
 *
 * <p>集中落地 BR-01（字段规则）、BR-02（PBKDF2 口令哈希，日志与异常不出现明文）、
 * BR-03（连续失败锁定）、BR-04（信用分区间）以及操作日志写入（BR-11）。</p>
 */
public class UserServiceImpl implements UserService {

    private static final Logger LOG = Logger.getLogger(UserServiceImpl.class.getName());

    /** 新用户默认初始信用分。 */
    public static final int DEFAULT_INIT_CREDIT = 100;

    /** 连续登录失败锁定阈值缺省值（BR-03）。 */
    public static final int DEFAULT_MAX_FAIL = 5;

    /** 账号锁定时长（分钟）缺省值（BR-03）。 */
    public static final int DEFAULT_LOCK_MINUTES = 15;

    private final UserDao userDao;
    private final CreditLogDao creditLogDao;
    private final OperationLogDao operationLogDao;
    private final SystemConfigDao systemConfigDao;

    public UserServiceImpl(UserDao userDao, CreditLogDao creditLogDao,
                           OperationLogDao operationLogDao, SystemConfigDao systemConfigDao) {
        this.userDao = Objects.requireNonNull(userDao, "userDao");
        this.creditLogDao = Objects.requireNonNull(creditLogDao, "creditLogDao");
        this.operationLogDao = Objects.requireNonNull(operationLogDao, "operationLogDao");
        this.systemConfigDao = Objects.requireNonNull(systemConfigDao, "systemConfigDao");
    }

    @Override
    public User register(String username, String rawPassword, String realName, String studentNo,
                         String role, String college, String contact)
            throws ValidationException, DuplicateEntityException {
        Validator.checkUsername(username);
        Validator.checkPassword(rawPassword);
        if (realName == null || realName.trim().length() < 2 || realName.trim().length() > 20) {
            throw ValidationException.of("真实姓名长度需为 2-20 个字符");
        }
        String trimmedStudentNo = studentNo == null ? null : studentNo.trim();
        if (trimmedStudentNo != null && trimmedStudentNo.isEmpty()) {
            trimmedStudentNo = null;
        }
        if (trimmedStudentNo != null) {
            Validator.checkStudentNo(trimmedStudentNo);
        }
        String roleCode = normalizeRole(role);
        if (userDao.existsByUsername(username.trim())) {
            throw DuplicateEntityException.of("用户名已被占用：" + username.trim());
        }
        if (trimmedStudentNo != null && userDao.existsByStudentNo(trimmedStudentNo)) {
            throw DuplicateEntityException.of("学号已被注册：" + trimmedStudentNo);
        }
        LocalDateTime now = LocalDateTime.now().withNano(0);
        String salt = PasswordUtil.generateSalt();
        User user = new User();
        user.setUsername(username.trim());
        user.setSalt(salt);
        user.setPasswordHash(PasswordUtil.hash(rawPassword, salt));
        user.setRealName(realName.trim());
        user.setStudentNo(trimmedStudentNo);
        user.setRole(roleCode);
        user.setCollege(trimToNull(college));
        user.setContact(trimToNull(contact));
        user.setCreditScore(systemConfigDao.getInt("credit.init", DEFAULT_INIT_CREDIT));
        user.setStatus(UserStatus.ACTIVE.getCode());
        user.setFailCount(0);
        user.setCreatedAt(now);
        user.setUpdatedAt(now);
        DbUtil.getInstance().executeInTransaction(conn -> {
            userDao.insert(user);
            writeLog(user.getId(), "REGISTER", "USER", user.getId(), "注册账号：" + user.getUsername());
            return null;
        });
        LOG.info(() -> "注册成功：userId=" + user.getId() + "，username=" + user.getUsername());
        return user;
    }

    @Override
    public LoginResult login(String username, String rawPassword)
            throws AuthenticationException, AccountLockedException {
        if (username == null || username.trim().isEmpty() || rawPassword == null) {
            throw AuthenticationException.of("用户名或密码错误");
        }
        User user = userDao.findByUsername(username.trim())
                .orElseThrow(() -> AuthenticationException.of("用户名或密码错误"));
        LocalDateTime now = LocalDateTime.now().withNano(0);
        if (user.getLockedUntil() != null && user.getLockedUntil().isAfter(now)) {
            long remainMinutes = Math.max(1L, Duration.between(now, user.getLockedUntil()).toMinutes() + 1L);
            throw AccountLockedException.of("账号已锁定，请 " + remainMinutes + " 分钟后再试");
        }
        if (!UserStatus.ACTIVE.getCode().equals(user.getStatus())) {
            throw AuthenticationException.of("账号状态异常（" + user.getStatus() + "），请联系管理员");
        }
        if (!PasswordUtil.verify(rawPassword, user.getSalt(), user.getPasswordHash())) {
            int maxFail = systemConfigDao.getInt("login.max_fail", DEFAULT_MAX_FAIL);
            int failCount = (user.getFailCount() == null ? 0 : user.getFailCount()) + 1;
            LocalDateTime lockedUntil = null;
            if (failCount >= maxFail) {
                int lockMinutes = systemConfigDao.getInt("login.lock_minutes", DEFAULT_LOCK_MINUTES);
                lockedUntil = now.plusMinutes(lockMinutes);
            }
            userDao.updateFailCount(user.getId(), failCount, lockedUntil);
            if (lockedUntil != null) {
                LOG.warning(() -> "账号锁定：userId=" + user.getId() + "，失败次数=" + failCount);
                throw AccountLockedException.of("连续 " + failCount + " 次密码错误，账号已锁定，请稍后再试");
            }
            throw AuthenticationException.of("用户名或密码错误，剩余尝试次数：" + (maxFail - failCount));
        }
        userDao.updateLoginSuccess(user.getId(), now);
        user.setFailCount(0);
        user.setLockedUntil(null);
        user.setLastLoginAt(now);
        writeLog(user.getId(), "LOGIN", "USER", user.getId(), "登录成功");
        return LoginResult.ofSuccess(user, now);
    }

    @Override
    public void changePassword(int userId, String oldPwd, String newPwd)
            throws AuthenticationException, ValidationException {
        User user = userDao.findById(userId)
                .orElseThrow(() -> EntityNotFoundException.of("用户不存在：id=" + userId));
        if (!PasswordUtil.verify(oldPwd, user.getSalt(), user.getPasswordHash())) {
            throw AuthenticationException.of("原密码不正确");
        }
        Validator.checkPassword(newPwd);
        if (oldPwd != null && oldPwd.equals(newPwd)) {
            throw ValidationException.of("新密码不能与原密码相同");
        }
        String salt = PasswordUtil.generateSalt();
        user.setSalt(salt);
        user.setPasswordHash(PasswordUtil.hash(newPwd, salt));
        user.setUpdatedAt(LocalDateTime.now().withNano(0));
        DbUtil.getInstance().executeInTransaction(conn -> {
            userDao.update(user);
            writeLog(userId, "CHANGE_PASSWORD", "USER", userId, "修改密码");
            return null;
        });
    }

    @Override
    public User findById(int userId) throws EntityNotFoundException {
        return userDao.findById(userId)
                .orElseThrow(() -> EntityNotFoundException.of("用户不存在：id=" + userId));
    }

    @Override
    public List<User> queryUsers(String keyword, String role, int pageNo, int pageSize) {
        int safePage = Math.max(1, pageNo);
        int safeSize = Math.min(Math.max(1, pageSize), 100);
        return userDao.findByCondition(keyword, role, safePage, safeSize);
    }

    @Override
    public void freezeUser(int operatorId, int userId) throws PermissionDeniedException, BusinessRuleException {
        requireAdmin(operatorId);
        User target = findById(userId);
        if (Role.ADMIN.getCode().equals(target.getRole())) {
            throw BusinessRuleException.of("BR-10", "管理员账号不可冻结");
        }
        if (UserStatus.FROZEN.getCode().equals(target.getStatus())) {
            return;
        }
        DbUtil.getInstance().executeInTransaction(conn -> {
            userDao.updateStatus(userId, UserStatus.FROZEN.getCode());
            writeLog(operatorId, "FREEZE_USER", "USER", userId, "冻结用户：" + target.getUsername());
            return null;
        });
    }

    @Override
    public void unfreezeUser(int operatorId, int userId) throws PermissionDeniedException {
        requireAdmin(operatorId);
        User target = findById(userId);
        if (UserStatus.ACTIVE.getCode().equals(target.getStatus())) {
            return;
        }
        DbUtil.getInstance().executeInTransaction(conn -> {
            userDao.updateStatus(userId, UserStatus.ACTIVE.getCode());
            writeLog(operatorId, "UNFREEZE_USER", "USER", userId, "解冻用户：" + target.getUsername());
            return null;
        });
    }

    @Override
    public void updateCredit(int userId, int delta, Integer flowId, String reason) throws BusinessRuleException {
        if (reason == null || reason.trim().isEmpty()) {
            throw BusinessRuleException.of("BR-04", "信用分变更原因不能为空");
        }
        findById(userId);
        DbUtil.getInstance().executeInTransaction(
                conn -> CreditRules.apply(userDao, creditLogDao, userId, delta, flowId, reason.trim()));
    }

    /**
     * 管理员权限校验。
     */
    private User requireAdmin(int operatorId) throws PermissionDeniedException {
        User operator = userDao.findById(operatorId)
                .orElseThrow(() -> EntityNotFoundException.of("操作用户不存在：id=" + operatorId));
        if (!Role.ADMIN.getCode().equals(operator.getRole())) {
            throw PermissionDeniedException.of("仅管理员可执行该操作");
        }
        return operator;
    }

    /**
     * 追加操作日志（BR-11 只追加）；日志失败不阻断主流程。
     */
    private void writeLog(Integer operatorId, String operation, String targetType, Integer targetId, String detail) {
        try {
            OperationLog log = new OperationLog();
            log.setOperatorId(operatorId);
            log.setOperation(operation);
            log.setTargetType(targetType);
            log.setTargetId(targetId);
            log.setDetail(detail);
            log.setIp("127.0.0.1");
            log.setCreatedAt(LocalDateTime.now().withNano(0));
            operationLogDao.insert(log);
        } catch (RuntimeException e) {
            LOG.log(Level.WARNING, "写操作日志失败（不影响主流程）：" + operation, e);
        }
    }

    private String normalizeRole(String role) {
        String code = role == null || role.trim().isEmpty()
                ? Role.STUDENT.getCode() : role.trim().toUpperCase();
        for (Role item : Role.values()) {
            if (item.getCode().equals(code)) {
                return code;
            }
        }
        throw ValidationException.of("非法的角色编码：" + role);
    }

    private String trimToNull(String value) {
        if (value == null) {
            return null;
        }
        String trimmed = value.trim();
        return trimmed.isEmpty() ? null : trimmed;
    }
}
''')

add("service/impl/ItemServiceImpl.java", r'''
package edu.campus.recycle.service.impl;

import edu.campus.recycle.dao.CategoryDao;
import edu.campus.recycle.dao.ItemDao;
import edu.campus.recycle.dao.ItemImageDao;
import edu.campus.recycle.dao.SystemConfigDao;
import edu.campus.recycle.dao.TradeFlowDao;
import edu.campus.recycle.dao.UserDao;
import edu.campus.recycle.dto.ItemQuery;
import edu.campus.recycle.dto.PageResult;
import edu.campus.recycle.entity.Category;
import edu.campus.recycle.entity.FlowStatus;
import edu.campus.recycle.entity.Item;
import edu.campus.recycle.entity.ItemImage;
import edu.campus.recycle.entity.ItemStatus;
import edu.campus.recycle.entity.Role;
import edu.campus.recycle.entity.TradeFlow;
import edu.campus.recycle.entity.TradeType;
import edu.campus.recycle.entity.User;
import edu.campus.recycle.exception.BusinessRuleException;
import edu.campus.recycle.exception.EntityNotFoundException;
import edu.campus.recycle.exception.PermissionDeniedException;
import edu.campus.recycle.exception.ValidationException;
import edu.campus.recycle.service.ItemService;
import edu.campus.recycle.util.DbUtil;
import edu.campus.recycle.util.ItemEvent;
import edu.campus.recycle.util.ItemEventBus;
import edu.campus.recycle.util.Validator;

import java.math.BigDecimal;
import java.time.LocalDateTime;
import java.util.ArrayList;
import java.util.List;
import java.util.Locale;
import java.util.Objects;
import java.util.logging.Logger;

/**
 * 物品服务实现。
 *
 * <p>发布物品与图片在同一事务内完成（BR-12 图片规则、BR-04 信用分门槛）；下架与审核
 * 保留操作痕迹并通过观察者写入操作日志。</p>
 */
public class ItemServiceImpl implements ItemService {

    private static final Logger LOG = Logger.getLogger(ItemServiceImpl.class.getName());

    /** 物品描述最大长度。 */
    public static final int DESCRIPTION_MAX = 500;

    private final ItemDao itemDao;
    private final ItemImageDao itemImageDao;
    private final CategoryDao categoryDao;
    private final UserDao userDao;
    private final TradeFlowDao tradeFlowDao;
    private final SystemConfigDao systemConfigDao;

    public ItemServiceImpl(ItemDao itemDao, ItemImageDao itemImageDao, CategoryDao categoryDao,
                           UserDao userDao, TradeFlowDao tradeFlowDao, SystemConfigDao systemConfigDao) {
        this.itemDao = Objects.requireNonNull(itemDao, "itemDao");
        this.itemImageDao = Objects.requireNonNull(itemImageDao, "itemImageDao");
        this.categoryDao = Objects.requireNonNull(categoryDao, "categoryDao");
        this.userDao = Objects.requireNonNull(userDao, "userDao");
        this.tradeFlowDao = Objects.requireNonNull(tradeFlowDao, "tradeFlowDao");
        this.systemConfigDao = Objects.requireNonNull(systemConfigDao, "systemConfigDao");
    }

    @Override
    public Item publish(Item item, List<String> imagePaths)
            throws ValidationException, BusinessRuleException {
        if (item == null) {
            throw ValidationException.of("物品信息不能为空");
        }
        Validator.checkTitle(item.getTitle());
        if (item.getDescription() != null && item.getDescription().length() > DESCRIPTION_MAX) {
            throw ValidationException.of("物品描述不能超过 " + DESCRIPTION_MAX + " 字");
        }
        List<String> paths = normalizeImages(imagePaths);
        if (item.getOwnerId() == null) {
            throw ValidationException.of("发布者不能为空");
        }
        User owner = userDao.findById(item.getOwnerId())
                .orElseThrow(() -> EntityNotFoundException.of("发布者不存在：id=" + item.getOwnerId()));
        int minCredit = systemConfigDao.getInt("credit.min_publish", 60);
        if (owner.getCreditScore() != null && owner.getCreditScore() < minCredit) {
            throw BusinessRuleException.of("BR-04",
                    "信用分低于 " + minCredit + "，暂不可发布物品（当前 " + owner.getCreditScore() + "）");
        }
        if (item.getCategoryId() == null) {
            throw ValidationException.of("请选择物品分类");
        }
        Category category = categoryDao.findById(item.getCategoryId())
                .orElseThrow(() -> EntityNotFoundException.of("分类不存在：id=" + item.getCategoryId()));
        if (!Boolean.TRUE.equals(category.getEnabled())) {
            throw BusinessRuleException.of("BR-06", "分类已停用，暂不可发布：" + category.getName());
        }
        if (item.getTradeType() == null || item.getTradeType().trim().isEmpty()) {
            item.setTradeType(TradeType.SELL.getCode());
        }
        if (item.getPrice() == null) {
            item.setPrice(BigDecimal.ZERO);
        }
        if (item.getPrice().signum() < 0) {
            throw ValidationException.of("价格不能为负数");
        }
        String status = item.getStatus() == null || item.getStatus().trim().isEmpty()
                ? ItemStatus.ON_SALE.getCode() : item.getStatus();
        LocalDateTime now = LocalDateTime.now().withNano(0);
        item.setStatus(status);
        item.setCreatedAt(now);
        item.setUpdatedAt(now);
        item.setPublishedAt(ItemStatus.ON_SALE.getCode().equals(status) ? now : null);
        item.setViewCount(0);
        item.setFavoriteCount(0);
        DbUtil.getInstance().executeInTransaction(conn -> {
            itemDao.insert(item);
            if (!paths.isEmpty()) {
                List<ItemImage> images = new ArrayList<>(paths.size());
                for (int i = 0; i < paths.size(); i++) {
                    ItemImage image = new ItemImage();
                    image.setItemId(item.getId());
                    image.setFilePath(paths.get(i));
                    image.setSortOrder(i);
                    image.setCreatedAt(now);
                    images.add(image);
                }
                itemImageDao.batchInsert(images);
            }
            ItemEventBus.getInstance().publish(
                    ItemEvent.item(ItemEvent.Type.ITEM_PUBLISHED, item, item.getOwnerId(), "发布物品：" + item.getTitle()));
            return null;
        });
        LOG.info(() -> "物品发布成功：itemId=" + item.getId() + "，图片 " + paths.size() + " 张");
        return item;
    }

    @Override
    public void updateItem(Item item, int operatorId) throws PermissionDeniedException, EntityNotFoundException {
        if (item == null || item.getId() == null) {
            throw ValidationException.of("待更新物品不能为空");
        }
        Item existing = itemDao.findById(item.getId())
                .orElseThrow(() -> EntityNotFoundException.of("物品不存在：id=" + item.getId()));
        boolean admin = isAdmin(operatorId);
        if (!admin && !Objects.equals(existing.getOwnerId(), operatorId)) {
            throw PermissionDeniedException.of("仅物品发布者或管理员可修改该物品");
        }
        Validator.checkTitle(item.getTitle());
        if (item.getDescription() != null && item.getDescription().length() > DESCRIPTION_MAX) {
            throw ValidationException.of("物品描述不能超过 " + DESCRIPTION_MAX + " 字");
        }
        item.setId(existing.getId());
        item.setOwnerId(existing.getOwnerId());
        item.setStatus(existing.getStatus());
        item.setPublishedAt(existing.getPublishedAt());
        item.setViewCount(existing.getViewCount());
        item.setFavoriteCount(existing.getFavoriteCount());
        item.setUpdatedAt(LocalDateTime.now().withNano(0));
        itemDao.update(item);
    }

    @Override
    public void offShelf(int itemId, int operatorId) throws PermissionDeniedException {
        Item item = itemDao.findById(itemId)
                .orElseThrow(() -> EntityNotFoundException.of("物品不存在：id=" + itemId));
        boolean admin = isAdmin(operatorId);
        if (!admin && !Objects.equals(item.getOwnerId(), operatorId)) {
            throw PermissionDeniedException.of("仅物品发布者或管理员可下架该物品");
        }
        if (ItemStatus.SOLD.getCode().equals(item.getStatus())
                || ItemStatus.OFF_SHELF.getCode().equals(item.getStatus())) {
            throw BusinessRuleException.of("BR-10", "当前状态不可下架：" + item.getStatus());
        }
        LocalDateTime now = LocalDateTime.now().withNano(0);
        DbUtil.getInstance().executeInTransaction(conn -> {
            tradeFlowDao.findActiveByItemId(itemId).ifPresent(flow ->
                    tradeFlowDao.updateStatus(flow.getId(), FlowStatus.CANCELLED.getCode(), "物品下架自动取消", now));
            itemDao.updateStatus(itemId, ItemStatus.OFF_SHELF.getCode(), "操作人下架");
            ItemEventBus.getInstance().publish(
                    ItemEvent.of(ItemEvent.Type.ITEM_OFF_SHELF, itemId, null, operatorId, "下架物品：" + item.getTitle()));
            return null;
        });
    }

    @Override
    public PageResult<Item> search(ItemQuery query) {
        ItemQuery effective = query == null ? new ItemQuery() : query;
        List<Item> records = itemDao.search(effective);
        long total = itemDao.countSearch(effective);
        return PageResult.of(records, total, Math.max(1, effective.getPageNo()), Math.max(1, effective.getPageSize()));
    }

    @Override
    public Item detail(int itemId) throws EntityNotFoundException {
        Item item = itemDao.findById(itemId)
                .orElseThrow(() -> EntityNotFoundException.of("物品不存在：id=" + itemId));
        itemDao.increaseViewCount(itemId);
        item.setViewCount((item.getViewCount() == null ? 0 : item.getViewCount()) + 1);
        return item;
    }

    @Override
    public void audit(int operatorId, int itemId, boolean pass, String remark) throws PermissionDeniedException {
        requireAdmin(operatorId);
        Item item = itemDao.findById(itemId)
                .orElseThrow(() -> EntityNotFoundException.of("物品不存在：id=" + itemId));
        if (ItemStatus.SOLD.getCode().equals(item.getStatus())) {
            throw BusinessRuleException.of("BR-10", "已成交物品不可再审核");
        }
        if (!ItemStatus.PENDING.getCode().equals(item.getStatus())
                && !ItemStatus.DRAFT.getCode().equals(item.getStatus())) {
            throw BusinessRuleException.of("BR-10", "仅待审核状态可审核，当前：" + item.getStatus());
        }
        LocalDateTime now = LocalDateTime.now().withNano(0);
        DbUtil.getInstance().executeInTransaction(conn -> {
            if (pass) {
                item.setStatus(ItemStatus.ON_SALE.getCode());
                item.setAuditRemark(remark);
                item.setUpdatedAt(now);
                if (item.getPublishedAt() == null) {
                    item.setPublishedAt(now);
                }
                itemDao.update(item);
            } else {
                itemDao.updateStatus(itemId, ItemStatus.REJECTED.getCode(), remark);
            }
            ItemEventBus.getInstance().publish(
                    ItemEvent.of(ItemEvent.Type.ITEM_AUDITED, itemId, null, operatorId,
                            (pass ? "审核通过：" : "审核驳回：") + item.getTitle()));
            return null;
        });
    }

    /**
     * 图片路径规整与后缀/数量校验（BR-12）。
     */
    private List<String> normalizeImages(List<String> imagePaths) {
        List<String> paths = new ArrayList<>();
        if (imagePaths != null) {
            for (String path : imagePaths) {
                if (path != null && !path.trim().isEmpty()) {
                    paths.add(path.trim());
                }
            }
        }
        if (paths.size() > Validator.MAX_IMAGE_COUNT) {
            throw ValidationException.of("图片最多上传 " + Validator.MAX_IMAGE_COUNT + " 张");
        }
        for (String path : paths) {
            String lower = path.toLowerCase(Locale.ROOT);
            if (!lower.endsWith(".jpg") && !lower.endsWith(".jpeg") && !lower.endsWith(".png")) {
                throw ValidationException.of("仅支持 jpg/jpeg/png 格式的图片：" + path);
            }
        }
        return paths;
    }

    private boolean isAdmin(int operatorId) {
        return userDao.findById(operatorId).map(u -> Role.ADMIN.getCode().equals(u.getRole())).orElse(false);
    }

    private User requireAdmin(int operatorId) throws PermissionDeniedException {
        User operator = userDao.findById(operatorId)
                .orElseThrow(() -> EntityNotFoundException.of("操作用户不存在：id=" + operatorId));
        if (!Role.ADMIN.getCode().equals(operator.getRole())) {
            throw PermissionDeniedException.of("仅管理员可执行该操作");
        }
        return operator;
    }
}
''')

add("service/impl/FavoriteServiceImpl.java", r'''
package edu.campus.recycle.service.impl;

import edu.campus.recycle.dao.FavoriteDao;
import edu.campus.recycle.dao.ItemDao;
import edu.campus.recycle.entity.Favorite;
import edu.campus.recycle.entity.Item;
import edu.campus.recycle.exception.EntityNotFoundException;
import edu.campus.recycle.service.FavoriteService;
import edu.campus.recycle.util.DbUtil;

import java.time.LocalDateTime;
import java.util.List;
import java.util.Objects;

/**
 * 收藏服务实现：toggle 采用「同一事务内判断存在性 + 插入/删除 + 计数维护」，
 * 避免并发下重复收藏（BR-09）。
 */
public class FavoriteServiceImpl implements FavoriteService {

    private final FavoriteDao favoriteDao;
    private final ItemDao itemDao;

    public FavoriteServiceImpl(FavoriteDao favoriteDao, ItemDao itemDao) {
        this.favoriteDao = Objects.requireNonNull(favoriteDao, "favoriteDao");
        this.itemDao = Objects.requireNonNull(itemDao, "itemDao");
    }

    @Override
    public boolean toggle(int userId, int itemId) {
        itemDao.findById(itemId)
                .orElseThrow(() -> EntityNotFoundException.of("物品不存在：id=" + itemId));
        return DbUtil.getInstance().executeInTransaction(conn -> {
            if (favoriteDao.exists(userId, itemId)) {
                favoriteDao.delete(userId, itemId);
                itemDao.increaseFavoriteCount(itemId, -1);
                return Boolean.FALSE;
            }
            Favorite favorite = new Favorite();
            favorite.setUserId(userId);
            favorite.setItemId(itemId);
            favorite.setCreatedAt(LocalDateTime.now().withNano(0));
            favoriteDao.insert(favorite);
            itemDao.increaseFavoriteCount(itemId, 1);
            return Boolean.TRUE;
        });
    }

    @Override
    public List<Item> listByUser(int userId) {
        return favoriteDao.findItemsByUserId(userId);
    }
}
''')

add("service/impl/TradeServiceImpl.java", r'''
package edu.campus.recycle.service.impl;

import edu.campus.recycle.dao.ItemDao;
import edu.campus.recycle.dao.TradeFlowDao;
import edu.campus.recycle.dao.UserDao;
import edu.campus.recycle.entity.FlowStatus;
import edu.campus.recycle.entity.Item;
import edu.campus.recycle.entity.ItemStatus;
import edu.campus.recycle.entity.TradeFlow;
import edu.campus.recycle.entity.TradeType;
import edu.campus.recycle.entity.User;
import edu.campus.recycle.entity.UserStatus;
import edu.campus.recycle.exception.BusinessRuleException;
import edu.campus.recycle.exception.EntityNotFoundException;
import edu.campus.recycle.exception.PermissionDeniedException;
import edu.campus.recycle.service.TradeService;
import edu.campus.recycle.util.DbUtil;
import edu.campus.recycle.util.ItemEvent;
import edu.campus.recycle.util.ItemEventBus;

import java.math.BigDecimal;
import java.time.LocalDateTime;
import java.util.List;
import java.util.Objects;
import java.util.logging.Logger;

/**
 * 流转服务实现。
 *
 * <p>核心 {@link #confirm(int, int)} 在一个事务内完成：物品置 SOLD、流转置 DONE、
 * 信用分变更（观察者）、操作日志（观察者）、统计累加（观察者）；任一步失败整体回滚（BR-07）。</p>
 */
public class TradeServiceImpl implements TradeService {

    private static final Logger LOG = Logger.getLogger(TradeServiceImpl.class.getName());

    private final TradeFlowDao tradeFlowDao;
    private final ItemDao itemDao;
    private final UserDao userDao;

    public TradeServiceImpl(TradeFlowDao tradeFlowDao, ItemDao itemDao, UserDao userDao) {
        this.tradeFlowDao = Objects.requireNonNull(tradeFlowDao, "tradeFlowDao");
        this.itemDao = Objects.requireNonNull(itemDao, "itemDao");
        this.userDao = Objects.requireNonNull(userDao, "userDao");
    }

    @Override
    public TradeFlow apply(int itemId, int buyerId, String remark)
            throws BusinessRuleException, EntityNotFoundException {
        Item item = itemDao.findById(itemId)
                .orElseThrow(() -> EntityNotFoundException.of("物品不存在：id=" + itemId));
        if (Objects.equals(item.getOwnerId(), buyerId)) {
            throw BusinessRuleException.of("BR-06", "不能申请自己发布的物品");
        }
        if (!ItemStatus.ON_SALE.getCode().equals(item.getStatus())) {
            throw BusinessRuleException.of("BR-06", "仅「在售」物品可发起流转申请，当前：" + item.getStatus());
        }
        User buyer = userDao.findById(buyerId)
                .orElseThrow(() -> EntityNotFoundException.of("申请用户不存在：id=" + buyerId));
        if (!UserStatus.ACTIVE.getCode().equals(buyer.getStatus())) {
            throw BusinessRuleException.of("BR-06", "账号状态异常，无法发起流转");
        }
        if (tradeFlowDao.findActiveByItemId(itemId).isPresent()) {
            throw BusinessRuleException.of("BR-05", "该物品已有进行中的流转，不可重复申请");
        }
        LocalDateTime now = LocalDateTime.now().withNano(0);
        TradeFlow flow = new TradeFlow();
        flow.setItemId(itemId);
        flow.setSellerId(item.getOwnerId());
        flow.setBuyerId(buyerId);
        flow.setFlowType(item.getTradeType());
        flow.setAmount(TradeType.SELL.getCode().equals(item.getTradeType())
                ? (item.getPrice() == null ? BigDecimal.ZERO : item.getPrice()) : BigDecimal.ZERO);
        flow.setStatus(FlowStatus.APPLYING.getCode());
        flow.setApplyRemark(remark);
        flow.setCreatedAt(now);
        DbUtil.getInstance().executeInTransaction(conn -> {
            tradeFlowDao.insert(flow);
            ItemEventBus.getInstance().publish(
                    ItemEvent.of(ItemEvent.Type.FLOW_APPLIED, itemId, flow.getId(), buyerId, "发起流转申请"));
            return null;
        });
        LOG.info(() -> "流转申请成功：flowId=" + flow.getId() + "，itemId=" + itemId);
        return flow;
    }

    @Override
    public void agree(int flowId, int operatorId) throws PermissionDeniedException, BusinessRuleException {
        TradeFlow flow = tradeFlowDao.findById(flowId)
                .orElseThrow(() -> EntityNotFoundException.of("流转记录不存在：id=" + flowId));
        if (!Objects.equals(flow.getSellerId(), operatorId)) {
            throw PermissionDeniedException.of("仅物品发布者可同意该流转申请");
        }
        if (!FlowStatus.APPLYING.getCode().equals(flow.getStatus())) {
            throw BusinessRuleException.of("BR-06", "仅「申请中」的流转可同意，当前：" + flow.getStatus());
        }
        DbUtil.getInstance().executeInTransaction(conn -> {
            tradeFlowDao.updateStatus(flowId, FlowStatus.AGREED.getCode(), null, null);
            itemDao.updateStatus(flow.getItemId(), ItemStatus.LOCKED.getCode(), null);
            ItemEventBus.getInstance().publish(
                    ItemEvent.flow(ItemEvent.Type.FLOW_AGREED, flow, operatorId, "同意流转申请"));
            return null;
        });
    }

    @Override
    public void confirm(int flowId, int operatorId) throws PermissionDeniedException, BusinessRuleException {
        DbUtil.getInstance().executeInTransaction(conn -> {
            TradeFlow flow = tradeFlowDao.findById(flowId)
                    .orElseThrow(() -> EntityNotFoundException.of("流转记录不存在：id=" + flowId));
            if (!Objects.equals(flow.getSellerId(), operatorId) && !Objects.equals(flow.getBuyerId(), operatorId)) {
                throw PermissionDeniedException.of("仅交易双方可确认成交");
            }
            if (!FlowStatus.AGREED.getCode().equals(flow.getStatus())) {
                throw BusinessRuleException.of("BR-06", "仅「已同意」的流转可确认成交，当前：" + flow.getStatus());
            }
            Item item = itemDao.findById(flow.getItemId())
                    .orElseThrow(() -> EntityNotFoundException.of("物品不存在：id=" + flow.getItemId()));
            if (ItemStatus.SOLD.getCode().equals(item.getStatus())) {
                throw BusinessRuleException.of("BR-05", "该物品已成交，不可重复成交");
            }
            LocalDateTime now = LocalDateTime.now().withNano(0);
            itemDao.updateStatus(flow.getItemId(), ItemStatus.SOLD.getCode(), null);
            tradeFlowDao.updateStatus(flowId, FlowStatus.DONE.getCode(), null, now);
            ItemEventBus.getInstance().publish(
                    ItemEvent.flow(ItemEvent.Type.FLOW_DONE, flow, operatorId, "确认成交"));
            LOG.info(() -> "确认成交成功：flowId=" + flowId + "，itemId=" + flow.getItemId());
            return null;
        });
    }

    @Override
    public void cancel(int flowId, int operatorId, String reason) throws PermissionDeniedException {
        TradeFlow flow = tradeFlowDao.findById(flowId)
                .orElseThrow(() -> EntityNotFoundException.of("流转记录不存在：id=" + flowId));
        boolean participant = Objects.equals(flow.getSellerId(), operatorId)
                || Objects.equals(flow.getBuyerId(), operatorId);
        if (!participant) {
            throw PermissionDeniedException.of("仅交易双方可取消该流转");
        }
        if (!FlowStatus.APPLYING.getCode().equals(flow.getStatus())
                && !FlowStatus.AGREED.getCode().equals(flow.getStatus())) {
            throw BusinessRuleException.of("BR-06", "仅进行中的流转可取消，当前：" + flow.getStatus());
        }
        if (reason == null || reason.trim().isEmpty()) {
            throw BusinessRuleException.of("BR-06", "取消原因不能为空");
        }
        LocalDateTime now = LocalDateTime.now().withNano(0);
        DbUtil.getInstance().executeInTransaction(conn -> {
            tradeFlowDao.updateStatus(flowId, FlowStatus.CANCELLED.getCode(), reason.trim(), now);
            if (FlowStatus.AGREED.getCode().equals(flow.getStatus())) {
                itemDao.updateStatus(flow.getItemId(), ItemStatus.ON_SALE.getCode(), null);
            }
            ItemEventBus.getInstance().publish(
                    ItemEvent.flow(ItemEvent.Type.FLOW_CANCELLED, flow, operatorId, "取消流转：" + reason.trim()));
            return null;
        });
    }

    @Override
    public List<TradeFlow> history(int userId, String status, int pageNo, int pageSize) {
        int safePage = Math.max(1, pageNo);
        int safeSize = Math.min(Math.max(1, pageSize), 100);
        return tradeFlowDao.findByUserId(userId, status, safePage, safeSize);
    }
}
''')

add("service/impl/ReviewServiceImpl.java", r'''
package edu.campus.recycle.service.impl;

import edu.campus.recycle.dao.CreditLogDao;
import edu.campus.recycle.dao.ReviewDao;
import edu.campus.recycle.dao.SystemConfigDao;
import edu.campus.recycle.dao.TradeFlowDao;
import edu.campus.recycle.dao.UserDao;
import edu.campus.recycle.entity.FlowStatus;
import edu.campus.recycle.entity.Review;
import edu.campus.recycle.entity.TradeFlow;
import edu.campus.recycle.exception.BusinessRuleException;
import edu.campus.recycle.exception.DuplicateEntityException;
import edu.campus.recycle.exception.EntityNotFoundException;
import edu.campus.recycle.exception.PermissionDeniedException;
import edu.campus.recycle.exception.ValidationException;
import edu.campus.recycle.service.ReviewService;
import edu.campus.recycle.util.CreditRules;
import edu.campus.recycle.util.DbUtil;
import edu.campus.recycle.util.ItemEvent;
import edu.campus.recycle.util.ItemEventBus;

import java.time.LocalDateTime;
import java.util.Objects;

/**
 * 评价服务实现：评价落库与对方信用分调整在同一事务内完成（BR-07 / BR-08）。
 */
public class ReviewServiceImpl implements ReviewService {

    private static final LoggerGuard GUARD = new LoggerGuard();

    private final ReviewDao reviewDao;
    private final TradeFlowDao tradeFlowDao;
    private final UserDao userDao;
    private final CreditLogDao creditLogDao;
    private final SystemConfigDao systemConfigDao;

    public ReviewServiceImpl(ReviewDao reviewDao, TradeFlowDao tradeFlowDao, UserDao userDao,
                             CreditLogDao creditLogDao, SystemConfigDao systemConfigDao) {
        this.reviewDao = Objects.requireNonNull(reviewDao, "reviewDao");
        this.tradeFlowDao = Objects.requireNonNull(tradeFlowDao, "tradeFlowDao");
        this.userDao = Objects.requireNonNull(userDao, "userDao");
        this.creditLogDao = Objects.requireNonNull(creditLogDao, "creditLogDao");
        this.systemConfigDao = Objects.requireNonNull(systemConfigDao, "systemConfigDao");
    }

    @Override
    public Review review(int flowId, int reviewerId, int score, String content)
            throws BusinessRuleException, DuplicateEntityException {
        if (score < 1 || score > 5) {
            throw ValidationException.of("评分必须为 1-5 分");
        }
        if (content != null && content.length() > 200) {
            throw ValidationException.of("评价内容不能超过 200 字");
        }
        TradeFlow flow = tradeFlowDao.findById(flowId)
                .orElseThrow(() -> EntityNotFoundException.of("流转记录不存在：id=" + flowId));
        if (!FlowStatus.DONE.getCode().equals(flow.getStatus())) {
            throw BusinessRuleException.of("BR-08", "仅已完成的流转可评价");
        }
        boolean participant = Objects.equals(flow.getSellerId(), reviewerId)
                || Objects.equals(flow.getBuyerId(), reviewerId);
        if (!participant) {
            throw PermissionDeniedException.of("仅交易双方可评价该流转");
        }
        if (reviewDao.existsByFlowAndReviewer(flowId, reviewerId)) {
            throw DuplicateEntityException.of("您已评价过该笔流转，不可重复评价");
        }
        int revieweeId = Objects.equals(flow.getSellerId(), reviewerId)
                ? flow.getBuyerId() : flow.getSellerId();
        Review review = new Review();
        review.setFlowId(flowId);
        review.setReviewerId(reviewerId);
        review.setRevieweeId(revieweeId);
        review.setScore(score);
        review.setContent(content == null ? "" : content.trim());
        review.setCreatedAt(LocalDateTime.now().withNano(0));
        int delta = creditDelta(score);
        DbUtil.getInstance().executeInTransaction(conn -> {
            reviewDao.insert(review);
            if (delta != 0) {
                CreditRules.apply(userDao, creditLogDao, revieweeId, delta, flowId,
                        "收到评价（" + score + " 分）信用分调整");
            }
            ItemEventBus.getInstance().publish(
                    ItemEvent.of(ItemEvent.Type.REVIEW_CREATED, flow.getItemId(), flowId, reviewerId,
                            "评价 " + score + " 分"));
            return null;
        });
        GUARD.info(() -> "评价成功：flowId=" + flowId + "，reviewerId=" + reviewerId + "，score=" + score);
        return review;
    }

    /**
     * 评价信用分规则：4-5 分奖励（credit.trade_bonus），1-2 分惩罚（credit.bad_review_penalty），3 分不变。
     */
    private int creditDelta(int score) {
        if (score >= 4) {
            return systemConfigDao.getInt("credit.trade_bonus", 2);
        }
        if (score <= 2) {
            return systemConfigDao.getInt("credit.bad_review_penalty", -5);
        }
        return 0;
    }

    /**
     * 轻量日志持有者（避免静态 Logger 字段与 checkstyle 冲突的占位实现）。
     */
    private static final class LoggerGuard {
        private final java.util.logging.Logger logger =
                java.util.logging.Logger.getLogger(ReviewServiceImpl.class.getName());

        void info(java.util.function.Supplier<String> message) {
            logger.info(message);
        }
    }
}
''')

add("service/impl/StatisticServiceImpl.java", r'''
package edu.campus.recycle.service.impl;

import edu.campus.recycle.dao.CategoryDao;
import edu.campus.recycle.dao.SystemConfigDao;
import edu.campus.recycle.dao.TradeFlowDao;
import edu.campus.recycle.dto.StatisticsDTO;
import edu.campus.recycle.entity.Category;
import edu.campus.recycle.service.StatisticService;
import edu.campus.recycle.util.CarbonFactorStrategy;
import edu.campus.recycle.util.CsvExporter;

import java.io.IOException;
import java.math.BigDecimal;
import java.math.RoundingMode;
import java.nio.file.Path;
import java.time.LocalDateTime;
import java.util.ArrayList;
import java.util.Comparator;
import java.util.HashMap;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;
import java.util.Objects;

/**
 * 统计服务实现：按一级分类聚合完成流转的笔数/金额，并按 system_config 中的
 * carbon.factor.* 系数折算碳减排量；策略模式 {@link CarbonFactorStrategy} 提供缺省系数回退。
 */
public class StatisticServiceImpl implements StatisticService {

    /** 一级分类名称 → system_config 中碳减排系数键。 */
    private static final Map<String, String> FACTOR_KEYS = Map.of(
            "教材书籍", "carbon.factor.book",
            "数码配件", "carbon.factor.electronics",
            "文体用品", "carbon.factor.sports",
            "生活物资", "carbon.factor.daily");

    private final TradeFlowDao tradeFlowDao;
    private final CategoryDao categoryDao;
    private final SystemConfigDao systemConfigDao;
    private final CarbonFactorStrategy carbonFactorStrategy;
    private final CsvExporter csvExporter = new CsvExporter();

    public StatisticServiceImpl(TradeFlowDao tradeFlowDao, CategoryDao categoryDao,
                                SystemConfigDao systemConfigDao, CarbonFactorStrategy carbonFactorStrategy) {
        this.tradeFlowDao = Objects.requireNonNull(tradeFlowDao, "tradeFlowDao");
        this.categoryDao = Objects.requireNonNull(categoryDao, "categoryDao");
        this.systemConfigDao = Objects.requireNonNull(systemConfigDao, "systemConfigDao");
        this.carbonFactorStrategy = Objects.requireNonNull(carbonFactorStrategy, "carbonFactorStrategy");
    }

    @Override
    public List<StatisticsDTO> statisticsByCategory(LocalDateTime from, LocalDateTime to) {
        List<StatisticsDTO> raw = tradeFlowDao.countByCategoryForPeriod(from, to);
        Map<Integer, Category> categories = new HashMap<>();
        Map<String, Integer> nameToId = new HashMap<>();
        for (Category category : categoryDao.findAll()) {
            categories.put(category.getId(), category);
            if (category.getName() != null) {
                nameToId.putIfAbsent(category.getName(), category.getId());
            }
        }
        Map<String, long[]> counts = new LinkedHashMap<>();
        Map<String, BigDecimal> amounts = new HashMap<>();
        for (StatisticsDTO row : raw) {
            Integer categoryId = nameToId.get(row.getCategoryName());
            String rootName = rootCategoryName(categoryId, categories);
            counts.computeIfAbsent(rootName, key -> new long[1])[0] += row.getFlowCount();
            BigDecimal amount = row.getTotalAmount() == null ? BigDecimal.ZERO : row.getTotalAmount();
            amounts.merge(rootName, amount, BigDecimal::add);
        }
        List<StatisticsDTO> result = new ArrayList<>(counts.size());
        for (Map.Entry<String, long[]> entry : counts.entrySet()) {
            String name = entry.getKey();
            long flowCount = entry.getValue()[0];
            BigDecimal totalAmount = amounts.getOrDefault(name, BigDecimal.ZERO)
                    .setScale(2, RoundingMode.HALF_UP);
            double carbon = factorOf(name) * flowCount;
            result.add(new StatisticsDTO(name, flowCount, totalAmount, carbon));
        }
        result.sort(Comparator.comparingLong(StatisticsDTO::getFlowCount).reversed());
        return result;
    }

    @Override
    public double carbonReduction(LocalDateTime from, LocalDateTime to) {
        double total = 0.0D;
        for (StatisticsDTO dto : statisticsByCategory(from, to)) {
            total += dto.getCarbonReduction();
        }
        return BigDecimal.valueOf(total).setScale(2, RoundingMode.HALF_UP).doubleValue();
    }

    @Override
    public String exportCsv(Path target, LocalDateTime from, LocalDateTime to) throws IOException {
        return csvExporter.exportStatistics(target, statisticsByCategory(from, to), from, to);
    }

    /**
     * 取分类的一级祖先名称（分类仅两级）。
     */
    private String rootCategoryName(Integer categoryId, Map<Integer, Category> categories) {
        if (categoryId == null) {
            return "未分类";
        }
        Category current = categories.get(categoryId);
        int guard = 0;
        while (current != null && current.getParentId() != null && guard++ < 5) {
            Category parent = categories.get(current.getParentId());
            if (parent == null) {
                break;
            }
            current = parent;
        }
        return current == null ? "未分类" : current.getName();
    }

    /**
     * 碳减排系数：优先读 system_config，读不到时回退到策略实现。
     */
    private double factorOf(String rootName) {
        String key = FACTOR_KEYS.get(rootName);
        if (key == null) {
            return carbonFactorStrategy.factorOf(rootName);
        }
        return systemConfigDao.getDouble(key, carbonFactorStrategy.factorOf(rootName));
    }
}
''')

add("service/impl/AdminServiceImpl.java", r'''
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
''')

# ---------------------------------------------------------------------------
# util.ServiceFactory（工厂模式：集中装配 DAO → Service）
# ---------------------------------------------------------------------------
add("util/ServiceFactory.java", r'''
package edu.campus.recycle.util;

import edu.campus.recycle.service.AdminService;
import edu.campus.recycle.service.FavoriteService;
import edu.campus.recycle.service.ItemService;
import edu.campus.recycle.service.ReviewService;
import edu.campus.recycle.service.StatisticService;
import edu.campus.recycle.service.TradeService;
import edu.campus.recycle.service.UserService;
import edu.campus.recycle.service.impl.AdminServiceImpl;
import edu.campus.recycle.service.impl.FavoriteServiceImpl;
import edu.campus.recycle.service.impl.ItemServiceImpl;
import edu.campus.recycle.service.impl.ReviewServiceImpl;
import edu.campus.recycle.service.impl.StatisticServiceImpl;
import edu.campus.recycle.service.impl.TradeServiceImpl;
import edu.campus.recycle.service.impl.UserServiceImpl;

/**
 * 服务工厂（工厂模式）：集中完成 DAO 与领域服务的装配，上层只依赖接口。
 *
 * <p>与 {@link DaoFactory} 一起构成两级工厂：DAO 工厂负责持久化实现，服务工厂负责
 * 用例编排；两者均为进程内单例，切换实现时只需修改工厂内部代码。</p>
 */
public final class ServiceFactory {

    private static final ServiceFactory INSTANCE = new ServiceFactory();

    private final UserService userService;
    private final ItemService itemService;
    private final FavoriteService favoriteService;
    private final TradeService tradeService;
    private final ReviewService reviewService;
    private final StatisticService statisticService;
    private final AdminService adminService;

    private ServiceFactory() {
        DaoFactory dao = DaoFactory.getInstance();
        this.userService = new UserServiceImpl(dao.getUserDao(), dao.getCreditLogDao(),
                dao.getOperationLogDao(), dao.getSystemConfigDao());
        this.itemService = new ItemServiceImpl(dao.getItemDao(), dao.getItemImageDao(),
                dao.getCategoryDao(), dao.getUserDao(), dao.getTradeFlowDao(), dao.getSystemConfigDao());
        this.favoriteService = new FavoriteServiceImpl(dao.getFavoriteDao(), dao.getItemDao());
        this.tradeService = new TradeServiceImpl(dao.getTradeFlowDao(), dao.getItemDao(), dao.getUserDao());
        this.reviewService = new ReviewServiceImpl(dao.getReviewDao(), dao.getTradeFlowDao(),
                dao.getUserDao(), dao.getCreditLogDao(), dao.getSystemConfigDao());
        this.statisticService = new StatisticServiceImpl(dao.getTradeFlowDao(), dao.getCategoryDao(),
                dao.getSystemConfigDao(), new DefaultCarbonFactorStrategy());
        this.adminService = new AdminServiceImpl(dao.getCategoryDao(), dao.getOperationLogDao(), dao.getUserDao());
    }

    /**
     * 全局单例。
     *
     * @return 服务工厂
     */
    public static ServiceFactory getInstance() {
        return INSTANCE;
    }

    public UserService getUserService() {
        return userService;
    }

    public ItemService getItemService() {
        return itemService;
    }

    public FavoriteService getFavoriteService() {
        return favoriteService;
    }

    public TradeService getTradeService() {
        return tradeService;
    }

    public ReviewService getReviewService() {
        return reviewService;
    }

    public StatisticService getStatisticService() {
        return statisticService;
    }

    public AdminService getAdminService() {
        return adminService;
    }
}
''')

# ---------------------------------------------------------------------------
# 写出
# ---------------------------------------------------------------------------
count = 0
for rel, text in files.items():
    path = os.path.join(BASE, rel.replace("/", os.sep))
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="\n") as fp:
        fp.write(text)
    count += 1
    print("  + " + rel + "  " + str(len(text.encode("utf-8"))) + " B")

print("part4b 完成：%d 个文件" % count)
