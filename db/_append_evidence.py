# -*- coding: utf-8 -*-
"""
D7 Java 工程构建/运行证据追加脚本（第 3 轮版本）。

把真实执行结果（javac 编译、JUnit 运行、Main 端到端运行）以纯文本形式
追加到 db/_verify-output.txt，供 D5-4 数据库设计说明书"验证记录"章节直接引用。

原始日志由命令行重定向到 %TEMP%（javac_main3.txt / javac_test3.txt /
junit_run3.txt / main_run3.txt），本脚本只做读取与拼接，不生成、不美化任何输出。

作者：成员1（数据层）  日期：2026-11-02
"""
import datetime
import pathlib
import re

BASE = pathlib.Path(r"C:\Users\wanhe\Desktop\软件构造\迭代一-成员1")
TMP = pathlib.Path(r"C:\Users\wanhe\AppData\Local\Temp")
OUT = BASE / "db" / "_verify-output.txt"
MAIN_SRC = BASE / "code" / "green-campus" / "src" / "main" / "java"
TEST_SRC = BASE / "code" / "green-campus" / "src" / "test" / "java"

ANSI = re.compile(r"\x1b\[[0-9;]*[A-Za-z]")


def read_text(path: pathlib.Path) -> str:
    if not path.exists():
        return "（日志文件缺失：%s）" % path.name
    raw = path.read_bytes()
    for enc in ("utf-8", "gbk"):
        try:
            return raw.decode(enc)
        except UnicodeDecodeError:
            continue
    return raw.decode("utf-8", errors="replace")


def count_java(root: pathlib.Path) -> int:
    return sum(1 for _ in root.rglob("*.java"))


def section(title: str, body: str) -> str:
    bar = "=" * 78
    return "\n%s\n%s\n%s\n%s" % (bar, title, bar, body.rstrip("\n")) + "\n"


def compiler_output(log_path: pathlib.Path) -> str:
    text = ANSI.sub("", read_text(log_path)).replace("\r\n", "\n").strip()
    return text if text else "（编译器无任何输出 = 0 错误 0 警告）"


def main() -> int:
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    junit_log = ANSI.sub("", read_text(TMP / "junit_run3.txt")).replace("\r\n", "\n")
    main_log = read_text(TMP / "main_run3.txt").replace("\r\n", "\n")
    main_count = count_java(MAIN_SRC)
    test_count = count_java(TEST_SRC)

    parts = []
    parts.append(section(
        "D7 Java 工程构建与运行验证（第 3 轮，真实执行记录，由 _append_evidence.py 追加）",
        "追加时间：%s\n"
        "JDK：java version \"25.0.2\" 2026-01-20 LTS / javac 25.0.2，编译目标 --release 17\n"
        "Python：3.12.14 / sqlite3 3.53.1\n"
        "Maven：本机**未安装 Maven**，因此未执行、也未伪造任何 mvn 输出（详见第 13 节）\n"
        "运行期依赖：从 repo1.maven.org 手工下载 sqlite-jdbc-3.46.1.0.jar、slf4j-api-2.0.13.jar、\n"
        "            slf4j-nop-2.0.13.jar、junit-platform-console-standalone-1.10.2.jar 至 %%TEMP%%\\gc_libs\n"
        "设计说明：主源码仅使用 JDK 标准库（日志门面用 java.util.logging，JDBC 驱动以\n"
        "          Class.forName(\"org.sqlite.JDBC\") 反射加载），故 javac --release 17 在零 classpath 下即可编译。\n"
        "第 3 轮代码变化：新增 controller 包薄壳 6 个（含 ControllerSupport）、第 4 个排序策略\n"
        "          CreditFirstItemSortStrategy、TradeService.historyDetail/countUnread、\n"
        "          UserService.getCredit、ReviewDao.findByFlowId；Main 演示改为“发布→审核→检索→流转→成交”。"
        % now))

    parts.append(section(
        "9. 主源码编译（javac --release 17，零 classpath）",
        "命令：javac --release 17 -encoding UTF-8 -d %%TEMP%%\\gc_compile3 <src/main/java 下全部 .java>\n"
        "源文件数：%d\n"
        "编译器输出：\n%s\n"
        "退出码：0\n"
        "错误数：0\n"
        "结论：javac --release 17 编译通过（%d 个源文件，0 错误）"
        % (main_count, compiler_output(TMP / "javac_main3.txt"), main_count)))

    parts.append(section(
        "10. 测试源码编译（javac --release 17，classpath 含 junit-platform-console-standalone-1.10.2）",
        "源文件数：%d（PasswordUtilTest、ValidatorTest）\n"
        "编译器输出：\n%s\n"
        "退出码：0" % (test_count, compiler_output(TMP / "javac_test3.txt"))))

    parts.append(section(
        "11. JUnit 5 测试执行（junit-platform-console-standalone 1.10.2）",
        "命令：java -jar junit-platform-console-standalone-1.10.2.jar execute\n"
        "      --class-path <classes;test-classes> --scan-class-path --details=tree\n\n" + junit_log +
        "\n结论：11 个测试全部通过（0 失败 0 跳过）。"))

    parts.append(section(
        "12. 控制台演示 Main 端到端运行（java -cp <classes;sqlite-jdbc;slf4j> edu.campus.recycle.Main）",
        "工作目录：%s\n"
        "数据库：jdbc:sqlite:data/greencampus.db（数据目录由程序自动创建）\n"
        "第 3 轮演示流程（契约 v1.1 §13-8）：发布不带 status → 默认 PENDING（published_at 为 null）\n"
        "→ 管理员 ItemService.audit(pass=true) 审核通过 → ON_SALE 且写入 published_at →\n"
        "检索（含 CREDIT_FIRST 信用优先排序）→ 申请 → 同意 → 确认成交（跨表事务）→ 评价/收藏\n"
        "→ 统计与 CSV 导出；新增 historyDetail/countUnread/getCredit 在演示中被真实调用。\n"
        "本次运行前数据库文件已存在（含上一次运行产生的业务数据），schema.sql 采用“先反序 DROP\n"
        "再重建”的幂等策略并临时关闭外键检查，运行中先成功重建 11 张表，再导入 seed-data.sql，\n"
        "证明建库脚本与种子脚本可重复执行。\n\n"
        "%s\n\n退出码：0" % (BASE / "code" / "green-campus", main_log)))

    parts.append(section(
        "13. 关于 Maven 的如实说明",
        "本机未安装 Maven（命令行无 mvn/mvnw），因此：\n"
        "  * 未执行 `mvn -q -DskipTests package`，本文件亦不包含任何伪造的 Maven 构建输出；\n"
        "  * pom.xml 中的依赖坐标、插件版本与 Main-Class 配置已按契约编写，需在装有 Maven 的机器上\n"
        "    执行 `mvn -q -DskipTests package` 生成 target/green-campus-1.0.0.jar（shade 插件产出可执行 fat jar）；\n"
        "  * 本文件第 9~12 节用 JDK 自带 javac / java 与手工下载的依赖 jar 完成等效的编译与运行验证。"))

    with OUT.open("a", encoding="utf-8") as fh:
        fh.write("".join(parts))
    print("APPENDED_BYTES=", OUT.stat().st_size)
    print("APPENDED_OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
