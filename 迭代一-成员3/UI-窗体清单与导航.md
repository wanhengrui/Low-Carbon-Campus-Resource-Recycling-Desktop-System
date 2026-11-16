# 迭代一 · 成员3 界面骨架说明

> 状态：迭代一交付；只交付窗体清单、导航、事件规则与可运行骨架。  
> 完整业务页在迭代二/三实现。

## 1. 窗体清单（9+2）

| # | 窗体/面板 | 类名（规划） | 所属模块 | 迭代一状态 | 依赖 Controller |
|---|---|---|---|---|---|
| 1 | 登录 | `LoginFrame` | 用户 | 已实现 | `AppController.login` |
| 2 | 注册 | `RegisterDialog` | 用户 | 已实现 | `UserController.register` |
| 3 | 主窗体 | `MainFrame` | 全局 | 已实现 | `AppController`（会话） |
| 4 | 首页 | `HomePanel`（内嵌） | 全局 | 已实现 | 无 |
| 5 | 检索物品 | `ItemSearchPanel` | 物品/检索 | 占位 | `ItemController.search` |
| 6 | 物品详情/收藏 | `ItemDetailDialog` | 物品/检索 | 占位 | `ItemController.detail`、`AppController.toggleFavorite` |
| 7 | 发布/修改物品 | `PublishItemDialog` | 物品 | 占位 | `ItemController.publish/updateItem` |
| 8 | 我的物品 | `MyItemPanel` | 物品 | 占位 | 待补按 ownerId 查询方法 |
| 9 | 流转/消息 | `TradePanel` | 流转 | 占位 | `TradeController.*` |
| 10 | 评价/信用 | `ReviewDialog`、`ProfilePanel` | 评价/信用 | 占位 | `ReviewController`、`UserController.getCredit` |
| 11 | 统计/导出 | `StatisticPanel` | 统计 | 占位 | `StatisticController` |
| 12 | 管理后台 | `AdminPanel` | 管理员 | 占位（仅 ADMIN 可见） | `AdminController`、`UserController`、`ItemController` |

> 表 1 的 1—4 已在 `ui` 包实现；5—12 是迭代二/三的明确落点，不在迭代一强行实现。

## 2. 主界面导航结构

```text
LoginFrame
└─ 登录成功 → MainFrame
   ├─ 顶部：系统菜单 / 帮助菜单
   ├─ 头部：姓名 · 角色 · 信用分 · 退出登录
   ├─ 左侧：首页 / 检索物品 / 发布物品 / 我的物品 /
   │        流转记录 / 评价与信用 / 统计报表 /
   │        [管理员] 管理后台
   └─ 右侧：CardLayout 内容区
```

### 角色菜单规则

| 菜单 | STUDENT | TEACHER | ADMIN |
|---|---:|---:|---:|
| 首页、检索、发布、我的物品、流转、评价、统计 | ✓ | ✓ | ✓ |
| 管理后台 | — | — | ✓ |

- 管理员入口的双层防线：UI 隐藏菜单 + Controller/Service 的 `PermissionDeniedException`。
- 退出登录：`AppController.logout()` → 关闭 `MainFrame` → 新建 `LoginFrame`。

## 3. 窗体职责边界

- UI 只调用 `controller`，不 import `service`、`service.impl`、`dao`。
- UI 只读 `entity`、`dto` 用于展示。
- UI 只捕获 `AppException`（`getUserMessage()` 直接展示），不吞异常。
- 不在 UI 中写 SQL、`DriverManager`、`commit/rollback`。
- 所有耗时操作（登录、检索、发布、成交、导出）必须走 `SwingWorker`，见 `UI-事件流与SwingWorker规则.md`。

## 4. 迭代一最小验收

- `run-ui.bat` 启动后出现登录窗体；
- `admin / Admin@123` 或 `zhangsan / Student@123` 能登录；
- 主界面左侧导航可切换，右侧占位卡片随标题变化；
- 管理员登录能看到“管理后台”，学生看不到；
- 退出登录能回到登录窗体。
