package edu.campus.recycle.service.impl;

import edu.campus.recycle.dao.CreditLogDao;
import edu.campus.recycle.dao.OperationLogDao;
import edu.campus.recycle.dao.SystemConfigDao;
import edu.campus.recycle.dao.UserDao;
import edu.campus.recycle.dto.LoginResult;
import edu.campus.recycle.dto.UserCreditDTO;
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

    @Override
    public UserCreditDTO getCredit(int userId) throws EntityNotFoundException {
        User user = findById(userId);
        int changeCount = creditLogDao.findByUserId(userId, 200).size();
        return new UserCreditDTO(user.getId(), user.getUsername(), user.getRealName(),
                user.getCreditScore(), UserCreditDTO.levelOf(user.getCreditScore()), changeCount);
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
