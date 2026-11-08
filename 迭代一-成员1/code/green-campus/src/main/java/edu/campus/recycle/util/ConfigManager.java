package edu.campus.recycle.util;

import java.io.IOException;
import java.io.InputStream;
import java.util.Properties;
import java.util.logging.Level;
import java.util.logging.Logger;

/**
 * 配置管理器（契约第 8 节：单例）。
 *
 * <p>读取 classpath 下的 {@code application.properties}，未配置项使用内置默认值；
 * 数据库中的 {@code system_config} 由业务层通过 {@code SystemConfigDao} 读取，
 * 二者分工为"部署参数"与"业务参数"。</p>
 */
public final class ConfigManager {

    private static final Logger LOG = Logger.getLogger(ConfigManager.class.getName());

    /** 单例实例 */
    private static final ConfigManager INSTANCE = new ConfigManager();

    /** 配置文件位置 */
    public static final String CONFIG_RESOURCE = "application.properties";

    /** 建库脚本路径（默认相对工程根目录） */
    public static final String KEY_SCHEMA = "db.schema";
    /** 种子数据脚本路径 */
    public static final String KEY_SEED = "db.seed";
    /** SQLite 连接串 */
    public static final String KEY_DB_URL = "db.url";
    /** 图片根目录 */
    public static final String KEY_IMAGE_DIR = "app.image.dir";
    /** 控制台演示数据开关 */
    public static final String KEY_SEED_ON_START = "app.seed.on.start";

    private final Properties properties = new Properties();

    private ConfigManager() {
        loadDefaults();
        loadFromResource(CONFIG_RESOURCE);
    }

    /**
     * 获取单例。
     *
     * @return 配置管理器
     */
    public static ConfigManager getInstance() {
        return INSTANCE;
    }

    private void loadDefaults() {
        properties.setProperty(KEY_DB_URL, "jdbc:sqlite:data/greencampus.db");
        properties.setProperty(KEY_SCHEMA, "../../db/schema.sql");
        properties.setProperty(KEY_SEED, "../../db/seed-data.sql");
        properties.setProperty(KEY_IMAGE_DIR, "data/images");
        properties.setProperty(KEY_SEED_ON_START, "true");
        properties.setProperty("app.name", "绿色校园闲置物品循环流转平台");
        properties.setProperty("app.version", "1.0.0");
    }

    private void loadFromResource(String resource) {
        try (InputStream in = ConfigManager.class.getClassLoader().getResourceAsStream(resource)) {
            if (in == null) {
                LOG.log(Level.INFO, "未找到 {0}，使用内置默认配置", resource);
                return;
            }
            properties.load(new java.io.InputStreamReader(in, java.nio.charset.StandardCharsets.UTF_8));
            LOG.log(Level.INFO, "已加载配置 {0}，共 {1} 项", new Object[]{resource, properties.size()});
        } catch (IOException e) {
            LOG.log(Level.WARNING, "加载配置失败，使用内置默认配置", e);
        }
    }

    /**
     * 读取字符串配置。
     *
     * @param key          键
     * @param defaultValue 默认值
     * @return 配置值
     */
    public String getProperty(String key, String defaultValue) {
        return properties.getProperty(key, defaultValue);
    }

    /**
     * 读取整型配置。
     *
     * @param key          键
     * @param defaultValue 默认值
     * @return 配置值
     */
    public int getInt(String key, int defaultValue) {
        String value = properties.getProperty(key);
        if (value == null) {
            return defaultValue;
        }
        try {
            return Integer.parseInt(value.trim());
        } catch (NumberFormatException e) {
            LOG.log(Level.WARNING, "配置 {0} 不是合法整数：{1}", new Object[]{key, value});
            return defaultValue;
        }
    }

    /**
     * 读取浮点配置。
     *
     * @param key          键
     * @param defaultValue 默认值
     * @return 配置值
     */
    public double getDouble(String key, double defaultValue) {
        String value = properties.getProperty(key);
        if (value == null) {
            return defaultValue;
        }
        try {
            return Double.parseDouble(value.trim());
        } catch (NumberFormatException e) {
            LOG.log(Level.WARNING, "配置 {0} 不是合法数值：{1}", new Object[]{key, value});
            return defaultValue;
        }
    }

    /**
     * 读取布尔配置。
     *
     * @param key          键
     * @param defaultValue 默认值
     * @return 配置值
     */
    public boolean getBoolean(String key, boolean defaultValue) {
        String value = properties.getProperty(key);
        return value == null ? defaultValue : Boolean.parseBoolean(value.trim());
    }
}
