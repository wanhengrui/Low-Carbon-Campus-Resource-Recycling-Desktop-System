package edu.campus.recycle.dao;

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
