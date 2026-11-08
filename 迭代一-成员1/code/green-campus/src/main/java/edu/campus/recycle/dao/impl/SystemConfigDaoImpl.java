package edu.campus.recycle.dao.impl;

import edu.campus.recycle.dao.SystemConfigDao;
import edu.campus.recycle.entity.SystemConfig;
import edu.campus.recycle.util.RowMapper;

import java.time.LocalDateTime;
import java.util.List;
import java.util.Optional;

/**
 * 系统配置 DAO 实现。业务参数（信用分阈值、减排系数、锁定策略等）集中存放，
 * 由 {@code ConfigManager} 与各 Service 读取，避免硬编码。
 */
public class SystemConfigDaoImpl extends AbstractJdbcDao<SystemConfig> implements SystemConfigDao {

    private static final String TABLE = "system_config";

    private static final String COLUMNS = "id, config_key, config_value, description, updated_at";

    private static final RowMapper<SystemConfig> ROW_MAPPER = rs -> {
        SystemConfig config = new SystemConfig();
        config.setId(rs.getInt("id"));
        config.setConfigKey(rs.getString("config_key"));
        config.setConfigValue(rs.getString("config_value"));
        config.setDescription(rs.getString("description"));
        config.setUpdatedAt(readDateTime(rs, "updated_at"));
        return config;
    };

    @Override
    protected String tableName() {
        return TABLE;
    }

    @Override
    protected RowMapper<SystemConfig> rowMapper() {
        return ROW_MAPPER;
    }

    @Override
    public Optional<SystemConfig> findById(Integer id) {
        return queryOne("SELECT " + COLUMNS + " FROM " + TABLE + " WHERE id = ?", ROW_MAPPER, id);
    }

    @Override
    public List<SystemConfig> findAll() {
        return queryList("SELECT " + COLUMNS + " FROM " + TABLE + " ORDER BY config_key", ROW_MAPPER);
    }

    @Override
    public int insert(SystemConfig config) {
        LocalDateTime now = config.getUpdatedAt() == null ? LocalDateTime.now() : config.getUpdatedAt();
        long id = executeInsert("INSERT INTO " + TABLE
                        + " (config_key, config_value, description, updated_at) VALUES (?, ?, ?, ?)",
                config.getConfigKey(), config.getConfigValue(), config.getDescription(),
                formatDateTime(now));
        config.setId((int) id);
        return 1;
    }

    @Override
    public int update(SystemConfig config) {
        LocalDateTime now = config.getUpdatedAt() == null ? LocalDateTime.now() : config.getUpdatedAt();
        return executeUpdate("UPDATE " + TABLE + " SET config_key = ?, config_value = ?,"
                        + " description = ?, updated_at = ? WHERE id = ?",
                config.getConfigKey(), config.getConfigValue(), config.getDescription(),
                formatDateTime(now), config.getId());
    }

    @Override
    public int deleteById(Integer id) {
        return executeUpdate("DELETE FROM " + TABLE + " WHERE id = ?", id);
    }

    @Override
    public String getValue(String key) {
        return queryOne("SELECT config_value FROM " + TABLE + " WHERE config_key = ?",
                rs -> rs.getString(1), key).orElse(null);
    }

    @Override
    public int getInt(String key, int defaultValue) {
        String value = getValue(key);
        if (value == null || value.isBlank()) {
            return defaultValue;
        }
        try {
            return Integer.parseInt(value.trim());
        } catch (NumberFormatException e) {
            return defaultValue;
        }
    }

    @Override
    public double getDouble(String key, double defaultValue) {
        String value = getValue(key);
        if (value == null || value.isBlank()) {
            return defaultValue;
        }
        try {
            return Double.parseDouble(value.trim());
        } catch (NumberFormatException e) {
            return defaultValue;
        }
    }

    @Override
    public int upsert(String key, String value, String description) {
        int updated = executeUpdate("UPDATE " + TABLE + " SET config_value = ?, description = ?,"
                + " updated_at = ? WHERE config_key = ?", value, description,
                formatDateTime(LocalDateTime.now()), key);
        if (updated > 0) {
            return updated;
        }
        SystemConfig config = new SystemConfig();
        config.setConfigKey(key);
        config.setConfigValue(value);
        config.setDescription(description);
        return insert(config);
    }
}
