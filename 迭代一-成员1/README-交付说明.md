# 迭代一 · 成员1 交付说明（先读这一份）

> 课题：低碳校园资源循环流转桌面系统（Java 17 + Maven + SQLite + JDBC + Swing + JUnit 5）
> 角色：成员1 —— 系统设计与数据层负责人
> 迭代一（第 1–2 周）职责：需求梳理、UML 建模、数据库表设计、JDBC 数据层、设计文档
> 版本：v1.1 / 2026-11-02　｜　全部文件均已实测通过，验证命令见第 4 节

---

## 1. 阅读顺序（30 分钟看懂全部）

| 顺序 | 文件 | 看什么 |
|---|---|---|
| 1 | `README-交付说明.md` | 本文件：交付清单、验证结果、待确认项 |
| 2 | `docs\00-能力自检与编排方案.docx` | 本机插件/工具/模型实测、任务分解、三轮"生成-自检-修复"记录、一致性对照表、评分覆盖、效率总结（兼作第 1 周周报素材） |
| 3 | `docs\01-需求规格说明书.docx` | FR-01…FR-17、NFR-01…NFR-10、UC-01…UC-08、权限矩阵、BR-01…BR-12、错误码总表（85 行）、追踪矩阵 |
| 4 | `docs\02-模块化设计与接口规范.docx` | 分层架构、12 个包、模块划分、**22 个接口 92 个方法的签名清单**、异常体系、设计模式落点、成员2/3 开工契约 |
| 5 | `design\03-UML类图.drawio` | 2 页、312 个图元、96 条关系（右侧栏 draw.io 打开可直接编辑） |
| 6 | `design\04-UML时序图.drawio` | 6 个核心场景（登录锁定 / 发布含图片 / 检索收藏 / 成交跨表事务含回滚 / 评价信用分 / 管理员下架） |
| 7 | `docs\05-数据库设计说明书.docx`＋`design\05-ER图.drawio` | 11 张表数据字典（93 列）、约束与索引理由、事务边界、ER 图 |
| 8 | `db\schema.sql`＋`db\seed-data.sql` | 可重复执行的建库脚本与演示数据（单事务导入） |
| 9 | `docs\06-小组分工与两周迭代计划.docx` | 三人分工、D1–D14 排期与里程碑 M1–M4、迭代二交接清单、Git 约定、风险与砍功能顺序 |
| 10 | `code\green-campus\` | Maven 工程骨架：107 个主源码文件 + 2 个测试类，可编译、可运行控制台演示（Swing 留给成员3）；`start.bat` 双击启动，`部署说明.md` 给全套命令 |

---

## 2. 目录结构

```
迭代一-成员1\
├─ README-交付说明.md              ← 本文件
├─ _共享契约-实体与接口基线.md      ← 全组唯一口径（字段/接口/异常/BR/写域/第 3 轮裁决 §13，队友禁改）
├─ docs\  00 能力自检与编排方案 / 01 需求规格 / 02 模块化设计与接口规范 / 05 数据库设计 / 06 分工与迭代计划
├─ design\ 03 UML类图 / 04 UML时序图 / 05 ER图（均为 .drawio，可直接编辑）
├─ db\    schema.sql / seed-data.sql / _verify-output.txt（13 节真实执行记录）/ 生成与校验脚本 / _verify\（验证库）
├─ code\green-campus\  pom.xml + start.bat + 部署说明.md + src\main\java（12 个包）+ src\test\java（2 个测试类）
│                      + lib\sqlite-jdbc-3.42.0.0.jar（离线演示用驱动副本）+ data\（运行产物）
└─ _tools\  verify_all.py / cross_check.py / gen_d0.py / fix_revision.py / 裁决-第3轮修复清单.md / review\（评审输入提取）+ 各脚本输出
```

> `db\` 与 `_tools\` 下的 `.py` 均为**生成与校验脚本**：docx 正文里的每个数字都可由脚本重跑复现，不是手写估值。`_共享契约` 是给成员2/3 的唯一口径文件；`_tools\裁决-第3轮修复清单.md` 是第 3 轮 45 条修复的逐条账目。

---

## 3. 交付物清单与产出者

| 编号 | 文件 | 规模 | 产出者 · 模型 · 轮次 |
|---|---|---|---|
| D0 | `docs\00-能力自检与编排方案.docx` | 59.7 KB / 80 段 / 31 标题 / 22 表 | Lead（成员1）自写 `gen_d0.py` 生成 · deepseek-flash · 第 3 轮 |
| D1 | `docs\01-需求规格说明书.docx` | 112.9 KB / 238 段 / 85 标题 / 63 表 | doc-writer 队友 · deepseek-flash · 第 3 轮 |
| D2 | `docs\02-模块化设计与接口规范.docx` | 100.9 KB / 332 段 / 45 表 / 22 接口 92 方法 | arch-modeler 队友 · deepseek-flash · 第 3 轮 |
| D3 | `design\03-UML类图.drawio` | 175 KB / 2 页 / 412 mxCell（312 顶点 / 96 边） | arch-modeler 队友 · deepseek-flash · 第 3 轮 |
| D4 | `design\04-UML时序图.drawio` | 105 KB / 6 页 / 274 mxCell | arch-modeler 队友 · deepseek-flash · 第 2 轮 |
| D5 | `docs\05-数据库设计说明书.docx`＋`design\05-ER图.drawio`＋`db\*.sql` | 106.6 KB / 929 段 / 38 表；ER 162 mxCell；schema 310 行 | data-layer 队友 · deepseek-flash · 第 3 轮 |
| D6 | `docs\06-小组分工与两周迭代计划.docx` | 63.6 KB / 114 段 / 35 标题 / 18 表 | doc-writer 队友 · deepseek-flash · 第 3 轮（Lead 补 D5/D7 文件口径） |
| D7 | `code\green-campus\` | 107 主源码（7,621 行）+ 2 测试类（102 行）/ 12 包 | data-layer 队友 · deepseek-flash · 第 3 轮；`start.bat`/`部署说明.md`/端到端复测由 Lead 补做 |
| D8 | 一致性交叉校验 + 评委视角评审 | `_tools\cross_check.txt` + `docs\00` 第 4–5 章 | Lead 脚本 + 3 名 deepseek-v4-pro 评审子代理 |

每份 docx 文末均有 `【生成：模型 / 角色 / 第 N 轮】` 注记，答辩时可直接说明人机分工。

---

## 4. 验证方法与实测结果（可逐条复现）

```powershell
$py = "C:\Users\wanhe\.dsh\dsh-runtimes\dsh-primary-runtime\dependencies\python\python.exe"
cd C:\Users\wanhe\Desktop\软件构造\迭代一-成员1\_tools
& $py verify_all.py            # docx / drawio / db / code 四段检查，合计 20 项
& $py cross_check.py           # 类图字段 = 表字段 = 接口签名 = 需求编号 四条链
```

| 检查项 | 结果 |
|---|---|
| 5 份 docx 可打开、标题层级、表号、页脚 PAGE 域、文末生成注记 | **PASS 5 / FAIL 0** |
| 3 份 .drawio XML 合法（ElementTree 解析） | **PASS 3 / FAIL 0**（412 / 274 / 162 mxCell） |
| `schema.sql` 在 SQLite 实跑 | **11/11 表**、`integrity_check=ok`、`foreign_key_check` 空、13 索引、18 外键、93 列 |
| `seed-data.sql` 导入 | user 5 / category 10 / item 12 / item_image 7 / favorite 6 / trade_message 6 / trade_flow 4 / review 3 / credit_log 5 / operation_log 7 / system_config 11 |
| 非法数据反例（CHECK/UNIQUE/FK 违例） | **12/12 全部被拒绝**（含 `ck_item_free_price`「FREE 必须 0 元」） |
| 代码包结构与文件数 | **PASS 10 / FAIL 0**（12 个包齐全，109 个 .java） |
| `javac --release 17` 编译主源码 | **exit=0，0 错误**，107 个源文件 → 109 个 .class（纯 JDK 符号，零 classpath；本机 JDK 为 25，故必须带 `--release 17`） |
| JUnit 5 用例 | **11 tests / 11 successful / 0 failed** |
| 运行 `Main` 控制台演示（Lead 亲自复测两遍：java 直接跑 + 双击 `start.bat`） | **9/9 步**：注册→登录→发布（PENDING、未写上架时间）→管理员审核（ON_SALE、写上架时间）→按信用优先排序检索→申请（APPLYING）→同意（LOCKED）→成交（SOLD，卖家信用 100→102）→评价+收藏+未读+流转记录→统计（碳减排 2.8 kgCO2e）与 CSV 导出 |
| 三方一致性（schema 列 / 实体字段 / 类图属性） | **11 张表全部一致，0 差异**；5 个枚举、6 个 DTO、25 个 interface 全部对齐 |
| 需求编号链路 | FR-01…FR-17 / NFR-01…NFR-10 / BR-01…BR-12 / UC-01…UC-08 在 D1、D2、D5 间引用一致 |
| 错误码口径 | 统一为「两级编号」：语义根码（VAL/DUP/NF/PERM/AUTH/LOCK/DB/TX/IO）+ 模块细分码（如 DB-131），D1 第 7.2.2 节总表 85 行，D2 无自造码 |

**本机限制（已在文档中如实说明，未伪造）**：本机未安装 Maven，因此**未执行 `mvn package`**；已用 `javac --release 17` 编译 + 直接运行 `Main` + 双击 `start.bat` 作为等效验证，`部署说明.md` 第 6 节记录了可复核的实测输出，并给出装 Maven 机器上的完整命令与预期结果。另本机无 draw.io CLI 与 LibreOffice，`.drawio` 只做 XML 结构级校验、docx 只做结构自检，建议交付前在右侧栏编辑器与 Word 中做一次视觉验收。

---

## 5. 迭代一设计要点（答辩时的三句话）

1. **先冻结契约再并行生产**：11 张表字段、12 个 DAO + 7 个 Service 接口签名、10 个异常类、12 条业务规则在动笔前写进 `_共享契约`，三份文档与代码全部照抄同一口径，因此交叉校验一次通过；第 3 轮再用 3 名 v4-pro 子代理反向挑错，45 条修复逐条落账。
2. **设计模式有明确落点**：单例（`DbUtil`/`ConfigManager`）、工厂（`DaoFactory`/`ServiceFactory`）、策略（`ItemSortStrategy` + `CreditFirstItemSortStrategy` / `CarbonFactorStrategy`）、观察者（`ItemEventBus` + 信用/日志/统计监听器）、模板方法（`AbstractJdbcDao.executeInTransaction`/`AbstractCsvExporter`），共 5 种，均给出"解决什么问题"的理由。
3. **事务与完整性写进类型系统**：成交操作（物品状态 + 流转记录 + 双方信用分 + 操作日志）在 `BEGIN IMMEDIATE` 单事务内完成，失败 `ROLLBACK` 并抛 `TransactionException`；数据库侧用部分唯一索引 `uq_flow_item_active` 保证"同一物品不可重复成交"，用 `UNIQUE(flow_id, reviewer_id)` 保证评价唯一，用 `ck_item_free_price` 保证"赠送即 0 元"。

---

## 6. 需要你确认的 3 件事（不影响先用，影响定稿）

1. **组员姓名/学号**：全文用「成员2（待补）」「成员3（待补）」占位（D6 分工表、D1 封面）。你把姓名学号给我，我一次性替换。
2. **里程碑日期**：D6 现按 D1=11-02 … D14=11-15 排期，M1 需求评审=11-06、M2 建模完成=11-10、M3 数据库评审=11-12、M4 交付=11-15，文档中已标注"示意排期"。如与实际组内评审日不同，我同步改 D6 排期表与 D1 修订记录两处。
3. **教师角色**：题目书只定义"学生用户 + 系统管理员"，本组额外加了"教师（可发布教学物资）"，已在 D1 权限矩阵与角色画像中统一标注【建议补充】。若决定合并为学生，我删该列并同步 D2 角色枚举说明。

---

## 7. 第 3 轮修复摘要（评审 → 落账）

| 评审角色 | 结论 | 已处理 |
|---|---|---|
| 评委视角（v4-pro） | 估分 70–75，6 条问题 | 错误码两套 → 统一两级制；D2 需求追踪 FR 编号系统性错位 → 表 4-3 十九行重映射；`item.status` 默认 ON_SALE 架空审核 → 改 PENDING 且发布不写上架时间；缺"信用优先排序"策略 → 新增 `CreditFirstItemSortStrategy`；删除 D2 凭空新增的"好评加分" |
| 一致性审查（v4-pro） | 16 处交叉冲突 | BR 三种写法 → 统一两位；PageResult `rows` → `records`+`totalPages`；`updateCredit` 参数顺序统一为 `(userId, delta, flowId, reason)`；消息 200/300 字 → 200 字（VAL-006）；碳系数键中英混用 → 统一 `carbon.factor.book/electronics/daily/sports`；FREE 价格加库层 CHECK；`freezeUser` 连带取消在途流转（新增 DAO 方法） |
| 可开工性审查（v4-pro） | 5 处硬伤 | D2 误教 `beginTransaction/commit/rollback` → 改为唯一入口 `executeInTransaction`；D6 误称 service 由成员2 迭代二编写 → 改为"已交付、成员2 只补测试与坏味道"；`TradeDetailDTO`/`UserCreditDTO` 无入口 → 新增 `historyDetail/countUnread/getCredit` 三个 Service 方法；主类三处口径 → 统一 `Main`（迭代一）/`ui.MainApp`（迭代二）；内存库方案失效 → 改 `cache=shared` URL |
| 误判（已复核不修） | 「类图/时序图未交付」 | 评审输入只含 01/02/06 文本与 schema.sql，未传 `design\03`（412 mxCell）与 `design\04`（274 mxCell / 6 场景）；Lead 核对文件后标记为误判，不再"修复" |

---

*本 README 由 Lead（成员1）在全部产物验收通过后编写，所有数字来自脚本实测输出，未使用估值。*
