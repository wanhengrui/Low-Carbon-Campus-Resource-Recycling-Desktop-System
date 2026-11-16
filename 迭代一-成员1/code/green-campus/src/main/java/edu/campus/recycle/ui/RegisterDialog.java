package edu.campus.recycle.ui;

import edu.campus.recycle.controller.UserController;

import javax.swing.BorderFactory;
import javax.swing.JButton;
import javax.swing.JDialog;
import javax.swing.JFrame;
import javax.swing.JLabel;
import javax.swing.JOptionPane;
import javax.swing.JPanel;
import javax.swing.JPasswordField;
import javax.swing.JTextField;
import javax.swing.SwingWorker;
import java.awt.BorderLayout;
import java.awt.Dimension;
import java.awt.Font;
import java.awt.GridBagConstraints;
import java.awt.GridBagLayout;
import java.awt.Insets;
import java.util.concurrent.ExecutionException;

/**
 * 注册对话框（迭代一成员3骨架）。
 *
 * <p>角色固定为学生；用户名/密码/学号的最终校验仍由 UserService 负责，
 * 本类只做必填与两次密码一致的界面提示，避免重复业务规则。</p>
 */
public class RegisterDialog extends JDialog {

    private final UserController userController;
    private final JTextField usernameField = new JTextField(18);
    private final JPasswordField passwordField = new JPasswordField(18);
    private final JPasswordField confirmField = new JPasswordField(18);
    private final JTextField realNameField = new JTextField(18);
    private final JTextField studentNoField = new JTextField(18);
    private final JTextField collegeField = new JTextField(18);
    private final JTextField contactField = new JTextField(18);
    private final JButton submitButton = UiTheme.primaryButton("注 册");
    private final JLabel statusLabel = new JLabel(" ");

    public RegisterDialog(JFrame owner, UserController userController) {
        super(owner, "注册新账号", true);
        this.userController = userController;
        setMinimumSize(new Dimension(520, 470));
        setContentPane(buildContent());
        pack();
        setLocationRelativeTo(owner);
        submitButton.addActionListener(e -> doRegister());
    }

    private JPanel buildContent() {
        JPanel root = new JPanel(new BorderLayout(0, 12));
        root.setBackground(UiTheme.BACKGROUND);
        root.setBorder(BorderFactory.createEmptyBorder(20, 28, 20, 28));

        JLabel title = new JLabel("注册学生账号");
        title.setFont(new Font("Microsoft YaHei", Font.BOLD, 20));
        title.setForeground(UiTheme.NAVY);
        root.add(title, BorderLayout.NORTH);

        JPanel form = new JPanel(new GridBagLayout());
        form.setOpaque(false);
        GridBagConstraints gbc = new GridBagConstraints();
        gbc.gridx = 0;
        gbc.gridy = 0;
        gbc.anchor = GridBagConstraints.WEST;
        gbc.insets = new Insets(5, 0, 5, 12);
        addRow(form, gbc, "用户名", usernameField);
        addRow(form, gbc, "密  码", passwordField);
        addRow(form, gbc, "确认密码", confirmField);
        addRow(form, gbc, "真实姓名", realNameField);
        addRow(form, gbc, "学  号", studentNoField);
        addRow(form, gbc, "学  院", collegeField);
        addRow(form, gbc, "联系方式", contactField);

        gbc.gridx = 0;
        gbc.gridy++;
        gbc.gridwidth = 2;
        gbc.fill = GridBagConstraints.HORIZONTAL;
        gbc.insets = new Insets(14, 0, 4, 0);
        form.add(submitButton, gbc);
        gbc.gridy++;
        gbc.insets = new Insets(2, 0, 0, 0);
        statusLabel.setForeground(new java.awt.Color(180, 60, 45));
        form.add(statusLabel, gbc);

        root.add(form, BorderLayout.CENTER);
        JLabel hint = new JLabel("提示：密码 8—20 位且同时包含字母与数字；学号 8—12 位数字。");
        hint.setForeground(UiTheme.MUTED);
        hint.setFont(new Font("Microsoft YaHei", Font.PLAIN, 11));
        root.add(hint, BorderLayout.SOUTH);
        return root;
    }

    private void addRow(JPanel form, GridBagConstraints gbc, String label, JTextField field) {
        gbc.gridx = 0;
        gbc.gridwidth = 1;
        gbc.weightx = 0;
        gbc.fill = GridBagConstraints.NONE;
        form.add(new JLabel(label), gbc);
        gbc.gridx = 1;
        gbc.weightx = 1;
        gbc.fill = GridBagConstraints.HORIZONTAL;
        form.add(field, gbc);
        gbc.gridy++;
    }

    private void doRegister() {
        String username = usernameField.getText().trim();
        String password = new String(passwordField.getPassword());
        String confirm = new String(confirmField.getPassword());
        String realName = realNameField.getText().trim();
        String studentNo = studentNoField.getText().trim();
        String college = collegeField.getText().trim();
        String contact = contactField.getText().trim();

        if (username.isEmpty() || password.isEmpty() || realName.isEmpty() || studentNo.isEmpty()) {
            statusLabel.setText("用户名、密码、真实姓名、学号不能为空");
            return;
        }
        if (!password.equals(confirm)) {
            statusLabel.setText("两次输入的密码不一致");
            confirmField.selectAll();
            return;
        }
        setBusy(true);
        statusLabel.setText("正在注册…");
        new SwingWorker<String, Void>() {
            @Override
            protected String doInBackground() {
                return userController.register(username, password, realName, studentNo,
                        "STUDENT", college, contact);
            }

            @Override
            protected void done() {
                try {
                    String message = get();
                    if (message != null && message.startsWith("注册成功")) {
                        JOptionPane.showMessageDialog(RegisterDialog.this,
                                message + "\n请使用新账号登录。", "注册成功",
                                JOptionPane.INFORMATION_MESSAGE);
                        dispose();
                    } else {
                        statusLabel.setText(message == null ? "注册失败" : message);
                    }
                } catch (InterruptedException ex) {
                    Thread.currentThread().interrupt();
                    statusLabel.setText("注册被中断");
                } catch (ExecutionException ex) {
                    Throwable cause = ex.getCause();
                    statusLabel.setText(cause == null ? "注册失败" : cause.getMessage());
                } finally {
                    setBusy(false);
                }
            }
        }.execute();
    }

    private void setBusy(boolean busy) {
        submitButton.setEnabled(!busy);
        submitButton.setText(busy ? "注册中…" : "注 册");
    }
}
