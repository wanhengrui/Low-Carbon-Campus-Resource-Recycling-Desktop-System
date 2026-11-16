# -*- coding: utf-8 -*-
"""Generate member3 iteration-1 docx deliverables."""
from __future__ import annotations

import os

from docx import Document
from docx.enum.section import WD_SECTION
from docx.enum.table import WD_ALIGN_VERTICAL, WD_TABLE_ALIGNMENT
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Cm, Pt, RGBColor

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DOCS = os.path.join(BASE, "docs")
os.makedirs(DOCS, exist_ok=True)

NAVY = "152238"
GREEN = "1F6F5C"
GOLD = "D9A441"
INK = "202A36"
MUTED = "6B7280"
BORDER = "D9D2C6"
FONT = "微软雅黑"


def rgb(hex_color):
    return RGBColor.from_string(hex_color)


def set_run(run, size=9.5, bold=False, color=INK, font=FONT):
    run.font.name = font
    run._element.get_or_add_rPr().rFonts.set(qn("w:eastAsia"), font)
    run.font.size = Pt(size)
    run.bold = bold
    run.font.color.rgb = rgb(color)


def shade(cell, color):
    tcPr = cell._tc.get_or_add_tcPr()
    shd = OxmlElement("w:shd")
    shd.set(qn("w:val"), "clear")
    shd.set(qn("w:color"), "auto")
    shd.set(qn("w:fill"), color)
    tcPr.append(shd)


def border_bottom(paragraph, color=GREEN, sz=8):
    pPr = paragraph._p.get_or_add_pPr()
    pBdr = OxmlElement("w:pBdr")
    el = OxmlElement("w:bottom")
    el.set(qn("w:val"), "single")
    el.set(qn("w:sz"), str(sz))
    el.set(qn("w:space"), "3")
    el.set(qn("w:color"), color)
    pBdr.append(el)
    pPr.append(pBdr)


def add_field(paragraph, instr):
    run = paragraph.add_run()
    fld = OxmlElement("w:fldChar")
    fld.set(qn("w:fldCharType"), "begin")
    it = OxmlElement("w:instrText")
    it.set(qn("xml:space"), "preserve")
    it.text = f" {instr} "
    sep = OxmlElement("w:fldChar")
    sep.set(qn("w:fldCharType"), "separate")
    txt = OxmlElement("w:t")
    txt.text = "1"
    end = OxmlElement("w:fldChar")
    end.set(qn("w:fldCharType"), "end")
    run._r.append(fld)
    run._r.append(it)
    run._r.append(sep)
    run._r.append(txt)
    run._r.append(end)
    set_run(run, 8, False, MUTED)


def new_doc(title, subtitle):
    doc = Document()
    sec = doc.sections[0]
    sec.page_width = Cm(21)
    sec.page_height = Cm(29.7)
    sec.top_margin = Cm(2.0)
    sec.bottom_margin = Cm(1.8)
    sec.left_margin = Cm(2.0)
    sec.right_margin = Cm(2.0)
    style = doc.styles["Normal"]
    style.font.name = FONT
    style._element.rPr.rFonts.set(qn("w:eastAsia"), FONT)
    style.font.size = Pt(9.5)
    style.font.color.rgb = rgb(INK)
    style.paragraph_format.line_spacing = 1.45
    style.paragraph_format.space_after = Pt(6)

    # header / footer
    hp = sec.header.paragraphs[0]
    set_run(hp.add_run("绿色校园 · 迭代一成员3"), 7.5, False, MUTED)
    hp.add_run("\t")
    set_run(hp.add_run("2026-11-16"), 7.5, False, MUTED)
    hp.paragraph_format.tab_stops.add_tab_stop(Cm(17.0), 2)

    fp = sec.footer.paragraphs[0]
    set_run(fp.add_run("成员3：GUI / 复用 / 交付"), 7.5, False, MUTED)
    fp.add_run("\t第 ")
    add_field(fp, "PAGE")
    set_run(fp.add_run(" 页"), 7.5, False, MUTED)
    fp.paragraph_format.tab_stops.add_tab_stop(Cm(17.0), 2)

    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(30)
    p.paragraph_format.space_after = Pt(4)
    set_run(p.add_run("迭代一 · 成员3"), 10, True, GOLD)
    p2 = doc.add_paragraph()
    p2.paragraph_format.space_after = Pt(2)
    set_run(p2.add_run(title), 24, True, NAVY)
    p3 = doc.add_paragraph()
    p3.paragraph_format.space_after = Pt(18)
    set_run(p3.add_run(subtitle), 11, False, MUTED)
    border_bottom(p3, GOLD, 12)
    return doc


def h1(doc, text):
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(16)
    p.paragraph_format.space_after = Pt(7)
    p.paragraph_format.keep_with_next = True
    set_run(p.add_run(text), 15, True, NAVY)
    border_bottom(p, GREEN, 8)


def h2(doc, text):
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(10)
    p.paragraph_format.space_after = Pt(4)
    p.paragraph_format.keep_with_next = True
    set_run(p.add_run(text), 11, True, GREEN)
    return p


def body(doc, text, size=9.5, color=INK, bold=False):
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    set_run(p.add_run(text), size, bold, color)
    return p


def bullet(doc, text):
    p = doc.add_paragraph()
    p.paragraph_format.left_indent = Cm(0.5)
    p.paragraph_format.first_line_indent = Cm(-0.3)
    p.paragraph_format.space_after = Pt(3)
    set_run(p.add_run("•  "), 9.5, True, GOLD)
    set_run(p.add_run(text), 9.3)
    return p


def code(doc, text):
    p = doc.add_paragraph()
    p.paragraph_format.left_indent = Cm(0.5)
    p.paragraph_format.space_before = Pt(4)
    p.paragraph_format.space_after = Pt(6)
    p.paragraph_format.line_spacing = 1.15
    for i, line in enumerate(text.split("\n")):
        if i:
            p.add_run().add_break()
        set_run(p.add_run(line), 8.2, False, "374151", "Consolas")


def table(doc, headers, rows, widths, font_size=8.2):
    t = doc.add_table(rows=1, cols=len(headers))
    t.alignment = WD_TABLE_ALIGNMENT.CENTER
    t.autofit = False
    t.style = "Table Grid"
    trPr = t.rows[0]._tr.get_or_add_trPr()
    th = OxmlElement("w:tblHeader")
    th.set(qn("w:val"), "true")
    trPr.append(th)
    for j, text in enumerate(headers):
        c = t.rows[0].cells[j]
        c.width = Cm(widths[j])
        shade(c, NAVY)
        c.vertical_alignment = WD_ALIGN_VERTICAL.CENTER
        p = c.paragraphs[0]
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p.paragraph_format.space_after = Pt(0)
        set_run(p.add_run(str(text)), font_size, True, "FFFFFF")
    for i, row in enumerate(rows):
        tr = t.add_row()
        trPr = tr._tr.get_or_add_trPr()
        cs = OxmlElement("w:cantSplit")
        cs.set(qn("w:val"), "true")
        trPr.append(cs)
        for j, value in enumerate(row):
            c = tr.cells[j]
            c.width = Cm(widths[j])
            c.vertical_alignment = WD_ALIGN_VERTICAL.CENTER
            if i % 2 == 1:
                shade(c, "FAF8F3")
            p = c.paragraphs[0]
            p.paragraph_format.space_after = Pt(0)
            p.paragraph_format.line_spacing = 1.1
            set_run(p.add_run(str(value)), font_size, j == 0, INK)
    return t


def build_ui_doc():
    doc = new_doc("界面骨架与复用设计说明",
                  "迭代一（第 1—2 周）· 成员3：Swing 界面 / 事件驱动 / 设计模式复用 / 构建交付")
    body(doc, "文档定位：本文件只固化迭代一的界面骨架、导航、事件流与复用接入口，"
              "不把检索、发布、流转、评价、统计、管理后台的完整业务实现冒充为已完成。"
              "完整界面在迭代二/三按本文件逐步落地。")

    h1(doc, "1. 迭代一交付边界")
    body(doc, "成员3 在迭代一的职责是“可用与可交付”：把成员1 已交付的 Controller/Service 能力"
              "包装成可启动的 Swing 骨架，并给出复用、构建、部署与演示方案。")
    bullet(doc, "已完成：MainApp、LoginFrame、RegisterDialog、MainFrame、UiTheme、run-ui.bat。")
    bullet(doc, "已完成：窗体清单、导航结构、事件流/SwingWorker 规则、复用接入口、构建方案、演示大纲。")
    bullet(doc, "未完成（迭代二/三）：检索、发布、我的物品、流转、评价、统计、管理后台的完整业务页。")
    bullet(doc, "边界：UI 只依赖 controller/dto/entity/exception，不直接依赖 service/dao，不写 SQL。")

    h1(doc, "2. 窗体清单与导航")
    body(doc, "主界面采用“菜单栏 + 左侧导航 + 右侧 CardLayout”的结构。登录成功后按角色动态显示菜单，"
              "管理员入口同时由 UI 隐藏与 Service 权限校验两层保护。")
    table(doc, ["#", "窗体/面板", "类名", "迭代一状态", "依赖 Controller"], [
        ["1", "登录", "LoginFrame", "已实现", "AppController.login"],
        ["2", "注册", "RegisterDialog", "已实现", "UserController.register"],
        ["3", "主窗体", "MainFrame", "已实现", "AppController（会话）"],
        ["4", "首页", "HomePanel（内嵌）", "已实现", "无"],
        ["5", "检索物品", "ItemSearchPanel", "占位", "ItemController.search"],
        ["6", "物品详情/收藏", "ItemDetailDialog", "占位", "ItemController.detail / AppController.toggleFavorite"],
        ["7", "发布/修改", "PublishItemDialog", "占位", "ItemController.publish/updateItem"],
        ["8", "我的物品", "MyItemPanel", "占位", "待补按 ownerId 查询方法"],
        ["9", "流转/消息", "TradePanel", "占位", "TradeController.*"],
        ["10", "评价/信用", "ReviewDialog / ProfilePanel", "占位", "ReviewController / UserController.getCredit"],
        ["11", "统计/导出", "StatisticPanel", "占位", "StatisticController"],
        ["12", "管理后台", "AdminPanel", "占位（仅 ADMIN）", "AdminController / UserController / ItemController"],
    ], [0.9, 3.1, 4.0, 3.3, 5.5], font_size=7.6)

    body(doc, "导航结构：登录 → 主窗体 → 首页 / 检索 / 发布 / 我的物品 / 流转 / 评价 / 统计 / [管理员] 管理后台。"
              "学生与教师不显示管理后台；管理员登录后多出该入口。")

    h1(doc, "3. 事件流与 SwingWorker 规则")
    body(doc, "所有业务按钮统一遵循“禁用按钮 → SwingWorker.doInBackground 调 Controller → done 更新控件 → finally 恢复按钮”。"
              "禁止在 EDT 中访问数据库或 Service；禁止在 doInBackground 中操作 Swing 组件。")
    code(doc, """button.setEnabled(false);
new SwingWorker<PageResult<Item>, Void>() {
    protected PageResult<Item> doInBackground() {
        return itemController.search(query);
    }
    protected void done() {
        try {
            tableModel.setRows(get().getRecords());
        } catch (ExecutionException ex) {
            Throwable cause = ex.getCause();
            if (cause instanceof AppException) {
                UiMessages.error(this, (AppException) cause);
            }
        } catch (InterruptedException ex) {
            Thread.currentThread().interrupt();
        } finally {
            button.setEnabled(true);
        }
    }
}.execute();""")
    body(doc, "迭代一已落地：登录、注册使用 SwingWorker；主界面导航与占位卡完成。"
              "检索、发布、流转、评价、统计、管理页在迭代二接入同一模板。")

    h1(doc, "4. UI 与 Controller 的映射")
    table(doc, ["功能", "Controller", "方法", "说明"], [
        ["登录", "AppController", "login(username, rawPassword)", "成功后持有 currentUser"],
        ["注册", "UserController", "register(... role=STUDENT ...)", "返回 String 文案"],
        ["检索", "ItemController", "search(ItemQuery)", "返回 PageResult<Item>"],
        ["详情/收藏", "ItemController / AppController", "detail / toggleFavorite", "收藏需登录"],
        ["发布/修改/下架", "ItemController", "publish / updateItem / offShelf", "发布默认 PENDING"],
        ["审核", "ItemController", "audit(operatorId, itemId, pass, remark)", "仅 ADMIN"],
        ["流转", "TradeController", "apply / agree / confirm / cancel / historyDetail", "成交跨表事务"],
        ["评价", "ReviewController", "review(flowId, reviewerId, score, content)", "仅 DONE 流转"],
        ["统计/导出", "StatisticController", "statisticsByCategory / carbonReduction / exportCsv", "CSV 走模板方法"],
        ["用户管理", "UserController", "queryUsers / freezeUser / unfreezeUser", "仅 ADMIN"],
        ["分类/日志", "AdminController", "addCategory / toggleCategory / recentLogs", "仅 ADMIN"],
    ], [2.4, 3.4, 7.0, 4.0], font_size=7.6)

    h1(doc, "5. 复用构件与设计模式")
    table(doc, ["模式", "已有构件", "UI 侧接入口"], [
        ["单例", "ServiceFactory / ConfigManager / DbUtil", "Controller 内部使用；UI 不 new Service"],
        ["工厂", "DaoFactory / ServiceFactory", "Controller 构造时装配；UI 不直接调用"],
        ["策略", "ItemSortStrategy 及 4 个实现", "检索排序下拉框 → ItemQuery.sortBy"],
        ["观察者", "ItemEventBus + 3 个 Listener", "发布/成交/评价后刷新列表与统计"],
        ["模板方法", "AbstractJdbcDao / AbstractCsvExporter", "统计导出走 StatisticController.exportCsv"],
    ], [2.6, 6.8, 7.4], font_size=8.0)
    body(doc, "成员3 不修改成员1 的策略/观察者/模板方法实现；只按上述接入口调用。"
              "新增排序策略时只加策略类并在 ItemDaoImpl 注册，不改 UI 的 if/else。")

    h1(doc, "6. 构建与交付")
    body(doc, "Maven 坐标：edu.campus:green-campus:1.0.0，Java release 17，maven-shade-plugin 打可执行 jar。"
              "迭代一主类保持 edu.campus.recycle.Main（控制台基线）；迭代二起切换为 edu.campus.recycle.ui.MainApp。")
    bullet(doc, "UI 骨架启动：code/green-campus/run-ui.bat。")
    bullet(doc, "控制台基线：code/green-campus/start.bat（成员1 保留，不破坏）。")
    bullet(doc, "数据库：默认 data/greencampus.db；MainApp 只在缺库时初始化，--reset-db 强制重置。")
    bullet(doc, "交付风险：本机无 Maven，fat jar 迭代四补跑；db 脚本相对路径需在迭代四做资源内置/回退。")

    h1(doc, "7. 迭代一验收")
    for t in [
        "run-ui.bat 启动后出现登录窗体；",
        "admin / Admin@123 或 zhangsan / Student@123 能登录；",
        "主界面导航可切换，管理员多出“管理后台”；",
        "退出登录回到登录窗体；",
        "start.bat 仍可跑控制台 9 步，未被 UI 修改破坏；",
        "本说明与 UI-窗体清单、复用设计说明、部署说明初稿一致。",
    ]:
        bullet(doc, t)

    h1(doc, "8. 迭代二交接")
    body(doc, "迭代二第 16 天起，按“登录 → 检索/详情/收藏 → 发布/我的物品 → 流转 → 评价/信用 → 统计/导出 → 管理后台”"
              "的纵向切片接入真实 Controller；每完成一个切片，补一次手工冒烟和截图。"
              "不在迭代一提前实现完整业务页，避免在接口未联调时返工。")
    doc.save(os.path.join(DOCS, "07-界面骨架与复用说明.docx"))


def build_deploy_doc():
    doc = new_doc("部署说明初稿（UI 骨架）",
                  "迭代一 · 成员3 · 运行环境 / 启动方式 / 演示账号 / 已知风险")
    body(doc, "本文只记录已验证的命令与已知限制，不虚构 Maven 构建输出。"
              "迭代四正式交付时，把本文升级为部署使用说明书。")

    h1(doc, "1. 环境要求")
    table(doc, ["项目", "要求", "说明"], [
        ["JDK", "17 及以上（编译目标 17）", "本机验证环境只有 JDK 11，run-ui.bat 提供回退编译"],
        ["SQLite", "sqlite-jdbc 3.42.0.0", "已由成员1 放入 code/green-campus/lib/"],
        ["Maven", "3.8+（可选）", "成员1 机器未安装；迭代四在装有 Maven 的机器补跑"],
        ["工作目录", "code/green-campus", "db.schema 使用 ../../db/schema.sql 相对路径"],
    ], [3.0, 6.0, 8.0], font_size=8.4)

    h1(doc, "2. 启动 UI 骨架")
    body(doc, "在 code/green-campus 目录执行：")
    code(doc, """run-ui.bat

REM 重置演示数据
run-ui.bat --reset-db""")
    body(doc, "run-ui.bat 的步骤：定位 sqlite-jdbc → 优先 javac --release 17 编译 → 失败回退当前 JDK → "
              "启动 edu.campus.recycle.ui.MainApp。首次启动创建 data/greencampus.db 并导入 seed；"
              "之后启动若数据库已存在则跳过初始化。")

    h1(doc, "3. 演示账号")
    table(doc, ["账号", "密码", "角色", "说明"], [
        ["admin", "Admin@123", "ADMIN", "验证管理员菜单"],
        ["zhangsan", "Student@123", "STUDENT", "验证普通学生菜单"],
    ], [3.0, 4.0, 3.0, 7.0], font_size=8.4)
    body(doc, "密码来自 D5 数据库设计说明书的演示口令表；数据库中只存 PBKDF2 摘要，明文仅用于课程演示。")

    h1(doc, "4. 控制台基线")
    body(doc, "成员1 的 start.bat 仍保留，用于验证 Service/DAO/Controller 的 9 步控制台流程。"
              "迭代一不把 start.bat 切换到 UI，避免破坏成员1 已验证的基线。")
    code(doc, """cd 迭代一-成员1\\code\\green-campus
start.bat""")

    h1(doc, "5. Maven 方案")
    body(doc, "Maven 坐标 edu.campus:green-campus:1.0.0；shade 插件生成 green-campus-1.0.0.jar。"
              "迭代一 main.class 仍为 edu.campus.recycle.Main；迭代二切到 edu.campus.recycle.ui.MainApp。")
    code(doc, """mvn -q -DskipTests package
java -jar target/green-campus-1.0.0.jar
mvn test""")
    body(doc, "本机没有 Maven，上述命令未执行，不能写成“已通过”；迭代四补跑并保存日志。")

    h1(doc, "6. 已知风险与处理")
    table(doc, ["风险", "影响", "处理"], [
        ["本机只有 JDK 11", "--release 17 不可用", "run-ui.bat 回退当前 JDK；正式环境用 JDK 17+"],
        ["本机无 Maven", "不能验证 fat jar", "迭代四换机器补跑并留存 mvn 日志"],
        ["db.schema 相对路径", "双击 jar 找不到脚本", "迭代四内置资源 + 外部 db/ 回退"],
        ["Main/MainApp 双入口", "可能启动旧控制台", "迭代二统一入口并更新 start.bat"],
        ["每次启动重置库", "数据丢失", "MainApp 只在缺库时初始化；--reset-db 显式重置"],
        ["Controller 返回 String", "UI 只能靠文案判断", "迭代二与成员1/2 统一 typed result"],
    ], [4.0, 5.5, 7.5], font_size=7.8)

    h1(doc, "7. 交付检查")
    for t in [
        "run-ui.bat 能启动登录窗体；",
        "admin/Admin@123、zhangsan/Student@123 可登录；",
        "管理员能看到管理后台，学生看不到；",
        "start.bat 仍能跑成员1 的控制台 9 步；",
        "README-UI交付.md 与本文件口径一致。",
    ]:
        bullet(doc, t)
    doc.save(os.path.join(DOCS, "08-部署说明初稿.docx"))


if __name__ == "__main__":
    build_ui_doc()
    build_deploy_doc()
    print("docs generated")
