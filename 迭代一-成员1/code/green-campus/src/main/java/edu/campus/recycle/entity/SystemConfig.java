package edu.campus.recycle.entity;

import java.time.LocalDateTime;

/**
 * 系统配置实体，与数据库表 {@code system_config} 一一对应（契约第 3.11 节，字段不得增删）。
 *
 * <p>字段名由表字段下划线形式转驼峰，金额使用 {@link java.math.BigDecimal}，
 * 时间使用 {@link java.time.LocalDateTime}，布尔语义字段使用 {@link Boolean}。</p>
 */
public class SystemConfig {

    /** 配置ID（主键） */
    private Integer id;

    /** 配置键 */
    private String configKey;

    /** 配置值 */
    private String configValue;

    /** 配置说明 */
    private String description;

    /** 更新时间 */
    private LocalDateTime updatedAt;

    /** 无参构造器，供 DAO 与框架反射使用。 */
    public SystemConfig() {
    }

    /** 全参构造器。 */
    public SystemConfig(Integer id, String configKey, String configValue, String description, LocalDateTime updatedAt) {
        this.id = id;
        this.configKey = configKey;
        this.configValue = configValue;
        this.description = description;
        this.updatedAt = updatedAt;
    }

    public Integer getId() {
        return id;
    }

    public void setId(Integer id) {
        this.id = id;
    }

    public String getConfigKey() {
        return configKey;
    }

    public void setConfigKey(String configKey) {
        this.configKey = configKey;
    }

    public String getConfigValue() {
        return configValue;
    }

    public void setConfigValue(String configValue) {
        this.configValue = configValue;
    }

    public String getDescription() {
        return description;
    }

    public void setDescription(String description) {
        this.description = description;
    }

    public LocalDateTime getUpdatedAt() {
        return updatedAt;
    }

    public void setUpdatedAt(LocalDateTime updatedAt) {
        this.updatedAt = updatedAt;
    }

    @Override
    public String toString() {
        return "SystemConfig{" + "id=" + id + ", " + "configKey=" + configKey + ", " + "configValue=" + configValue + ", " + "description=" + description + ", " + "updatedAt=" + updatedAt + '}';
    }
}
