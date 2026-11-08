package edu.campus.recycle.config;

import edu.campus.recycle.entity.SystemConfig;
import edu.campus.recycle.util.ConfigManager;
import edu.campus.recycle.util.DaoFactory;
import edu.campus.recycle.util.DbUtil;

import java.util.LinkedHashMap;
import java.util.Map;

/**
 * 数据库配置（单例）：启动时从 application.properties 读取连接串与脚本路径，
 * 并在运行期从 system_config 表读取业务参数（信用分、锁定策略、碳减排系数）。
 */
public final class DbConfig {

    private static final DbConfig INSTANCE = new DbConfig();

    private final String jdbcUrl;
    private final String schemaPath;
    private final String seedPath;
    private final String imageDir;
    private final boolean seedOnStart;

    private DbConfig() {
        ConfigManager config = ConfigManager.getInstance();
        this.jdbcUrl = config.getProperty(ConfigManager.KEY_DB_URL, "jdbc:sqlite:data/greencampus.db");
        this.schemaPath = config.getProperty(ConfigManager.KEY_SCHEMA, "../../db/schema.sql");
        this.seedPath = config.getProperty(ConfigManager.KEY_SEED, "../../db/seed-data.sql");
        this.imageDir = config.getProperty(ConfigManager.KEY_IMAGE_DIR, "data/images");
        this.seedOnStart = config.getBoolean(ConfigManager.KEY_SEED_ON_START, true);
    }

    /**
     * 获取单例。
     *
     * @return 配置对象
     */
    public static DbConfig getInstance() {
        return INSTANCE;
    }

    /**
     * 将连接串应用到 {@link DbUtil}（加载 JDBC 驱动）。
     */
    public void applyToDbUtil() {
        DbUtil.getInstance().init(jdbcUrl);
    }

    /**
     * 从 system_config 表读取全部配置项。
     *
     * @return 键值对（保持数据库读取顺序）
     */
    public Map<String, String> loadSystemConfigMap() {
        Map<String, String> result = new LinkedHashMap<>();
        for (SystemConfig config : DaoFactory.getInstance().getSystemConfigDao().findAll()) {
            result.put(config.getConfigKey(), config.getConfigValue());
        }
        return result;
    }

    public String getJdbcUrl() {
        return jdbcUrl;
    }

    public String getSchemaPath() {
        return schemaPath;
    }

    public String getSeedPath() {
        return seedPath;
    }

    public String getImageDir() {
        return imageDir;
    }

    public boolean isSeedOnStart() {
        return seedOnStart;
    }
}
