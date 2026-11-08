package edu.campus.recycle.config;

import edu.campus.recycle.exception.DataAccessException;
import edu.campus.recycle.util.DbUtil;

import java.io.IOException;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.sql.Connection;
import java.sql.SQLException;
import java.sql.Statement;
import java.util.ArrayList;
import java.util.List;
import java.util.logging.Level;
import java.util.logging.Logger;

/**
 * 数据库初始化器：执行 {@code schema.sql}（脚本自身可重复执行：先反序 DROP 再重建），
 * 并按开关执行 {@code seed-data.sql} 导入演示数据。
 *
 * <p>脚本按分号拆分逐条执行；拆分时识别单引号字符串与 {@code --} 行注释，避免误切。</p>
 */
public final class DatabaseInitializer {

    private static final Logger LOG = Logger.getLogger(DatabaseInitializer.class.getName());

    private DatabaseInitializer() {
    }

    /**
     * 初始化数据库（含种子数据，取决于配置 app.seed.on.start）。
     */
    public static void initialize() {
        initialize(DbConfig.getInstance().isSeedOnStart());
    }

    /**
     * 初始化数据库。
     *
     * @param withSeed 是否导入种子数据
     */
    public static void initialize(boolean withSeed) {
        ensureDatabaseDirectory();
        Path schema = Paths.get(DbConfig.getInstance().getSchemaPath()).toAbsolutePath().normalize();
        runScript(schema, "建库脚本");
        if (withSeed) {
            Path seed = Paths.get(DbConfig.getInstance().getSeedPath()).toAbsolutePath().normalize();
            runScript(seed, "种子数据脚本");
        }
        LOG.info(() -> "数据库初始化完成，schema=" + schema);
    }

    /**
     * 确保 SQLite 数据库文件所在目录存在（首次运行时 data 目录通常不存在）。
     */
    private static void ensureDatabaseDirectory() {
        String jdbcUrl = DbUtil.getInstance().getJdbcUrl();
        final String prefix = "jdbc:sqlite:";
        if (jdbcUrl == null || !jdbcUrl.startsWith(prefix)) {
            return;
        }
        String filePart = jdbcUrl.substring(prefix.length());
        if (filePart.isEmpty() || filePart.startsWith(":memory:")) {
            return;
        }
        Path parent = Paths.get(filePart).toAbsolutePath().normalize().getParent();
        if (parent == null) {
            return;
        }
        try {
            Files.createDirectories(parent);
        } catch (IOException e) {
            throw new DataAccessException("无法创建数据库目录：" + parent, e);
        }
    }

    /**
     * 执行一个 SQL 脚本文件。
     *
     * @param path  脚本路径
     * @param label 日志标签
     */
    private static void runScript(Path path, String label) {
        if (!Files.exists(path)) {
            throw new IllegalStateException(label + "不存在：" + path);
        }
        String content;
        try {
            content = Files.readString(path, StandardCharsets.UTF_8);
        } catch (IOException e) {
            throw DataAccessException.of("读取" + label + "失败：" + path, e);
        }
        List<String> statements = splitStatements(content);
        LOG.info(() -> label + "共 " + statements.size() + " 条语句：" + path.getFileName());
        try (Connection connection = DbUtil.getInstance().getConnection();
             Statement statement = connection.createStatement()) {
            for (String sql : statements) {
                statement.execute(sql);
            }
        } catch (SQLException e) {
            throw DataAccessException.of("执行" + label + "失败：" + path + "（" + e.getMessage() + "）", e);
        }
    }

    /**
     * 按分号拆分 SQL 语句：忽略行注释与字符串内的分号。
     *
     * @param content 脚本全文
     * @return 语句列表
     */
    static List<String> splitStatements(String content) {
        List<String> statements = new ArrayList<>();
        StringBuilder current = new StringBuilder();
        boolean inSingleQuote = false;
        boolean inComment = false;
        for (int i = 0; i < content.length(); i++) {
            char ch = content.charAt(i);
            if (inComment) {
                if (ch == '\n') {
                    inComment = false;
                    current.append('\n');
                }
                continue;
            }
            if (!inSingleQuote && ch == '-' && i + 1 < content.length() && content.charAt(i + 1) == '-') {
                inComment = true;
                i++;
                continue;
            }
            if (ch == '\'') {
                if (inSingleQuote && i + 1 < content.length() && content.charAt(i + 1) == '\'') {
                    current.append("''");
                    i++;
                    continue;
                }
                inSingleQuote = !inSingleQuote;
                current.append(ch);
                continue;
            }
            if (ch == ';' && !inSingleQuote) {
                addStatement(statements, current);
                current.setLength(0);
                continue;
            }
            current.append(ch);
        }
        addStatement(statements, current);
        return statements;
    }

    private static void addStatement(List<String> statements, StringBuilder buffer) {
        String sql = buffer.toString().trim();
        if (!sql.isEmpty()) {
            statements.add(sql);
        }
    }
}
