# 低碳校园资源循环流转桌面系统（GreenCampus Recycle）

《软件构造》课程分组实验，3人小组、8周4个迭代。技术栈：Java 17、Maven、SQLite/JDBC、Swing、JUnit 5。

面向校园的闲置物品流转桌面应用，覆盖发布、检索收藏、意向沟通、流转成交、互评与信用分、统计与CSV导出。当前处于迭代一，成员1已交付设计与参考实现，成员2已完成业务规则核对、测试基线与走查。Swing GUI由成员3继续开发。

## 仓库结构

```text
Low-Carbon-Campus-Resource-Recycling-Desktop-System/
├─ README.md
├─ .gitignore
├─ .agentic/
│  └─ 迭代一-成员1-提示词.md       # 历史工作提示词
├─ green-campus/                 # Maven工程，所有构建和Java运行命令在此执行
│  ├─ pom.xml
│  ├─ start.bat
│  ├─ 部署说明.md
│  ├─ lib/                       # 已提供的离线SQLite JDBC驱动
│  ├─ src/main/                  # Java源码与运行配置
│  ├─ src/test/                  # JUnit测试
│  └─ data/                      # 运行生成的数据库、图片与导出文件
├─ db/
│  ├─ schema.sql
│  ├─ seed-data.sql
│  ├─ verify_db.py
│  └─ _verify/                   # 数据库验证目录
└─ docs/
   ├─ 2026软件构造分组实验v3.docx # 老师原始实验要求
   ├─ 迭代一-成员1/              # 需求、接口基线、UML、数据库设计及校验工具
   └─ 迭代一-成员2/              # 规则核对、测试计划、代码走查及实测记录
```

目录迁移后，Java工程和SQL脚本已独立置于仓库根目录。成员1历史文档中的旧路径及原电脑环境记录保留供追溯，当前运行方式以本文件和[部署说明](green-campus/部署说明.md)为准。历史提示词仅用于了解当时的工作过程。

## 阅读入口

- [实验要求](docs/2026软件构造分组实验v3.docx)
- [成员1交付说明与历史验证记录](docs/迭代一-成员1/README-交付说明.md)
- [成员2交付说明与验证记录](docs/迭代一-成员2/README-交付说明.md)
- [共享契约](docs/迭代一-成员1/_共享契约-实体与接口基线.md)：字段、接口、异常和业务规则基线；阅读时结合第13节最新裁决。
- [需求规格](docs/迭代一-成员1/docs/01-需求规格说明书.docx)
- [模块与接口规范](docs/迭代一-成员1/docs/02-模块化设计与接口规范.docx)
- [数据库设计](docs/迭代一-成员1/docs/05-数据库设计说明书.docx)
- [分工与迭代计划](docs/迭代一-成员1/docs/06-小组分工与两周迭代计划.docx)
- [UML及ER图目录](docs/迭代一-成员1/design)

## 构建与运行

安装JDK 17及以上；Maven构建需要Maven 3.8及以上。以下命令从仓库根目录开始：

```powershell
cd green-campus
mvn test
mvn package
java -jar target/green-campus-1.0.0.jar
```

Windows也可双击 `green-campus/start.bat`。脚本依次尝试已有Jar、Maven构建、javac离线编译；脚本的构建分支会跳过测试，测试需单独执行。当前入口为 `edu.campus.recycle.Main` 控制台演示，Swing入口仍待成员3实现。

离线编译与运行（同样在 `green-campus` 目录执行）：

```powershell
javac --release 17 -encoding UTF-8 -sourcepath src/main/java -d build/classes -cp "lib/sqlite-jdbc-3.42.0.0.jar" src/main/java/edu/campus/recycle/Main.java
java -cp "build/classes;src/main/resources;lib/sqlite-jdbc-3.42.0.0.jar" edu.campus.recycle.Main
```

运行工作目录必须是 `green-campus`，配置与默认值均通过 `../db/schema.sql`、`../db/seed-data.sql` 查找脚本。手工运行时将 `src/main/resources` 加入 classpath。当前 Main 每次启动会重建 `green-campus/data/greencampus.db`，演示请使用独立副本。

## 交付物校验

需要Python 3和 `python-docx`；默认Python缺少依赖时，先执行 `python -m pip install python-docx`，或使用已含该依赖的Python环境。下列命令从仓库根目录执行，两个脚本通过自身位置定位文件，也可从其他目录用其完整路径调用：

```powershell
python docs/迭代一-成员1/_tools/verify_all.py
python docs/迭代一-成员1/_tools/cross_check.py
```

- `verify_all.py`：检查Word结构、draw.io XML、临时数据库建库与种子导入、Java目录结构；有失败项返回非零退出码。
- `cross_check.py`：核对表、实体、类图字段、DTO字段和接口名称，更新同目录 `cross_check.txt`。应查看报告中的差异；它不验证完整方法签名或业务行为，也不以退出码表示所有一致性结果。
- 更详细的数据库反例验证可执行 `python db/verify_db.py`，会更新 `db/_verify/` 验证库和 `db/_verify-output.txt`。

2026-11-09目录迁移复核：全量校验20项通过；交叉报告显示11张表字段一致、6个DTO字段一致、接口名称无缺漏。本次未重新运行Java编译、JUnit或Main演示。成员1原环境的11条JUnit及演示结果见历史交付说明，不能替代当前环境的业务验收。

## 协作约定

- 成员1负责设计与数据层，成员2负责业务逻辑与测试，成员3负责GUI与构建交付；每个人都需参与编码和测试。
- 字段、接口或业务规则调整需同步契约、调用方及测试；组内分支和评审约定见分工文档。当前成员2工作分支为 `feature/service-test`。
- 提交格式：`<类型>(<范围>): <说明>`，如 `test(trade): 补充成交事务回滚测试`。
- 构建目录、class文件、运行数据库、CSV导出和Python缓存不入库；`db/_verify/greencampus.db` 为原有验证样本，保留。离线驱动 `green-campus/lib/sqlite-jdbc-3.42.0.0.jar` 随仓库提供。
- 提交前运行相关测试并检查 `git diff`。重排目录后的移动、新增及删除文件需一并检查，避免漏交。
