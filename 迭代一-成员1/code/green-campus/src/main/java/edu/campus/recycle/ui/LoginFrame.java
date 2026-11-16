package edu.campus.recycle.ui;

import edu.campus.recycle.controller.AppController;
import edu.campus.recycle.controller.UserController;
import edu.campus.recycle.dto.LoginResult;
import edu.campus.recycle.exception.AppException;

import javax.swing.BorderFactory;
import javax.swing.Box;
import javax.swing.BoxLayout;
import javax.swing.JButton;
import javax.swing.JFrame;
import javax.swing.JLabel;
import javax.swing.JPanel;
import javax.swing.JPasswordField;
import javax.swing.JTextField;
import javax.swing.SwingConstants;
import javax.swing.SwingWorker;
import java.awt.BorderLayout;
import java.awt.Color;
import java.awt.Dimension;
import java.awt.Font;
import java.awt.GridBagConstraints;
import java.awt.GridBagLayout;
import java.awt.Insets;
import java.util.concurrent.ExecutionException;

/**
 * 登录窗体（迭代一成员3骨架）。
 *
 * <p>只通过 {@link AppController} 调用登录；登录成功后把当前用户会话带入
 * {@link MainFrame}。注册入口打开 {@link RegisterDialog}。</p>
 */
public class LoginFrame extends JFrame {

    private final AppController appController;
    private final UserController userController = new UserController();
    private final JTextField usernameField = new JTextField(20);
    private final JPasswordField passwordField = new JPasswordField(20);
    private final JLabel statusLabel = new JLabel(" ", SwingConstants.CENTER);
    private final JButton loginButton = UiTheme.primaryButton("登 录");
    private final JButton registerButton = UiTheme.secondaryButton("注册新账号");

    public LoginFrame(AppController appController) {
        super("绿色校园 · 登录");
        this.appController = appController;
        setDefaultCloseOperation(EXIT_ON_CLOSE);
        setMinimumSize(new Dimension(520, 430));
        setContentPane(buildContent());
        pack();
        setLocationRelativeTo(null);
        getRootPane().setDefaultButton(loginButton);
        loginButton.addActionListener(e -> doLogin());
        registerButton.addActionListener(e -> new RegisterDialog(this, userController).setVisible(true));
    }

    private JPanel buildContent() {
        JPanel root = new JPanel(new BorderLayout());
        root.setBackground(UiTheme.BACKGROUND);
        root.setBorder(BorderFactory.createEmptyBorder(36, 64, 36, 64));

        JPanel brand = new JPanel();
        brand.setOpaque(false);
        brand.setLayout(new BoxLayout(brand, BoxLayout.Y_AXIS));
        JLabel title = new JLabel("绿色校园");
        title.setFont(new Font("Microsoft YaHei", Font.BOLD, 30));
        title.setForeground(UiTheme.NAVY);
        JLabel subtitle = new JLabel("闲置物品循环流转平台");
        subtitle.setFont(new Font("Microsoft YaHei", Font.PLAIN, 15));
        subtitle.setForeground(UiTheme.MUTED);
        JLabel version = new JLabel("迭代一 · Swing 界面骨架");
        version.setFont(new Font("Microsoft YaHei", Font.PLAIN, 12));
        version.setForeground(UiTheme.GREEN);
        brand.add(title);
        brand.add(Box.createVerticalStrut(4));
        brand.add(subtitle);
        brand.add(Box.createVerticalStrut(8));
        brand.add(version);
        brand.add(Box.createVerticalStrut(24));

        JPanel form = new JPanel(new GridBagLayout());
        form.setOpaque(false);
        GridBagConstraints gbc = new GridBagConstraints();
        gbc.gridx = 0;
        gbc.gridy = 0;
        gbc.weightx = 0;
        gbc.fill = GridBagConstraints.HORIZONTAL;
        gbc.insets = new Insets(8, 0, 6, 12);
        form.add(new JLabel("用户名"), gbc);
        gbc.gridx = 1;
        gbc.weightx = 1;
        gbc.insets = new Insets(8, 0, 6, 0);
        form.add(usernameField, gbc);

        gbc.gridx = 0;
        gbc.gridy++;
        gbc.weightx = 0;
        gbc.insets = new Insets(6, 0, 6, 12);
        form.add(new JLabel("密  码"), gbc);
        gbc.gridx = 1;
        gbc.weightx = 1;
        gbc.insets = new Insets(6, 0, 6, 0);
        form.add(passwordField, gbc);

        gbc.gridx = 0;
        gbc.gridy++;
        gbc.gridwidth = 2;
        gbc.insets = new Insets(18, 0, 8, 0);
        loginButton.setMaximumSize(new Dimension(Integer.MAX_VALUE, 40));
        form.add(loginButton, gbc);

        gbc.gridy++;
        gbc.insets = new Insets(2, 0, 4, 0);
        form.add(registerButton, gbc);

        gbc.gridy++;
        statusLabel.setForeground(new Color(180, 60, 45));
        statusLabel.setFont(new Font("Microsoft YaHei", Font.PLAIN, 12));
        form.add(statusLabel, gbc);

        JPanel card = new JPanel(new BorderLayout());
        UiTheme.cardBorder(card);
        card.add(brand, BorderLayout.NORTH);
        card.add(form, BorderLayout.CENTER);

        JLabel hint = new JLabel("演示账号：admin / Admin@123　或　zhangsan / Student@123", SwingConstants.CENTER);
        hint.setForeground(UiTheme.MUTED);
        hint.setFont(new Font("Microsoft YaHei", Font.PLAIN, 11));
        root.add(card, BorderLayout.CENTER);
        root.add(hint, BorderLayout.SOUTH);
        return root;
    }

    private void doLogin() {
        String username = usernameField.getText().trim();
        String password = new String(passwordField.getPassword());
        if (username.isEmpty() || password.isEmpty()) {
            statusLabel.setText("请输入用户名和密码");
            return;
        }
        setBusy(true);
        statusLabel.setText("正在登录…");
        new SwingWorker<LoginResult, Void>() {
            @Override
            protected LoginResult doInBackground() {
                return appController.login(username, password);
            }

            @Override
            protected void done() {
                try {
                    LoginResult result = get();
                    if (result == null || !result.isSuccess()) {
                        String message = result == null ? "登录失败" : result.getMessage();
                        statusLabel.setText(message == null ? "登录失败" : message);
                        passwordField.selectAll();
                        return;
                    }
                    MainFrame mainFrame = new MainFrame(appController, result);
                    mainFrame.setVisible(true);
                    dispose();
                } catch (InterruptedException ex) {
                    Thread.currentThread().interrupt();
                    statusLabel.setText("登录被中断");
                } catch (ExecutionException ex) {
                    Throwable cause = ex.getCause();
                    if (cause instanceof AppException) {
                        statusLabel.setText(((AppException) cause).getUserMessage());
                    } else {
                        statusLabel.setText(cause == null ? "登录失败" : cause.getMessage());
                    }
                    passwordField.selectAll();
                } finally {
                    setBusy(false);
                }
            }
        }.execute();
    }

    private void setBusy(boolean busy) {
        loginButton.setEnabled(!busy);
        registerButton.setEnabled(!busy);
        usernameField.setEnabled(!busy);
        passwordField.setEnabled(!busy);
        loginButton.setText(busy ? "登录中…" : "登 录");
    }
}
