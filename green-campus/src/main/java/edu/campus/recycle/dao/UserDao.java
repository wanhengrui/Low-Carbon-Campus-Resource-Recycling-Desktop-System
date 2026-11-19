package edu.campus.recycle.dao;

import edu.campus.recycle.entity.User;

import java.time.LocalDateTime;
import java.util.List;
import java.util.Optional;

/**
 * 用户 DAO（契约第 5 节）。覆盖注册唯一性校验、登录失败计数与信用分更新等登录域查询。
 */
public interface UserDao extends BaseDao<User, Integer> {

    /**
     * 按登录名查询用户。
     *
     * @param username 登录名
     * @return 用户
     */
    Optional<User> findByUsername(String username);

    /**
     * 判断登录名是否已存在（BR-01 唯一性）。
     *
     * @param username 登录名
     * @return 已存在返回 true
     */
    boolean existsByUsername(String username);

    /**
     * 判断学号是否已存在（BR-01 唯一性）。
     *
     * @param studentNo 学号
     * @return 已存在返回 true
     */
    boolean existsByStudentNo(String studentNo);

    /**
     * 条件分页查询用户。
     *
     * @param keyword 关键字（匹配登录名/姓名/学号，可为 null）
     * @param role    角色过滤（可为 null）
     * @param pageNo  页码，从 1 开始
     * @param pageSize 每页条数
     * @return 用户列表
     */
    List<User> findByCondition(String keyword, String role, int pageNo, int pageSize);

    /**
     * 统计条件查询命中总数。
     *
     * @param keyword 关键字（可为 null）
     * @param role    角色过滤（可为 null）
     * @return 总条数
     */
    int countByCondition(String keyword, String role);

    /**
     * 登录成功后清零失败次数并记录登录时间。
     *
     * @param userId    用户ID
     * @param loginTime 登录时间
     * @return 受影响行数
     */
    int updateLoginSuccess(int userId, LocalDateTime loginTime);

    /**
     * 更新失败次数与锁定截止时间（BR-03）。
     *
     * @param userId     用户ID
     * @param failCount  连续失败次数
     * @param lockedUntil 锁定截止时间，null 表示不锁定
     * @return 受影响行数
     */
    int updateFailCount(int userId, int failCount, LocalDateTime lockedUntil);

    /**
     * 更新信用分。
     *
     * @param userId   用户ID
     * @param newScore 新的信用分（0–150）
     * @return 受影响行数
     */
    int updateCreditScore(int userId, int newScore);

    /**
     * 更新账号状态（ACTIVE/FROZEN/CANCELLED）。
     *
     * @param userId 用户ID
     * @param status 目标状态
     * @return 受影响行数
     */
    int updateStatus(int userId, String status);
}
