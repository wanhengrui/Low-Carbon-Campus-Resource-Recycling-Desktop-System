package edu.campus.recycle.ui;

import javax.swing.BorderFactory;
import javax.swing.JButton;
import javax.swing.JComponent;
import javax.swing.UIManager;
import javax.swing.plaf.FontUIResource;
import java.awt.Color;
import java.awt.Font;
import java.util.Enumeration;

/**
 * 成员3的界面主题与公共样式。
 *
 * <p>只做 Swing 外观统一，不包含业务逻辑；业务调用全部经 controller 完成。</p>
 */
public final class UiTheme {

    public static final Color NAVY = new Color(21, 34, 56);
    public static final Color GREEN = new Color(31, 111, 92);
    public static final Color GREEN_LIGHT = new Color(234, 244, 239);
    public static final Color GOLD = new Color(217, 164, 65);
    public static final Color CREAM = new Color(244, 239, 229);
    public static final Color INK = new Color(32, 42, 54);
    public static final Color MUTED = new Color(107, 114, 128);
    public static final Color BORDER = new Color(217, 210, 198);
    public static final Color BACKGROUND = new Color(251, 248, 242);

    private UiTheme() {
    }

    /** 安装系统外观、统一中文字体与常用控件字体。 */
    public static void install() {
        try {
            UIManager.setLookAndFeel(UIManager.getSystemLookAndFeelClassName());
        } catch (Exception ignored) {
            // 系统外观不可用时使用 Swing 默认外观，不影响功能。
        }
        FontUIResource font = new FontUIResource("Microsoft YaHei", Font.PLAIN, 14);
        Enumeration<Object> keys = UIManager.getDefaults().keys();
        while (keys.hasMoreElements()) {
            Object key = keys.nextElement();
            if (UIManager.get(key) instanceof FontUIResource) {
                UIManager.put(key, font);
            }
        }
        UIManager.put("OptionPane.messageFont", font);
        UIManager.put("OptionPane.buttonFont", font);
        UIManager.put("TextField.font", font);
        UIManager.put("PasswordField.font", font);
        UIManager.put("Table.font", font);
        UIManager.put("TableHeader.font", font);
        UIManager.put("Label.font", font);
        UIManager.put("Button.font", font);
    }

    /** 主操作按钮：深绿色底、白字。 */
    public static JButton primaryButton(String text) {
        JButton button = new JButton(text);
        button.setBackground(GREEN);
        button.setForeground(Color.WHITE);
        button.setOpaque(true);
        button.setBorder(BorderFactory.createEmptyBorder(9, 18, 9, 18));
        button.setFocusPainted(false);
        button.setFont(new Font("Microsoft YaHei", Font.BOLD, 14));
        return button;
    }

    /** 次要按钮：白底、深色边。 */
    public static JButton secondaryButton(String text) {
        JButton button = new JButton(text);
        button.setBackground(Color.WHITE);
        button.setForeground(INK);
        button.setOpaque(true);
        button.setBorder(BorderFactory.createCompoundBorder(
                BorderFactory.createLineBorder(BORDER),
                BorderFactory.createEmptyBorder(8, 16, 8, 16)));
        button.setFocusPainted(false);
        return button;
    }

    /** 统一给卡片/面板加浅色边框。 */
    public static void cardBorder(JComponent component) {
        component.setBorder(BorderFactory.createCompoundBorder(
                BorderFactory.createLineBorder(BORDER),
                BorderFactory.createEmptyBorder(18, 20, 18, 20)));
        component.setBackground(Color.WHITE);
    }
}
