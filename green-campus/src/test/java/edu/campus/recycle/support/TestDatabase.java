package edu.campus.recycle.support;

import edu.campus.recycle.config.DatabaseInitializer;
import edu.campus.recycle.util.DbUtil;

import java.nio.file.Path;

/** 每个用例使用一个空库，测试结束后恢复原 JDBC URL。 */
public final class TestDatabase implements AutoCloseable {
    private final DbUtil db = DbUtil.getInstance();
    private final String previousUrl = db.getJdbcUrl();

    public TestDatabase(Path directory) {
        boolean initialized = false;
        try {
            db.init("jdbc:sqlite:" + directory.resolve("test.db").toAbsolutePath());
            DatabaseInitializer.initialize(false);
            initialized = true;
        } finally {
            if (!initialized) {
                close();
            }
        }
    }

    @Override
    public void close() {
        db.init(previousUrl);
    }
}
