# 低碳校园资源循环流转桌面系统（GreenCampus Recycle）

> 《软件构造》课程分组实验（3 人组 · 8 周 4 迭代）· Java 17 + Maven + SQLite/JDBC + Swing + JUnit 5

面向校园的二手闲置物品流转桌面应用：**发布 → 检索收藏 → 意向沟通 → 流转成交 → 互评与信用分 → 数据统计与低碳减排估算**，管理员负责用户与物品审核。当前进度：**迭代一（第 1–2 周，需求与设计）已交付**。

---

## 一、仓库结构

```
软件构造/
├─ 2026软件构造分组实验v3.docx      # 题目书（老师原始要求，唯一需求来源）
├─ README.md                        # 本文件
├─ .gitignore
└─ 迭代一-成员1/                    # 迭代一交付物（成员1：系统设计与数据层）
   ├─ README-交付说明.md            # ★ 交付总入口：阅读顺序 / 验证命令 / 待确认项
   ├─ _共享契约-实体与接口基线.md   # ★ 全组唯一口径：11 张表字段、接口签名、BR、异常、裁决记录
   ├─ docs/                         # 00 能力自检与编排方案｜01 需求规格｜02 模块化设计与接口规范｜05 数据库设计｜06 分工与迭代计划
   ├─ design/                       # 03 UML 类图｜04 UML 时序图｜05 ER 图（均为 .drawio，可继续编辑）
   ├─ db/                           # schema.sql｜seed-data.sql｜_verify/（验证库与实测输出）
   ├─ code/green-campus/            # Maven 工程骨架（12 包 109 个源文件，可编译可运行）
   └─ _tools/                       # 交付自检与交叉校验脚本、第 3 轮修复裁决清单
```

---

## 二、组员快速上手（第一次克隆）

```bash
# 1) 克隆（国内网络若报 Connection was reset，用下一行带代理的版本）
git clone https://github.com/wanhengrui/Low-Carbon-Campus-Resource-Recycling-Desktop-System.git
git -c http.proxy=http://127.0.0.1:7897 clone https://github.com/wanhengrui/Low-Carbon-Campus-Resource-Recycling-Desktop-System.git

# 2) 进入仓库，先读交付总入口
cd Low-Carbon-Campus-Resource-Recycling-Desktop-System/迭代一-成员1
#    打开 README-交付说明.md（阅读顺序：D0 → D2 → D3/D4 → D5 → D1 → D6）

# 3) 跑一遍演示，确认环境没问题
cd code/green-campus && start.bat
```

> 首次使用前请组内先确认：①仓库 Settings → Collaborators 已把成员2/3 加进来（否则无法 push）；②各自 `git config user.name` / `user.email` 已设置为本人；③**动手前先看 [_共享契约-实体与接口基线.md](迭代一-成员1/_共享契约-实体与接口基线.md)**，那是全组唯一口径。

---

## 三、快速开始（三种方式，任选一种）

**① 双击运行（推荐给组员/答辩现场）**

```bat
cd 迭代一-成员1\code\green-campus
start.bat
```

`start.bat` 会自动三级回退：已有 `target/*.jar` → 直接 `java -jar`；有 Maven → `mvn -q -DskipTests package` 后运行；两者都没有 → 用 `lib/sqlite-jdbc-3.42.0.0.jar` 走 `javac` 离线编译再运行。会打印 9 步演示流程（注册 → 登录 → 发布 → 检索 → 意向 → 成交 → 评价 → 统计 → CSV 导出）。

**② Maven 方式**

```bash
mvn -q -DskipTests package
java -jar target/green-campus-1.0.0.jar
mvn test
```

**③ 手工编译（无 Maven 环境）**

```bash
javac --release 17 -encoding UTF-8 -sourcepath src/main/java -d build/classes \
      -cp "lib/sqlite-jdbc-3.42.0.0.jar" src/main/java/edu/campus/recycle/Main.java
java -cp "build/classes;src/main/resources;lib/sqlite-jdbc-3.42.0.0.jar" edu.campus.recycle.Main
```

> ⚠️ **两个必须注意的点**（否则会报"建库脚本不存在"或读不到配置）：
> 1. 工作目录必须是 `code/green-campus`（`DbConfig` 默认按 `../../db/schema.sql` 找建库脚本）；
> 2. classpath 必须包含 `src/main/resources`（否则 `application.properties` 被静默跳过，改用内置默认值）。
> 详细说明见 [`迭代一-成员1/code/green-campus/部署说明.md`](迭代一-成员1/code/green-campus/部署说明.md)。

---

## 四、迭代一交付物索引

| 编号 | 交付物 | 内容要点 | 负责人 |
|---|---|---|---|
| D0 | `docs/00-能力自检与编排方案.docx` | 本机工具链实测、编排与多模型分工、三轮生成–自检–修复记录 | 成员1 |
| D1 | `docs/01-需求规格说明书.docx` | FR-01…17、NFR-01…10、BR-01…12、UC-01…08、权限矩阵、错误码总表 | 成员1 |
| D2 | `docs/02-模块化设计与接口规范.docx` | 分层架构、12 包、**22 接口 92 方法**签名、5 处设计模式落点、成员2/3 开工契约 | 成员1 |
| D3 | `design/03-UML类图.drawio` | 实体/DAO/Service/工具/异常全量类图，412 mxCell、312 顶点、96 条关系 | 成员1 |
| D4 | `design/04-UML时序图.drawio` | 6 个核心场景，含 alt/loop 与事务回滚分支 | 成员1 |
| D5 | `docs/05-数据库设计说明书.docx` + `design/05-ER图.drawio` + `db/schema.sql` + `db/seed-data.sql` | 11 表 93 列 13 索引 18 外键、事务边界、可实跑建库脚本 | 成员1 |
| D6 | `docs/06-小组分工与两周迭代计划.docx` | 三人分工、14 天排期、迭代二交接、Git 约定、风险应对 | 成员1（含成员2/3 建议分工） |
| D7 | `code/green-campus/` | Maven 骨架 + 可跑 Main（控制台版，Swing 留给成员3） | 成员1（骨架） |
| D8 | `README-交付说明.md` + `_tools/` | 一致性交叉校验、20 项自动化验收、第 3 轮 v4-pro 评审修复记录 | 成员1 |

**已实测**：`javac --release 17` 107 文件 0 错误 · JUnit 11/11 通过 · `Main` 9/9 步跑通 · `schema.sql` 11 表实跑 `integrity_check=ok`、`foreign_key_check` 无违规 · 12/12 非法数据被库层拒绝 · 双击 `start.bat` 同样跑通。

---

## 五、组内协作约定（迭代二起执行）

- **唯一口径**：任何字段、接口签名、业务规则以 [`_共享契约-实体与接口基线.md`](迭代一-成员1/_共享契约-实体与接口基线.md) 为准；文档之间冲突时以契约为准并提 issue 更正。
- **分支模型**：`main` 保持可编译可运行；成员2 用 `feature/service-test`、成员3 用 `feature/ui`，合并前必须本地 `mvn test` 通过 + 一次代码走查。
- **提交信息**：`<类型>(<范围>): <说明>`，例如 `feat(service): 实现 TradeService.confirm 跨表事务`、`docs(iter1): 补充 D2 接口清单`。
- **不要提交**：`target/`、`build/`、`*.class`、`__pycache__/`、IDE 配置、运行生成的 `*.db`（`.gitignore` 已覆盖）。
- **依赖 jar**：`code/green-campus/lib/sqlite-jdbc-3.42.0.0.jar` 已入库，保证无 Maven 环境也能一键运行，请勿删除。

---

## 六、网络提示（仅对国内网络环境）

若 `git push` 报 `Recv failure: Connection was reset`，说明直连 GitHub 不通，请临时走本地代理：

```bash
git -c http.proxy=http://127.0.0.1:7897 -c https.proxy=http://127.0.0.1:7897 push -u origin main
```

（代理地址按自己实际情况替换；本机 Clash 默认 `127.0.0.1:7897`。）
