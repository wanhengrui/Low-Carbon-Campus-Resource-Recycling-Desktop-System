# -*- coding: utf-8 -*-
"""D7 生成器 part3a：dao 包接口（BaseDao + 11 个 DAO）与 DAO 模板基类 AbstractJdbcDao。"""
import os

BASE = r'C:\Users\wanhe\Desktop\软件构造\迭代一-成员1\code\green-campus'


def write(rel, content):
    path = os.path.join(BASE, rel)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'w', encoding='utf-8', newline='\n') as f:
        f.write(content)
    print('  + %-82s %5d B' % (rel, len(content.encode('utf-8'))))


def out(pkg, cls):
    return os.path.join('src', 'main', 'java', 'edu', 'campus', 'recycle', *pkg.split('.'), cls + '.java')


HEADER = '''package edu.campus.recycle.dao;

'''

BASE_DAO = '''package edu.campus.recycle.dao;

import java.util.List;
import java.util.Optional;

/**
 * 通用 DAO 接口（契约第 5 节）。
 *
 * <p>定义单表最基础的 5 个持久化操作；各业务 DAO 继承本接口后补充专有查询方法。
 * 模板方法 {@code AbstractJdbcDao} 提供这些方法的默认实现，实现类只需给出
 * 表名与行映射器。</p>
 *
 * @param <T>  实体类型
 * @param <ID> 主键类型
 */
public interface BaseDao<T, ID> {

    /**
     * 按主键查询。
     *
     * @param id 主键
     * @return 实体（不存在时返回空 Optional）
     */
    Optional<T> findById(ID id);

    /**
     * 查询全部记录（按主键升序）。
     *
     * @return 实体列表
     */
    List<T> findAll();

    /**
     * 插入记录。
     *
     * @param entity 实体
     * @return 受影响行数
     */
    int insert(T entity);

    /**
     * 按主键更新记录。
     *
     * @param entity 实体（必须携带主键）
     * @return 受影响行数
     */
    int update(T entity);

    /**
     * 按主键删除记录。
     *
     * @param id 主键
     * @return 受影响行数
     */
    int deleteById(ID id);
}
'''
write(out('dao', 'BaseDao'), BASE_DAO)

# ---------------------------------------------------------------- 接口定义
DAO_INTERFACES = {}

DAO_INTERFACES['UserDao'] = '''package edu.campus.recycle.dao;

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
'''

DAO_INTERFACES['CategoryDao'] = '''package edu.campus.recycle.dao;

import edu.campus.recycle.entity.Category;

import java.util.List;

/**
 * 分类 DAO（契约第 5 节）。支持两级分类树查询与启用状态维护。
 */
public interface CategoryDao extends BaseDao<Category, Integer> {

    /**
     * 查询全部启用分类（按 sort_order 升序）。
     *
     * @return 启用分类列表
     */
    List<Category> findEnabled();

    /**
     * 按父分类查询直接子分类；{@code parentId} 为 null 时查询一级分类。
     *
     * @param parentId 父分类ID，可为 null
     * @return 子分类列表
     */
    List<Category> findByParentId(Integer parentId);

    /**
     * 判断同一父分类下分类名是否已存在（UNIQUE(parent_id, name)）。
     *
     * @param parentId 父分类ID，可为 null
     * @param name     分类名
     * @return 已存在返回 true
     */
    boolean existsByName(Integer parentId, String name);

    /**
     * 启用/停用分类。
     *
     * @param id      分类ID
     * @param enabled 是否启用
     * @return 受影响行数
     */
    int updateEnabled(int id, boolean enabled);
}
'''

DAO_INTERFACES['ItemDao'] = '''package edu.campus.recycle.dao;

import edu.campus.recycle.dto.ItemQuery;
import edu.campus.recycle.dto.StatisticsDTO;
import edu.campus.recycle.entity.Item;

import java.util.List;
import java.util.Optional;

/**
 * 物品 DAO（契约第 5 节）。检索使用动态条件 + 白名单排序（策略模式），
 * 所有条件均以 {@code PreparedStatement} 参数化，杜绝 SQL 注入。
 */
public interface ItemDao extends BaseDao<Item, Integer> {

    /**
     * 插入物品并回填自增主键。
     *
     * @param item 物品
     * @return 受影响行数
     */
    @Override
    int insert(Item item);

    /**
     * 按主键查询物品。
     *
     * @param id 物品ID
     * @return 物品
     */
    Optional<Item> findById(int id);

    /**
     * 多条件检索物品。
     *
     * @param query 检索条件
     * @return 当前页物品列表
     */
    List<Item> search(ItemQuery query);

    /**
     * 统计检索命中总数。
     *
     * @param query 检索条件
     * @return 总条数
     */
    int countSearch(ItemQuery query);

    /**
     * 更新物品状态并记录审核/下架备注。
     *
     * @param itemId 物品ID
     * @param status 目标状态
     * @param remark 备注，可为 null
     * @return 受影响行数
     */
    int updateStatus(int itemId, String status, String remark);

    /**
     * 浏览数 +1。
     *
     * @param itemId 物品ID
     * @return 受影响行数
     */
    int increaseViewCount(int itemId);

    /**
     * 收藏数增减（收藏/取消收藏时调用）。
     *
     * @param itemId 物品ID
     * @param delta  +1 或 -1
     * @return 受影响行数
     */
    int increaseFavoriteCount(int itemId, int delta);

    /**
     * 查询某用户发布的物品。
     *
     * @param ownerId 发布者ID
     * @return 物品列表
     */
    List<Item> findByOwnerId(int ownerId);

    /**
     * 按分类统计已完成流转的笔数、金额与减排量（LEFT JOIN 到分类名）。
     *
     * @return 分类统计列表
     */
    List<StatisticsDTO> countByCategory();
}
'''

DAO_INTERFACES['ItemImageDao'] = '''package edu.campus.recycle.dao;

import edu.campus.recycle.entity.ItemImage;

import java.util.List;

/**
 * 物品图片 DAO（契约第 5 节）。图片只存相对路径，二进制不入库（BR-12）。
 */
public interface ItemImageDao extends BaseDao<ItemImage, Integer> {

    /**
     * 批量插入图片（单事务）。
     *
     * @param images 图片列表
     * @return 成功插入条数
     */
    int batchInsert(List<ItemImage> images);

    /**
     * 按物品查询图片（按 sort_order 升序）。
     *
     * @param itemId 物品ID
     * @return 图片列表
     */
    List<ItemImage> findByItemId(int itemId);

    /**
     * 删除某物品的全部图片。
     *
     * @param itemId 物品ID
     * @return 删除条数
     */
    int deleteByItemId(int itemId);
}
'''

DAO_INTERFACES['FavoriteDao'] = '''package edu.campus.recycle.dao;

import edu.campus.recycle.entity.Favorite;
import edu.campus.recycle.entity.Item;

import java.util.List;

/**
 * 收藏 DAO（契约第 5 节）。{@code UNIQUE(user_id, item_id)} 保证收藏唯一，
 * Service 层以 toggle 语义调用（BR-09）。
 */
public interface FavoriteDao extends BaseDao<Favorite, Integer> {

    /**
     * 判断是否已收藏。
     *
     * @param userId 用户ID
     * @param itemId 物品ID
     * @return 已收藏返回 true
     */
    boolean exists(int userId, int itemId);

    /**
     * 新增收藏。
     *
     * @param f 收藏记录
     * @return 受影响行数
     */
    int insert(Favorite f);

    /**
     * 取消收藏。
     *
     * @param userId 用户ID
     * @param itemId 物品ID
     * @return 受影响行数
     */
    int delete(int userId, int itemId);

    /**
     * 查询某用户收藏的物品（联表返回物品视图数据）。
     *
     * @param userId 用户ID
     * @return 物品列表
     */
    List<Item> findItemsByUserId(int userId);

    /**
     * 统计某物品被收藏次数。
     *
     * @param itemId 物品ID
     * @return 收藏数
     */
    int countByItemId(int itemId);
}
'''

DAO_INTERFACES['TradeMessageDao'] = '''package edu.campus.recycle.dao;

import edu.campus.recycle.entity.TradeMessage;

import java.util.List;

/**
 * 流转沟通消息 DAO（契约第 5 节）。消息按物品 + 双方用户组成会话。
 */
public interface TradeMessageDao extends BaseDao<TradeMessage, Integer> {

    /**
     * 新增消息。
     *
     * @param m 消息
     * @return 受影响行数
     */
    @Override
    int insert(TradeMessage m);

    /**
     * 查询指定物品下两名用户之间的会话（双向，按时间升序）。
     *
     * @param userId      当前用户
     * @param otherUserId 对方用户
     * @param itemId      物品ID
     * @return 消息列表
     */
    List<TradeMessage> findConversation(int userId, int otherUserId, int itemId);

    /**
     * 将某物品下发给指定用户的消息全部标记为已读。
     *
     * @param toUserId 接收者
     * @param itemId   物品ID
     * @return 更新条数
     */
    int markRead(int toUserId, int itemId);

    /**
     * 统计用户未读消息数。
     *
     * @param userId 接收者用户ID
     * @return 未读条数
     */
    int countUnread(int userId);
}
'''

DAO_INTERFACES['TradeFlowDao'] = '''package edu.campus.recycle.dao;

import edu.campus.recycle.dto.StatisticsDTO;
import edu.campus.recycle.entity.TradeFlow;

import java.time.LocalDateTime;
import java.util.List;
import java.util.Optional;

/**
 * 流转记录 DAO（契约第 5 节）。核心表，配合部分唯一索引
 * {@code uq_flow_item_active} 保证同一物品同时只有一条进行中流转（BR-05）。
 */
public interface TradeFlowDao extends BaseDao<TradeFlow, Integer> {

    /**
     * 插入流转记录并回填自增主键。
     *
     * @param f 流转记录
     * @return 受影响行数
     */
    @Override
    int insert(TradeFlow f);

    /**
     * 查询某物品当前进行中的流转（APPLYING/AGREED）。
     *
     * @param itemId 物品ID
     * @return 进行中的流转
     */
    Optional<TradeFlow> findActiveByItemId(int itemId);

    /**
     * 按主键查询流转。
     *
     * @param id 流转ID
     * @return 流转记录
     */
    Optional<TradeFlow> findById(int id);

    /**
     * 更新流转状态、取消原因与完成时间。
     *
     * @param flowId       流转ID
     * @param status       目标状态
     * @param cancelReason 取消原因，可为 null
     * @param finishedAt   完成时间，可为 null
     * @return 受影响行数
     */
    int updateStatus(int flowId, String status, String cancelReason, LocalDateTime finishedAt);

    /**
     * 分页查询某用户相关的流转（作为出让方或受让方）。
     *
     * @param userId   用户ID
     * @param status   状态过滤，可为 null
     * @param pageNo   页码
     * @param pageSize 每页条数
     * @return 流转列表
     */
    List<TradeFlow> findByUserId(int userId, String status, int pageNo, int pageSize);

    /**
     * 统计某用户相关流转总数。
     *
     * @param userId 用户ID
     * @param status 状态过滤，可为 null
     * @return 总条数
     */
    int countByUserId(int userId, String status);

    /**
     * 按分类统计指定时间区间内已完成流转的笔数与金额。
     *
     * @param from 起始时间（含）
     * @param to   结束时间（含）
     * @return 分类统计列表
     */
    List<StatisticsDTO> countByCategoryForPeriod(LocalDateTime from, LocalDateTime to);
}
'''

DAO_INTERFACES['ReviewDao'] = '''package edu.campus.recycle.dao;

import edu.campus.recycle.entity.Review;

import java.util.List;

/**
 * 评价 DAO（契约第 5 节）。{@code UNIQUE(flow_id, reviewer_id)} 保证同一流转每人只评一次（BR-08）。
 */
public interface ReviewDao extends BaseDao<Review, Integer> {

    /**
     * 新增评价。
     *
     * @param r 评价
     * @return 受影响行数
     */
    @Override
    int insert(Review r);

    /**
     * 判断某用户是否已评价过该流转。
     *
     * @param flowId     流转ID
     * @param reviewerId 评价人
     * @return 已评价返回 true
     */
    boolean existsByFlowAndReviewer(int flowId, int reviewerId);

    /**
     * 查询某用户收到的评价。
     *
     * @param revieweeId 被评价人
     * @return 评价列表
     */
    List<Review> findByRevieweeId(int revieweeId);

    /**
     * 计算某用户收到的平均评分。
     *
     * @param revieweeId 被评价人
     * @return 平均分（无评价时返回 0）
     */
    double avgScoreByRevieweeId(int revieweeId);
}
'''

DAO_INTERFACES['CreditLogDao'] = '''package edu.campus.recycle.dao;

import edu.campus.recycle.entity.CreditLog;

import java.util.List;

/**
 * 信用分流水 DAO（契约第 5 节）。流水只追加，作为信用分变更的审计快照（BR-04）。
 */
public interface CreditLogDao extends BaseDao<CreditLog, Integer> {

    /**
     * 新增流水。
     *
     * @param log 流水
     * @return 受影响行数
     */
    @Override
    int insert(CreditLog log);

    /**
     * 查询某用户最近若干条信用分流水（按时间倒序）。
     *
     * @param userId 用户ID
     * @param limit  条数上限
     * @return 流水列表
     */
    List<CreditLog> findByUserId(int userId, int limit);
}
'''

DAO_INTERFACES['OperationLogDao'] = '''package edu.campus.recycle.dao;

import edu.campus.recycle.entity.OperationLog;

import java.util.List;

/**
 * 操作日志 DAO（契约第 5 节）。日志仅追加，不提供修改与删除（BR-11）。
 */
public interface OperationLogDao extends BaseDao<OperationLog, Integer> {

    /**
     * 追加一条操作日志。
     *
     * @param log 日志
     * @return 受影响行数
     */
    @Override
    int insert(OperationLog log);

    /**
     * 查询最近若干条操作日志（按时间倒序）。
     *
     * @param limit 条数上限
     * @return 日志列表
     */
    List<OperationLog> findRecent(int limit);
}
'''

DAO_INTERFACES['SystemConfigDao'] = '''package edu.campus.recycle.dao;

import edu.campus.recycle.entity.SystemConfig;

/**
 * 系统配置 DAO（契约第 5 节）。读取 {@code system_config} 中的业务参数
 * （信用分阈值、减排系数、登录锁定策略等）。
 */
public interface SystemConfigDao extends BaseDao<SystemConfig, Integer> {

    /**
     * 读取配置值。
     *
     * @param key 配置键
     * @return 配置值，不存在返回 null
     */
    String getValue(String key);

    /**
     * 读取整型配置。
     *
     * @param key          配置键
     * @param defaultValue 缺省值
     * @return 配置值
     */
    int getInt(String key, int defaultValue);

    /**
     * 读取浮点配置。
     *
     * @param key          配置键
     * @param defaultValue 缺省值
     * @return 配置值
     */
    double getDouble(String key, double defaultValue);

    /**
     * 写入或覆盖配置项。
     *
     * @param key         配置键
     * @param value       配置值
     * @param description 说明
     * @return 受影响行数
     */
    int upsert(String key, String value, String description);
}
'''

for cls, content in DAO_INTERFACES.items():
    write(out('dao', cls), content)

# ---------------------------------------------------------------- AbstractJdbcDao
ABSTRACT_JDBC_DAO = '''package edu.campus.recycle.dao.impl;

import edu.campus.recycle.exception.DataAccessException;
import edu.campus.recycle.util.ConnectionCallback;
import edu.campus.recycle.util.DbUtil;
import edu.campus.recycle.util.RowMapper;

import java.math.BigDecimal;
import java.sql.Connection;
import java.sql.PreparedStatement;
import java.sql.ResultSet;
import java.sql.SQLException;
import java.sql.Statement;
import java.time.LocalDateTime;
import java.time.format.DateTimeFormatter;
import java.time.format.DateTimeParseException;
import java.util.ArrayList;
import java.util.List;
import java.util.Optional;
import java.util.logging.Level;
import java.util.logging.Logger;

/**
 * JDBC DAO 模板基类（契约第 8 节：模板方法 + 统一异常转换）。
 *
 * <p>模板方法负责：获取连接（事务中自动复用事务连接）→ 绑定参数 → 执行 →
 * 映射结果 → 关闭资源 → 把 {@link SQLException} 统一转换为
 * {@link DataAccessException}。子类只需声明表名、行映射器与业务 SQL，不再出现
 * 重复的 try-catch-finally。</p>
 *
 * @param <T> 实体类型
 */
public abstract class AbstractJdbcDao<T> {

    private static final Logger LOG = Logger.getLogger(AbstractJdbcDao.class.getName());

    /** 数据库时间格式：yyyy-MM-dd HH:mm:ss（契约第 2 节） */
    public static final DateTimeFormatter DATE_TIME_FORMATTER =
            DateTimeFormatter.ofPattern("yyyy-MM-dd HH:mm:ss");

    /**
     * 逻辑表名，仅用于日志与错误信息定位。
     *
     * @return 表名
     */
    protected abstract String tableName();

    /**
     * 行映射器，把结果集当前行转换为实体。
     *
     * @return 行映射器
     */
    protected abstract RowMapper<T> rowMapper();

    // ------------------------------------------------------------------ 模板方法

    /**
     * 模板方法：在连接上执行 JDBC 操作并统一处理资源与异常。
     *
     * @param callback JDBC 回调
     * @param <R>      返回类型
     * @return 回调结果
     */
    protected <R> R withConnection(ConnectionCallback<R> callback) {
        boolean managed = DbUtil.getInstance().isInTransaction();
        Connection conn = null;
        try {
            conn = DbUtil.getInstance().currentConnection();
            return callback.doInConnection(conn);
        } catch (SQLException e) {
            LOG.log(Level.SEVERE, "[" + tableName() + "] 数据访问失败：" + e.getMessage(), e);
            throw DataAccessException.of("数据访问失败（" + tableName() + "），请稍后重试", e);
        } finally {
            if (!managed) {
                DbUtil.getInstance().closeQuietly(conn);
            }
        }
    }

    /**
     * 执行 INSERT/UPDATE/DELETE。
     *
     * @param sql    SQL 语句（参数使用 ? 占位）
     * @param params 参数
     * @return 受影响行数
     */
    protected int executeUpdate(String sql, Object... params) {
        return withConnection(conn -> {
            try (PreparedStatement ps = conn.prepareStatement(sql)) {
                setParams(ps, params);
                return ps.executeUpdate();
            }
        });
    }

    /**
     * 执行 INSERT 并返回自增主键。
     *
     * @param sql    SQL 语句
     * @param params 参数
     * @return 自增主键
     */
    protected long executeInsert(String sql, Object... params) {
        return withConnection(conn -> {
            try (PreparedStatement ps = conn.prepareStatement(sql, Statement.RETURN_GENERATED_KEYS)) {
                setParams(ps, params);
                ps.executeUpdate();
                try (ResultSet keys = ps.getGeneratedKeys()) {
                    if (keys.next()) {
                        return keys.getLong(1);
                    }
                }
            }
            throw new SQLException("插入成功但未获取到自增主键");
        });
    }

    /**
     * 查询多行并映射。
     *
     * @param sql    SQL 语句
     * @param mapper 行映射器
     * @param params 参数
     * @param <R>    结果类型
     * @return 结果列表（无结果返回空列表）
     */
    protected <R> List<R> queryList(String sql, RowMapper<R> mapper, Object... params) {
        return withConnection(conn -> {
            try (PreparedStatement ps = conn.prepareStatement(sql)) {
                setParams(ps, params);
                try (ResultSet rs = ps.executeQuery()) {
                    List<R> list = new ArrayList<>();
                    while (rs.next()) {
                        list.add(mapper.mapRow(rs));
                    }
                    return list;
                }
            }
        });
    }

    /**
     * 查询单行并映射。
     *
     * @param sql    SQL 语句
     * @param mapper 行映射器
     * @param params 参数
     * @param <R>    结果类型
     * @return 结果（无结果返回空 Optional）
     */
    protected <R> Optional<R> queryOne(String sql, RowMapper<R> mapper, Object... params) {
        List<R> list = queryList(sql, mapper, params);
        return list.isEmpty() ? Optional.empty() : Optional.of(list.get(0));
    }

    /**
     * 查询单个整数（如 COUNT(*)）。
     *
     * @param sql    SQL 语句
     * @param params 参数
     * @return 整数结果，NULL 时返回 0
     */
    protected int queryInt(String sql, Object... params) {
        Optional<Integer> value = queryOne(sql, rs -> rs.getInt(1), params);
        return value.orElse(0);
    }

    /**
     * 查询单个字符串。
     *
     * @param sql    SQL 语句
     * @param params 参数
     * @return 字符串结果
     */
    protected Optional<String> queryString(String sql, Object... params) {
        return queryOne(sql, rs -> rs.getString(1), params);
    }

    /**
     * 查询单个浮点数。
     *
     * @param sql    SQL 语句
     * @param params 参数
     * @return 浮点结果，NULL 时返回 0
     */
    protected double queryDouble(String sql, Object... params) {
        Optional<Double> value = queryOne(sql, rs -> rs.getDouble(1), params);
        return value.orElse(0.0D);
    }

    // ------------------------------------------------------------------ 参数绑定与类型转换

    /**
     * 绑定 PreparedStatement 参数，统一处理 LocalDateTime、BigDecimal、Boolean 与枚举。
     *
     * @param ps     PreparedStatement
     * @param params 参数数组
     * @throws SQLException 绑定失败
     */
    protected static void setParams(PreparedStatement ps, Object[] params) throws SQLException {
        if (params == null) {
            return;
        }
        for (int i = 0; i < params.length; i++) {
            Object value = params[i];
            int index = i + 1;
            if (value == null) {
                ps.setObject(index, null);
            } else if (value instanceof LocalDateTime) {
                ps.setString(index, formatDateTime((LocalDateTime) value));
            } else if (value instanceof BigDecimal) {
                ps.setBigDecimal(index, (BigDecimal) value);
            } else if (value instanceof Boolean) {
                ps.setInt(index, ((Boolean) value) ? 1 : 0);
            } else if (value instanceof Enum) {
                ps.setString(index, ((Enum<?>) value).name());
            } else {
                ps.setObject(index, value);
            }
        }
    }

    /**
     * 读取 TEXT 时间列并解析为 LocalDateTime。
     *
     * @param rs     结果集
     * @param column 列名
     * @return 时间，NULL 返回 null
     * @throws SQLException 读取失败
     */
    protected static LocalDateTime readDateTime(ResultSet rs, String column) throws SQLException {
        String value = rs.getString(column);
        if (value == null || value.isBlank()) {
            return null;
        }
        String trimmed = value.trim();
        try {
            return LocalDateTime.parse(trimmed, DATE_TIME_FORMATTER);
        } catch (DateTimeParseException e) {
            return LocalDateTime.parse(trimmed, DateTimeFormatter.ISO_LOCAL_DATE_TIME);
        }
    }

    /**
     * 把 LocalDateTime 格式化为数据库 TEXT 形式。
     *
     * @param time 时间
     * @return 格式化字符串，null 返回 null
     */
    protected static String formatDateTime(LocalDateTime time) {
        return time == null ? null : time.format(DATE_TIME_FORMATTER);
    }

    /**
     * 读取 INTEGER(0/1) 布尔列。
     *
     * @param rs     结果集
     * @param column 列名
     * @return 布尔值
     * @throws SQLException 读取失败
     */
    protected static boolean readBoolean(ResultSet rs, String column) throws SQLException {
        return rs.getInt(column) != 0;
    }

    /**
     * 读取可空整数列。
     *
     * @param rs     结果集
     * @param column 列名
     * @return 整数，NULL 返回 null
     * @throws SQLException 读取失败
     */
    protected static Integer readInteger(ResultSet rs, String column) throws SQLException {
        int value = rs.getInt(column);
        return rs.wasNull() ? null : value;
    }

    /**
     * 读取可空长整型列。
     *
     * @param rs     结果集
     * @param column 列名
     * @return 长整型，NULL 返回 null
     * @throws SQLException 读取失败
     */
    protected static Long readLong(ResultSet rs, String column) throws SQLException {
        long value = rs.getLong(column);
        return rs.wasNull() ? null : value;
    }

    /**
     * 读取 REAL 金额列并转 BigDecimal。
     *
     * @param rs     结果集
     * @param column 列名
     * @return 金额，NULL 返回 null
     * @throws SQLException 读取失败
     */
    protected static BigDecimal readBigDecimal(ResultSet rs, String column) throws SQLException {
        return rs.getBigDecimal(column);
    }
}
'''
write(out('dao.impl', 'AbstractJdbcDao'), ABSTRACT_JDBC_DAO)

print('\npart3a 完成（DAO 接口 12 个 + AbstractJdbcDao）。')
