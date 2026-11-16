package edu.campus.recycle.ui;

import edu.campus.recycle.controller.AppController;
import edu.campus.recycle.dto.LoginResult;

import javax.swing.BorderFactory;
import javax.swing.Box;
import javax.swing.BoxLayout;
import javax.swing.JButton;
import javax.swing.JFrame;
import javax.swing.JLabel;
import javax.swing.JMenu;
import javax.swing.JMenuBar;
import javax.swing.JMenuItem;
import javax.swing.JOptionPane;
import javax.swing.JPanel;
import javax.swing.JSeparator;
import javax.swing.SwingConstants;
import java.awt.BorderLayout;
import java.awt.CardLayout;
import java.awt.Color;
import java.awt.Dimension;
import java.awt.Font;
import java.awt.GridLayout;

/**
 * 主窗体骨架：菜单栏 + 左侧导航 + 右侧 CardLayout。
 *
 * <p>迭代一只实现导航和占位卡片；检索、发布、流转、评价、统计、管理页面
 * 在迭代二/三接入真实 Controller。管理员菜单按角色动态显示。</p>
 */
public class MainFrame extends JFrame {

    private final AppController appController;
    private final LoginResult loginResult;
    private final CardLayout cardLayout = new CardLayout();
    private final JPanel contentPanel = new JPanel(cardLayout);
    private final JLabel titleLabel = new JLabel("首页");

    public MainFrame(AppController appController, LoginResult loginResult) {
        super("绿色校园 · 工作台");
        this.appController = appController;
        this.loginResult = loginResult;
        setDefaultCloseOperation(EXIT_ON_CLOSE);
        setMinimumSize(new Dimension(1080, 700));
        setJMenuBar(buildMenuBar());
        setContentPane(buildContent());
        pack();
        setLocationRelativeTo(null);
        showCard("home", "首页");
    }

    private JMenuBar buildMenuBar() {
        JMenuBar bar = new JMenuBar();
        JMenu system = new JMenu("系统");
        JMenuItem logout = new JMenuItem("退出登录");
        logout.addActionListener(e -> logout());
        JMenuItem exit = new JMenuItem("退出");
        exit.addActionListener(e -> System.exit(0));
        system.add(logout);
        system.addSeparator();
        system.add(exit);

        JMenu help = new JMenu("帮助");
        JMenuItem about = new JMenuItem("关于");
        about.addActionListener(e -> JOptionPane.showMessageDialog(this,
                "绿色校园 · 闲置物品循环流转平台\n迭代一 Swing 界面骨架\n成员3：GUI / 复用 / 交付",
                "关于", JOptionPane.INFORMATION_MESSAGE));
        help.add(about);
        bar.add(system);
        bar.add(help);
        return bar;
    }

    private JPanel buildContent() {
        JPanel root = new JPanel(new BorderLayout());
        root.setBackground(UiTheme.BACKGROUND);
        root.add(buildHeader(), BorderLayout.NORTH);

        JPanel sidebar = buildSidebar();
        JPanel main = new JPanel(new BorderLayout());
        main.setBackground(UiTheme.BACKGROUND);
        main.setBorder(BorderFactory.createEmptyBorder(14, 18, 18, 18));

        JPanel titleBar = new JPanel(new BorderLayout());
        titleBar.setOpaque(false);
        titleLabel.setFont(new Font("Microsoft YaHei", Font.BOLD, 20));
        titleLabel.setForeground(UiTheme.NAVY);
        titleBar.add(titleLabel, BorderLayout.WEST);
        main.add(titleBar, BorderLayout.NORTH);
        main.add(contentPanel, BorderLayout.CENTER);

        contentPanel.setOpaque(false);
        contentPanel.add(buildHome(), "home");
        contentPanel.add(placeholder("检索物品", "关键词、分类、价格区间、排序、分页；"
                + "迭代二接入 ItemController.search。"), "search");
        contentPanel.add(placeholder("发布物品", "标题、分类、描述、交易方式、价格、成色、标签、图片；"
                + "迭代二接入 ItemController.publish。"), "publish");
        contentPanel.add(placeholder("我的物品", "我发布的物品、修改与下架；"
                + "待成员2补齐按 ownerId 查询的 Controller 方法后接入。"), "my-items");
        contentPanel.add(placeholder("流转记录", "我收到/我发起的申请、同意、成交、取消与历史；"
                + "迭代二接入 TradeController.historyDetail/agree/confirm/cancel。"), "trade");
        contentPanel.add(placeholder("评价与信用", "完成后互评、信用分与信用等级；"
                + "迭代二接入 ReviewController + UserController.getCredit。"), "review");
        contentPanel.add(placeholder("统计报表", "按分类统计流转数量/金额、碳减排估算与 CSV 导出；"
                + "迭代三接入 StatisticController。"), "statistics");

        if ("ADMIN".equalsIgnoreCase(loginResult.getRole())) {
            contentPanel.add(placeholder("管理后台", "用户冻结/解冻、物品审核/下架、分类维护、操作日志；"
                    + "迭代三接入 AdminController/UserController/ItemController。"), "admin");
        }

        root.add(sidebar, BorderLayout.WEST);
        root.add(main, BorderLayout.CENTER);
        return root;
    }

    private JPanel buildHeader() {
        JPanel header = new JPanel(new BorderLayout());
        header.setBackground(UiTheme.NAVY);
        header.setBorder(BorderFactory.createEmptyBorder(12, 18, 12, 18));

        JLabel brand = new JLabel("绿色校园  ·  资源循环");
        brand.setForeground(Color.WHITE);
        brand.setFont(new Font("Microsoft YaHei", Font.BOLD, 20));
        header.add(brand, BorderLayout.WEST);

        JPanel user = new JPanel(new GridLayout(1, 4, 12, 0));
        user.setOpaque(false);
        user.add(headerLabel(loginResult.getRealName() == null ? loginResult.getUsername() : loginResult.getRealName()));
        user.add(headerLabel(roleLabel(loginResult.getRole())));
        user.add(headerLabel("信用分 " + loginResult.getCreditScore()));
        JButton logout = UiTheme.secondaryButton("退出登录");
        logout.addActionListener(e -> logout());
        user.add(logout);
        header.add(user, BorderLayout.EAST);
        return header;
    }

    private JLabel headerLabel(String text) {
        JLabel label = new JLabel(text, SwingConstants.CENTER);
        label.setForeground(new Color(226, 232, 240));
        label.setFont(new Font("Microsoft YaHei", Font.PLAIN, 12));
        return label;
    }

    private JPanel buildSidebar() {
        JPanel sidebar = new JPanel();
        sidebar.setBackground(new Color(244, 239, 229));
        sidebar.setBorder(BorderFactory.createEmptyBorder(18, 12, 18, 12));
        sidebar.setLayout(new BoxLayout(sidebar, BoxLayout.Y_AXIS));
        sidebar.setPreferredSize(new Dimension(184, 0));

        addNav(sidebar, "首页", "home");
        addNav(sidebar, "检索物品", "search");
        addNav(sidebar, "发布物品", "publish");
        addNav(sidebar, "我的物品", "my-items");
        addNav(sidebar, "流转记录", "trade");
        addNav(sidebar, "评价与信用", "review");
        addNav(sidebar, "统计报表", "statistics");
        if ("ADMIN".equalsIgnoreCase(loginResult.getRole())) {
            sidebar.add(new JSeparator());
            addNav(sidebar, "管理后台", "admin");
        }
        sidebar.add(Box.createVerticalGlue());
        JLabel version = new JLabel("迭代一 · 成员3 骨架");
        version.setForeground(UiTheme.MUTED);
        version.setFont(new Font("Microsoft YaHei", Font.PLAIN, 11));
        version.setAlignmentX(LEFT_ALIGNMENT);
        sidebar.add(version);
        return sidebar;
    }

    private void addNav(JPanel sidebar, String text, String card) {
        JButton button = new JButton(text);
        button.setHorizontalAlignment(SwingConstants.LEFT);
        button.setMaximumSize(new Dimension(Integer.MAX_VALUE, 38));
        button.setBackground(Color.WHITE);
        button.setForeground(UiTheme.INK);
        button.setFocusPainted(false);
        button.setBorder(BorderFactory.createCompoundBorder(
                BorderFactory.createLineBorder(UiTheme.BORDER),
                BorderFactory.createEmptyBorder(8, 12, 8, 12)));
        button.addActionListener(e -> showCard(card, text));
        sidebar.add(button);
        sidebar.add(Box.createVerticalStrut(6));
    }

    private JPanel buildHome() {
        JPanel panel = new JPanel();
        panel.setOpaque(false);
        panel.setLayout(new BoxLayout(panel, BoxLayout.Y_AXIS));
        JLabel welcome = new JLabel("你好，" + (loginResult.getRealName() == null
                ? loginResult.getUsername() : loginResult.getRealName()));
        welcome.setFont(new Font("Microsoft YaHei", Font.BOLD, 26));
        welcome.setForeground(UiTheme.NAVY);
        JLabel sub = new JLabel("欢迎使用绿色校园资源循环流转平台。");
        sub.setForeground(UiTheme.MUTED);
        sub.setFont(new Font("Microsoft YaHei", Font.PLAIN, 14));
        panel.add(welcome);
        panel.add(Box.createVerticalStrut(6));
        panel.add(sub);
        panel.add(Box.createVerticalStrut(24));

        JPanel card = new JPanel();
        UiTheme.cardBorder(card);
        card.setLayout(new BoxLayout(card, BoxLayout.Y_AXIS));
        JLabel cardTitle = new JLabel("迭代一交付：可运行骨架");
        cardTitle.setFont(new Font("Microsoft YaHei", Font.BOLD, 16));
        cardTitle.setForeground(UiTheme.GREEN);
        card.add(cardTitle);
        card.add(Box.createVerticalStrut(10));
        card.add(line("✓ 登录真实走 UserController / AppController 与 SQLite 种子账号。"));
        card.add(line("✓ 主界面采用菜单 + 左侧导航 + CardLayout，按角色显示管理员入口。"));
        card.add(line("✓ 业务页面为占位卡片；检索、发布、流转、评价、统计、管理在迭代二/三接入。"));
        card.add(line("✓ 所有耗时操作统一使用 SwingWorker，不在 EDT 中访问数据库。"));
        card.add(Box.createVerticalStrut(12));
        JLabel hint = new JLabel("演示账号：admin / Admin@123　或　zhangsan / Student@123");
        hint.setForeground(UiTheme.MUTED);
        hint.setFont(new Font("Microsoft YaHei", Font.PLAIN, 12));
        card.add(hint);
        panel.add(card);
        panel.add(Box.createVerticalGlue());
        return panel;
    }

    private JLabel line(String text) {
        JLabel label = new JLabel(text);
        label.setForeground(UiTheme.INK);
        label.setFont(new Font("Microsoft YaHei", Font.PLAIN, 13));
        label.setBorder(BorderFactory.createEmptyBorder(3, 0, 3, 0));
        return label;
    }

    private JPanel placeholder(String name, String description) {
        JPanel panel = new JPanel(new BorderLayout());
        panel.setOpaque(false);
        JPanel card = new JPanel();
        UiTheme.cardBorder(card);
        card.setLayout(new BoxLayout(card, BoxLayout.Y_AXIS));
        JLabel title = new JLabel(name + "（迭代二/三接入）");
        title.setFont(new Font("Microsoft YaHei", Font.BOLD, 18));
        title.setForeground(UiTheme.NAVY);
        JLabel desc = new JLabel("<html><body style='width:640px'>" + description + "</body></html>");
        desc.setForeground(UiTheme.MUTED);
        desc.setFont(new Font("Microsoft YaHei", Font.PLAIN, 13));
        card.add(title);
        card.add(Box.createVerticalStrut(12));
        card.add(desc);
        card.add(Box.createVerticalStrut(18));
        JLabel notice = new JLabel("占位页：迭代一仅交付导航壳，不实现本页业务。");
        notice.setForeground(UiTheme.GREEN);
        notice.setFont(new Font("Microsoft YaHei", Font.PLAIN, 12));
        card.add(notice);
        panel.add(card, BorderLayout.NORTH);
        return panel;
    }

    private void showCard(String card, String title) {
        cardLayout.show(contentPanel, card);
        titleLabel.setText(title);
    }

    private void logout() {
        int choice = JOptionPane.showConfirmDialog(this, "确认退出当前账号？", "退出登录",
                JOptionPane.YES_NO_OPTION);
        if (choice != JOptionPane.YES_OPTION) {
            return;
        }
        appController.logout();
        dispose();
        new LoginFrame(appController).setVisible(true);
    }

    private String roleLabel(String role) {
        if ("ADMIN".equalsIgnoreCase(role)) {
            return "管理员";
        }
        if ("TEACHER".equalsIgnoreCase(role)) {
            return "教师";
        }
        return "学生";
    }
}
