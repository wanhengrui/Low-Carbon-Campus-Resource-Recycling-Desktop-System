package edu.campus.recycle.ui;

import edu.campus.recycle.controller.AppController;

import javax.swing.JOptionPane;
import javax.swing.SwingUtilities;
import java.awt.GraphicsEnvironment;
import java.nio.file.Files;
import java.nio.file.Path;

/**
 * 迭代一成员3的 Swing 启动入口。
 *
 * <p>启动策略：默认数据库不存在时初始化一次；数据库已存在则跳过，避免每次启动
 * 都执行 schema.sql 的 DROP/重建。需要重置演示数据时运行
 * {@code run-ui.bat --reset-db}。</p>
 *
 * <p>工作目录要求：{@code 迭代一-成员1/code/green-campus}，因为
 * {@code application.properties} 中的 db.schema 使用相对路径。</p>
 */
public final class MainApp {

    private MainApp() {
    }

    public static void main(String[] args) {
        UiTheme.install();
        AppController appController = new AppController();
        try {
            if (shouldInitialize(args)) {
                appController.bootstrapDatabase();
            }
        } catch (RuntimeException ex) {
            String message = ex.getMessage() == null ? ex.toString() : ex.getMessage();
            JOptionPane.showMessageDialog(null,
                    "数据库初始化失败：\n" + message
                            + "\n\n请在 code/green-campus 目录下运行。",
                    "启动失败", JOptionPane.ERROR_MESSAGE);
            return;
        }

        if (GraphicsEnvironment.isHeadless()) {
            System.err.println("当前环境为 headless，无法显示 Swing 界面。请在有桌面的环境运行 run-ui.bat。");
            return;
        }
        SwingUtilities.invokeLater(() -> new LoginFrame(appController).setVisible(true));
    }

    private static boolean shouldInitialize(String[] args) {
        for (String arg : args) {
            if ("--reset-db".equalsIgnoreCase(arg)) {
                return true;
            }
        }
        return !Files.exists(Path.of("data", "greencampus.db"));
    }
}
