# 迭代一 · 成员3 交付说明（UI / 复用 / 交付）

> 分支：`feature/ui`  
> 范围：迭代一第 1—2 周，成员3 只交付 **界面骨架 + 设计说明 + 构建方案 + 仓库/演示材料**。  
> 不包含：完整的检索、发布、流转、评价、统计、管理后台业务实现（迭代二/三完成）。

## 1. 本次实际完成内容

| 交付项 | 文件/代码 | 状态 |
|---|---|---|
| Swing 启动入口 | `code/green-campus/src/main/java/edu/campus/recycle/ui/MainApp.java` | 已实现 |
| 登录窗体 | `ui/LoginFrame.java` | 已实现，真实调用 `AppController.login` |
| 注册对话框 | `ui/RegisterDialog.java` | 已实现，调用 `UserController.register`（学生角色） |
| 主界面骨架 | `ui/MainFrame.java` | 已实现：菜单 + 左侧导航 + CardLayout + 角色菜单 |
| 统一主题 | `ui/UiTheme.java` | 已实现 |
| UI 启动脚本 | `code/green-campus/run-ui.bat` | 已实现 |
| 界面/复用说明 | `docs/07-界面骨架与复用说明.docx` | 已生成 |
| 部署说明初稿 | `docs/08-部署说明初稿.docx` | 已生成 |
| 快速阅读文档 | `README-UI交付.md`、`UI-窗体清单与导航.md`、`UI-事件流与SwingWorker规则.md`、`复用设计说明.md`、`构建与部署方案.md`、`演示PPT与视频脚本大纲.md` | 已生成 |

## 2. 如何运行

前置：JDK 17+；`lib/sqlite-jdbc-3.42.0.0.jar` 已由成员1入库。

```bat
cd 迭代一-成员1\code\green-campus
run-ui.bat
```

`run-ui.bat` 会：

1. 定位 `lib/sqlite-jdbc-*.jar`；
2. 优先用 `javac --release 17` 编译，失败时回退到当前 JDK；
3. 启动 `edu.campus.recycle.ui.MainApp`。

首次启动会建 `data/greencampus.db` 并导入 seed；之后启动若数据库已存在则跳过初始化，不重置数据。需要重置演示数据：

```bat
run-ui.bat --reset-db
```

## 3. 演示账号

| 账号 | 密码 | 角色 | 用途 |
|---|---|---|---|
| `admin` | `Admin@123` | ADMIN | 验证登录、管理员菜单可见 |
| `zhangsan` | `Student@123` | STUDENT | 验证普通学生菜单 |

> 仅用于课程验收演示；生产环境必须修改。密码来自 D5 数据库设计说明书的演示口令表，数据库中只存 PBKDF2 摘要。

## 4. 已验证

- `MainApp.java` 及其依赖在 JDK 11 下编译通过（本机环境只有 JDK 11；源码保持 Java 17 目标，`run-ui.bat` 优先 `--release 17`）。
- 启动 `MainApp` 能完成建库/seed，进程保持运行并显示登录窗体，无启动异常。
- 登录走 `AppController.login`，成功后进入 `MainFrame`；管理员登录会多出“管理后台”导航。
- 未做完整业务页：检索/发布/流转/评价/统计/管理均为占位卡片。

## 5. 与成员1/2的交接边界

- UI 不直接依赖 `service` / `dao` / `service.impl`，只依赖 `controller`、`dto`、`entity`、`exception`。
- 成员3 **没有修改** 成员1 的 entity/dao/service/controller/db/design/docs 文件。
- 新增文件仅在 `ui` 包、`run-ui.bat` 和 `迭代一-成员3/` 下。
- 迭代二起，成员3 按 `UI-窗体清单与导航.md` 的顺序接入真实 Controller；`pom.xml` 的 `main.class` 从 `Main` 切换到 `ui.MainApp` 前，必须先保证 `run-ui.bat` 和 `mvn test` 均通过。

## 6. 已知限制

- `MainApp` 只在默认数据库文件 `data/greencampus.db` 不存在时初始化；自定义 `db.url` 时不适用，需要后续补 `DatabaseInitializer.isInitialized()` 或迁移脚本。
- fat jar 尚未打包；`DbConfig` 的 `../../db/schema.sql` 在 jar 外运行时仍需要外部 `db/` 目录，迭代四交付时再处理资源内置。
- `UserController` 的注册/审核/发布等操作返回 String 文案，UI 目前按“成功前缀”判断注册结果；迭代二建议成员1/2 统一为 typed result，避免解析文案。
- 未实现完整的 `SwingWorker` 业务页；骨架中登录/注册已用 `SwingWorker`，其余页面在迭代二接入时统一使用同一模板。
