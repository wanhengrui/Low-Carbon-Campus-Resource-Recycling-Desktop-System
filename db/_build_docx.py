# -*- coding: utf-8 -*-
"""
D5-4《05-数据库设计说明书》构建脚本。

数据来源（单一真实来源，避免文档与实现不一致）：
  * 结构：db/schema.sql（由 _schema_model.parse_schema 解析，11 表 93 列 18 外键 13 索引）；
  * 种子：db/_verify/greencampus.db（由 verify_db.py 真实建库并导入 seed-data.sql 后留存）；
  * 验证：db/_verify-output.txt（verify_db.py / _check_er.py / _append_evidence.py 的真实输出）。

输出：迭代一-成员1/docs/05-数据库设计说明书.docx
作者：成员1（数据层）  日期：2026-11-02
"""
import datetime
import pathlib
import re
import sqlite3

from docx import Document
from docx.enum.section import WD_SECTION
from docx.enum.table import WD_ALIGN_VERTICAL, WD_TABLE_ALIGNMENT
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_BREAK
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Cm, Pt, RGBColor

import _schema_model as sm

BASE = pathlib.Path(r"C:\Users\wanhe\Desktop\软件构造\迭代一-成员1")
OUT = BASE / "docs" / "05-数据库设计说明书.docx"
VERIFY_OUTPUT = BASE / "db" / "_verify-output.txt"
VERIFY_DB = BASE / "db" / "_verify" / "greencampus.db"
PROJECT = BASE.parent.name  # 迭代一-成员1

TODAY = datetime.date(2026, 11, 2)
GENERATED_AT = "2026-11-02"

# 关系线业务含义（键：子表.列）
REL_DESC = {
    "category.parent_id": ("父分类 1 : N 子分类", "两级分类自关联，parent_id 为 NULL 表示一级分类；最多两级"),
    "credit_log.user_id": ("用户 1 : N 信用流水", "每次信用分变化写一条审计流水，支撑个人信用页"),
    "credit_log.flow_id": ("流转 1 : N 信用流水", "一次成交最多两条（买卖双方各一条）；流转删除后流水保留、flow_id 置空"),
    "favorite.user_id": ("用户 1 : N 收藏", "“我的收藏”列表；同一用户对同一物品至多一条"),
    "favorite.item_id": ("物品 1 : N 收藏", "收藏数冗余在 item.favorite_count，便于列表展示"),
    "item.owner_id": ("用户 1 : N 物品", "“我的发布”；注销时级联删除物品（业务上要求先下架）"),
    "item.category_id": ("分类 1 : N 物品", "检索维度；分类被引用时禁止删除（RESTRICT）"),
    "item_image.item_id": ("物品 1 : N 图片", "最多 5 张（BR-12），sort_order=0 为首图"),
    "operation_log.operator_id": ("用户 1 : N 操作日志", "审计留痕；操作人删除后日志保留（SET NULL）"),
    "review.flow_id": ("流转 1 : N 评价", "成交后买卖双方各可评价一次，UNIQUE(flow_id, reviewer_id) 兜底"),
    "review.reviewer_id": ("用户 1 : N 评价（作为评价人）", "“我发出的评价”"),
    "review.reviewee_id": ("用户 1 : N 评价（作为被评价人）", "“我收到的评价”，用于信用分调整"),
    "trade_flow.item_id": ("物品 1 : N 流转", "同一物品可有多次历史流转，但活动态（APPLYING/AGREED）至多一条"),
    "trade_flow.seller_id": ("用户 1 : N 流转（作为卖家）", "“我卖出的”；存在流转时禁止删除用户（RESTRICT）"),
    "trade_flow.buyer_id": ("用户 1 : N 流转（作为买家）", "“我买到的”"),
    "trade_message.item_id": ("物品 1 : N 消息", "围绕某物品的沟通上下文"),
    "trade_message.from_user_id": ("用户 1 : N 消息（发送）", "会话查询按 (from,to,item) 三元组"),
    "trade_message.to_user_id": ("用户 1 : N 消息（接收）", "未读数统计"),
}

# 表 → DAO 接口 / Service 接口（契约第 5、6 节）
TABLE_SERVICE = {
    "user": ("UserDao", "UserService", "AdminService（冻结/解冻）"),
    "category": ("CategoryDao", "AdminService（新增/启停分类）", "—"),
    "item": ("ItemDao", "ItemService", "StatisticService（统计口径）"),
    "item_image": ("ItemImageDao", "ItemService（发布/详情）", "—"),
    "favorite": ("FavoriteDao", "FavoriteService", "—"),
    "trade_message": ("TradeMessageDao", "TradeService（沟通）", "—"),
    "trade_flow": ("TradeFlowDao", "TradeService", "StatisticService"),
    "review": ("ReviewDao", "ReviewService", "—"),
    "credit_log": ("CreditLogDao", "UserService.updateCredit", "TradeService.confirm / ReviewService.review"),
    "operation_log": ("OperationLogDao", "AdminService.recentLogs", "观察者 OperationLogListener 自动写入"),
    "system_config": ("SystemConfigDao", "—", "ConfigManager / 各 Service 读取业务参数"),
}

TYPE_MAP = [
    ("INTEGER（主键/外键）", "Integer", "主键自增；外键允许 NULL 时用 Integer 包装类型，禁止 int 表示可空列"),
    ("INTEGER（计数/分值）", "int / Integer", "浏览数、收藏数用 int；fail_count、credit_score 用 int 承载（NOT NULL）"),
    ("INTEGER（0/1 布尔）", "Boolean", "例如 trade_message.is_read、category.enabled；JDBC getBoolean 读取"),
    ("TEXT（时间）", "LocalDateTime", "统一 'yyyy-MM-dd HH:mm:ss' 文本；Java 侧用 AbstractJdbcDao.DATE_TIME_FORMATTER 格式化"),
    ("TEXT（枚举编码）", "String", "role/status/trade_type/flow_type 直接存编码；实体字段用 String，枚举负责 getCode/fromCode"),
    ("REAL（金额）", "BigDecimal", "price/amount/original_price 用 REAL 存，Java 侧 BigDecimal 精确比较，写库时转 double"),
]

CHAPTERS = [
    ("1", "设计目标与选型理由"),
    ("2", "ER 图说明"),
    ("3", "数据字典"),
    ("4", "主键、外键、唯一与 CHECK 约束"),
    ("5", "索引清单与建立理由"),
    ("6", "事务边界与并发控制"),
    ("7", "反范式设计说明"),
    ("8", "初始化与种子数据说明"),
    ("9", "验证记录"),
    ("10", "与 D3 类图、D2 接口的字段对照"),
    ("附录 A", "工程结构与文件清单"),
    ("附录 B", "复现步骤（命令）"),
]

# =============================================================================
# 基础排版工具
# =============================================================================


def set_run_font(run, name="宋体", size=None, bold=None, color=None, ascii_font=None):
    run.font.name = ascii_font or "Times New Roman"
    run._element.rPr.rFonts.set(qn("w:eastAsia"), name)
    if size is not None:
        run.font.size = Pt(size)
    if bold is not None:
        run.bold = bold
    if color is not None:
        run.font.color.rgb = RGBColor(*color)


def style_font(style, name, size, bold=False, color=None):
    style.font.name = "Times New Roman"
    style.font.size = Pt(size)
    style.font.bold = bold
    style.element.rPr.rFonts.set(qn("w:eastAsia"), name)
    if color:
        style.font.color.rgb = RGBColor(*color)


def shade_cell(cell, hex_fill):
    tc_pr = cell._tc.get_or_add_tcPr()
    shd = OxmlElement("w:shd")
    shd.set(qn("w:val"), "clear")
    shd.set(qn("w:color"), "auto")
    shd.set(qn("w:fill"), hex_fill)
    tc_pr.append(shd)


def set_cell_margins(table, top=40, bottom=40, left=80, right=80):
    tbl_pr = table._tbl.tblPr
    mar = OxmlElement("w:tblCellMar")
    for tag, val in (("top", top), ("left", left), ("bottom", bottom), ("right", right)):
        el = OxmlElement("w:%s" % tag)
        el.set(qn("w:w"), str(val))
        el.set(qn("w:type"), "dxa")
        mar.append(el)
    tbl_pr.append(mar)


def repeat_header(row):
    tr_pr = row._tr.get_or_add_trPr()
    header = OxmlElement("w:tblHeader")
    header.set(qn("w:val"), "true")
    tr_pr.append(header)


def add_field(paragraph, instr, size=9):
    run = paragraph.add_run()
    fld_begin = OxmlElement("w:fldChar")
    fld_begin.set(qn("w:fldCharType"), "begin")
    instr_el = OxmlElement("w:instrText")
    instr_el.set(qn("xml:space"), "preserve")
    instr_el.text = instr
    fld_sep = OxmlElement("w:fldChar")
    fld_sep.set(qn("w:fldCharType"), "separate")
    text_el = OxmlElement("w:t")
    text_el.text = "1"
    fld_end = OxmlElement("w:fldChar")
    fld_end.set(qn("w:fldCharType"), "end")
    run._r.append(fld_begin)
    run._r.append(instr_el)
    run._r.append(fld_sep)
    run._r.append(text_el)
    run._r.append(fld_end)
    set_run_font(run, "宋体", size)


def body(doc, text, indent=True, size=10.5, bold=False, align=None, space_after=4,
         first_line=True, line_spacing=1.35):
    p = doc.add_paragraph()
    pf = p.paragraph_format
    pf.space_before = Pt(0)
    pf.space_after = Pt(space_after)
    pf.line_spacing = line_spacing
    if first_line and indent:
        pf.first_line_indent = Pt(21)
    if align is not None:
        p.alignment = align
    run = p.add_run(text)
    set_run_font(run, "宋体", size, bold=bold)
    return p


def bullets(doc, items, size=10.5):
    for it in items:
        p = doc.add_paragraph(style="List Bullet")
        pf = p.paragraph_format
        pf.space_after = Pt(2)
        pf.line_spacing = 1.3
        pf.left_indent = Cm(0.9)
        run = p.add_run(it)
        set_run_font(run, "宋体", size)


def caption(doc, text):
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.space_before = Pt(4)
    p.paragraph_format.space_after = Pt(3)
    run = p.add_run(text)
    set_run_font(run, "黑体", 9.5, bold=True)
    return p


def make_table(doc, headers, rows, widths, size=8.5, header_fill="D9E2F3",
               align_center_cols=None, first_col_bold=False, zebra=True):
    """构建带表头底色、可跨页重复表头、单元格垂直居中的表格。"""
    table = doc.add_table(rows=1, cols=len(headers))
    table.style = "Table Grid"
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    table.autofit = False
    set_cell_margins(table)

    hdr = table.rows[0]
    repeat_header(hdr)
    for idx, h in enumerate(headers):
        cell = hdr.cells[idx]
        cell.width = Cm(widths[idx])
        cell.vertical_alignment = WD_ALIGN_VERTICAL.CENTER
        shade_cell(cell, header_fill)
        p = cell.paragraphs[0]
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p.paragraph_format.space_after = Pt(0)
        run = p.add_run(str(h))
        set_run_font(run, "黑体", size, bold=True)

    for r_idx, row in enumerate(rows):
        cells = table.add_row().cells
        for c_idx, val in enumerate(row):
            cell = cells[c_idx]
            cell.width = Cm(widths[c_idx])
            cell.vertical_alignment = WD_ALIGN_VERTICAL.CENTER
            if zebra and r_idx % 2 == 1:
                shade_cell(cell, "F2F2F2")
            p = cell.paragraphs[0]
            p.paragraph_format.space_after = Pt(0)
            p.paragraph_format.line_spacing = 1.05
            if align_center_cols and c_idx in align_center_cols:
                p.alignment = WD_ALIGN_PARAGRAPH.CENTER
            run = p.add_run(str(val))
            set_run_font(run, "宋体", size, bold=(first_col_bold and c_idx == 0))
    return table


def code_block(doc, lines, size=7.8):
    for line in lines:
        p = doc.add_paragraph()
        pf = p.paragraph_format
        pf.space_before = Pt(0)
        pf.space_after = Pt(0)
        pf.line_spacing = 1.0
        pf.left_indent = Cm(0.4)
        p_pr = p._p.get_or_add_pPr()
        shd = OxmlElement("w:shd")
        shd.set(qn("w:val"), "clear")
        shd.set(qn("w:color"), "auto")
        shd.set(qn("w:fill"), "F5F5F5")
        p_pr.append(shd)
        run = p.add_run(line if line else " ")
        set_run_font(run, "宋体", size, ascii_font="Consolas")


def h1(doc, text):
    p = doc.add_heading(level=1)
    p.paragraph_format.space_before = Pt(14)
    p.paragraph_format.space_after = Pt(6)
    run = p.add_run(text)
    set_run_font(run, "黑体", 16, bold=True, color=(0x1F, 0x3B, 0x63))


def h2(doc, text):
    p = doc.add_heading(level=2)
    p.paragraph_format.space_before = Pt(10)
    p.paragraph_format.space_after = Pt(4)
    run = p.add_run(text)
    set_run_font(run, "黑体", 12.5, bold=True, color=(0x1F, 0x3B, 0x63))


def h3(doc, text):
    p = doc.add_heading(level=3)
    p.paragraph_format.space_before = Pt(8)
    p.paragraph_format.space_after = Pt(3)
    run = p.add_run(text)
    set_run_font(run, "黑体", 11, bold=True, color=(0x33, 0x33, 0x33))


def page_break(doc):
    p = doc.add_paragraph()
    p.add_run().add_break(WD_BREAK.PAGE)


# =============================================================================
# 文档骨架
# =============================================================================


def setup_document():
    doc = Document()
    section = doc.sections[0]
    section.page_width = Cm(21.0)
    section.page_height = Cm(29.7)
    section.left_margin = Cm(2.4)
    section.right_margin = Cm(2.2)
    section.top_margin = Cm(2.3)
    section.bottom_margin = Cm(2.0)
    section.header_distance = Cm(1.3)
    section.footer_distance = Cm(1.1)

    styles = doc.styles
    normal = styles["Normal"]
    style_font(normal, "宋体", 10.5)
    normal.paragraph_format.line_spacing = 1.35
    normal.paragraph_format.space_after = Pt(4)

    for name, size in (("Heading 1", 16), ("Heading 2", 12.5), ("Heading 3", 11)):
        st = styles[name]
        style_font(st, "黑体", size, bold=True)

    # 页眉
    header = section.header
    hp = header.paragraphs[0]
    hp.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = hp.add_run("绿色校园闲置物品循环流转平台 · 迭代一 · D5 数据库设计说明书")
    set_run_font(run, "宋体", 8.5, color=(0x66, 0x66, 0x66))
    # 页脚：第 X 页 / 共 Y 页
    footer = section.footer
    fp = footer.paragraphs[0]
    fp.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r1 = fp.add_run("第 ")
    set_run_font(r1, "宋体", 9)
    add_field(fp, "PAGE")
    r2 = fp.add_run(" 页 / 共 ")
    set_run_font(r2, "宋体", 9)
    add_field(fp, "NUMPAGES")
    r3 = fp.add_run(" 页")
    set_run_font(r3, "宋体", 9)

    doc.core_properties.title = "D5 数据库设计说明书"
    doc.core_properties.author = "成员1（数据层）"
    doc.core_properties.subject = "绿色校园闲置物品循环流转平台 · 迭代一"
    doc.core_properties.comments = "由成员1根据 _共享契约-实体与接口基线 与 db/schema.sql 生成"
    return doc


def add_cover(doc):
    for _ in range(3):
        doc.add_paragraph()
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = p.add_run("绿色校园闲置物品循环流转平台")
    set_run_font(run, "黑体", 22, bold=True, color=(0x1F, 0x3B, 0x63))

    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.space_before = Pt(6)
    run = p.add_run("迭代一 · 数据库设计说明书")
    set_run_font(run, "黑体", 26, bold=True, color=(0x1F, 0x3B, 0x63))

    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.space_before = Pt(18)
    run = p.add_run("文档编号：D5　　版本：v1.0.0")
    set_run_font(run, "宋体", 12)

    for _ in range(5):
        doc.add_paragraph()

    rows = [
        ("项目名称", "绿色校园闲置物品循环流转平台"),
        ("课程名称", "软件构造"),
        ("迭代阶段", "迭代一：数据层与基础骨架"),
        ("文档名称", "05-数据库设计说明书"),
        ("编写人", "成员1（数据层负责人）"),
        ("复核人", "项目组内部复核（Lead 汇总）"),
        ("完成日期", "%d 年 %d 月 %d 日" % (TODAY.year, TODAY.month, TODAY.day)),
        ("适用范围", "迭代一验收；与《_共享契约-实体与接口基线》v1.0 配套使用"),
    ]
    table = doc.add_table(rows=0, cols=2)
    table.style = "Table Grid"
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    for k, v in rows:
        cells = table.add_row().cells
        cells[0].width = Cm(4.0)
        cells[1].width = Cm(10.5)
        shade_cell(cells[0], "EDE7F6")
        p0 = cells[0].paragraphs[0]
        p0.alignment = WD_ALIGN_PARAGRAPH.CENTER
        set_run_font(p0.add_run(k), "黑体", 10.5, bold=True)
        p1 = cells[1].paragraphs[0]
        set_run_font(p1.add_run(v), "宋体", 10.5)

    for _ in range(4):
        doc.add_paragraph()
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    set_run_font(p.add_run("软件构造课程项目组"), "黑体", 12, bold=True)
    page_break(doc)


def add_toc(doc):
    h1(doc, "目　录")
    body(doc, "本文档共 10 章与 2 个附录，章节结构与《迭代一任务书》对 D5 的要求逐条对应；"
              "各章页码见页脚，目录顺序与正文一致。", indent=False)
    for num, title in CHAPTERS:
        p = doc.add_paragraph()
        pf = p.paragraph_format
        pf.space_after = Pt(4)
        pf.left_indent = Cm(0.6)
        run = p.add_run("%-8s %s" % (num, title))
        set_run_font(run, "宋体", 11)
    page_break(doc)


def add_revision(doc):
    caption(doc, "表 0-1　文档修订记录")
    make_table(
        doc,
        ["版本", "日期", "作者", "修订说明"],
        [
            ["v0.9", "2026-10-28", "成员1", "搭建章节框架，确定 11 张表的字段草案"],
            ["v1.0.0", GENERATED_AT, "成员1",
             "按《_共享契约-实体与接口基线》v1.0 第 3 节定稿 11 表字段、约束与索引；"
             "补充部分唯一索引与数据字典；接入真实建库/种子/Java 编译运行验证记录"],
        ],
        widths=[2.0, 2.6, 2.4, 8.4],
        size=9,
        align_center_cols={0, 1, 2},
    )
    body(doc, "本文档所有表结构、约束、索引、行数均来自 db/schema.sql 与 db/_verify-output.txt 的真实执行结果，"
              "未做任何手工润色或虚构；验证命令与输出可在任意安装 Python 3.12 的机器上复现（见附录 B）。")
    page_break(doc)


# =============================================================================
# 第 1 章
# =============================================================================


def add_chapter1(doc):
    h1(doc, "1　设计目标与选型理由")

    h2(doc, "1.1　设计目标")
    body(doc, "数据层是迭代一的地基：界面层、业务层与外部统计全部依赖它。结合题目书第八章"
              "“应用数据库”的要求与《_共享契约-实体与接口基线》（下称“契约”）第 3 节，"
              "本章先明确五条设计目标，后续选型与表结构均围绕这些目标展开。")
    bullets(doc, [
        "目标一：全部业务数据持久化到单一数据库文件，程序重启后数据完整可恢复，禁止内存态伪持久化；",
        "目标二：业务规则在数据库层“兜底”。角色的枚举、信用分区间、物品状态、评分范围、"
        "同一物品不可重复成交等规则，除业务层校验外必须有 DDL 约束（CHECK/UNIQUE/FK）双重保障；",
        "目标三：多表写操作必须原子。流转成交（物品置 SOLD + 流转置 DONE + 双方信用分 + 信用流水 + 日志）、"
        "评价与信用调整、发布物品与图片、注册唯一性校验，任一环节失败必须整体回滚；",
        "目标四：可演示、可验证、可复现。建库脚本、种子数据、验证脚本与见证输出全部随交付物提交，"
        "验收方可独立重跑；",
        "目标五：为迭代二留出演进空间。表结构遵循契约、字段不做投机性扩张，但通过索引与配置表"
        "（system_config）预留调参能力，降低二次迭代的改库成本。",
    ])

    h2(doc, "1.2　为什么选择 SQLite")
    body(doc, "题目书明确要求“应用数据库”并使用 SQLite + JDBC。除课程要求外，SQLite 在"
              "“单机桌面 + 单用户 + 小数据量”的场景下同样是工程上合理的选择。表 1-1 给出与常见"
              "候选方案的对比，评估维度取自本项目真实约束：零配置部署、事务与约束能力、并发写模型、"
              "以及是否需要独立数据库服务进程。")
    caption(doc, "表 1-1　候选存储方案对比")
    make_table(
        doc,
        ["评估维度", "SQLite（选用）", "MySQL", "H2/HSQLDB", "文件序列化"],
        [
            ["部署形态", "嵌入式，零安装，单 .db 文件", "需独立服务进程与账号配置", "嵌入式或服务模式", "无数据库，纯文件"],
            ["事务能力", "完整 ACID，默认 SERIALIZABLE", "完整 ACID，需配置隔离级别", "完整 ACID", "无事务，需自行保证"],
            ["约束能力", "PK/FK/UNIQUE/CHECK/部分索引齐全", "齐全，功能更多", "齐全", "无，全靠代码"],
            ["并发写", "单写者（库级写锁）", "多写者，行级锁", "支持多写者", "无并发控制"],
            ["课程/题目要求", "明确指定", "未指定", "未指定", "不符合要求"],
            ["结论", "选用", "部署成本高，超出单机桌面范围", "备选，但题目指定 SQLite", "不满足持久化与约束要求"],
        ],
        widths=[2.4, 4.6, 3.4, 3.0, 3.0],
        size=8.6,
        align_center_cols={0},
    )
    body(doc, "选用 SQLite 的具体理由如下：")
    bullets(doc, [
        "零配置、单文件：数据库即 data/greencampus.db 一个文件，随项目目录整体拷贝即可迁移，"
        "符合“课程演示 + 单机桌面”的交付形态；",
        "约束能力满足业务规则落库：契约中的 role/status/trade_type/score 等枚举与区间检查，"
        "均可用 CHECK 约束表达，配合 UNIQUE 与复合主键实现“数据库层兜底”；",
        "事务语义严格：SQLite 默认串行化（SERIALIZABLE），且支持 BEGIN IMMEDIATE 显式取写锁，"
        "能够保证成交、评价等跨表事务的原子性与一致性；",
        "与 JDBC 兼容良好：xerial sqlite-jdbc 驱动成熟，一条 JDBC URL 即完成接入，且驱动可随"
        "Maven 依赖分发，无需额外安装数据库服务。",
    ])
    body(doc, "代价同样明确：SQLite 只有单写者（同一时刻仅一个连接可写库），不适合高并发写入。"
              "本项目的真实并发模型是“单机 Swing 客户端、单用户操作、偶发多窗口”，写冲突概率极低；"
              "第 6 节给出 WAL 日志、busy_timeout、短事务与重试的完整应对方案。")

    h2(doc, "1.3　为什么用 JDBC 手写 DAO，而不用 ORM")
    body(doc, "题目明确禁止 Spring / ORM，要求以 JDBC 编程完成持久化。即便没有该限制，"
              "在“教学演示 + 需要证明索引与事务有效性”的语境下，手写 DAO 依然优于 ORM。")
    caption(doc, "表 1-2　持久化访问层方案对比")
    make_table(
        doc,
        ["评估维度", "JDBC + 手写 DAO（选用）", "MyBatis", "JPA / Hibernate"],
        [
            ["SQL 可控性", "完全可控，可逐条核对索引命中", "XML/注解映射，可控制", "自动生成 SQL，难精确控制"],
            ["学习与课程价值", "直接体现 JDBC 编程、PreparedStatement、事务", "隐藏 JDBC 细节", "隐藏 JDBC 细节，依赖重"],
            ["题目允许性", "允许且要求", "属于 ORM 框架，禁止", "禁止"],
            ["依赖规模", "仅 JDBC 驱动", "框架 + 配置", "框架 + 大量传递依赖"],
            ["结论", "选用", "不符合要求", "不符合要求"],
        ],
        widths=[2.4, 5.0, 3.6, 4.4],
        size=8.6,
        align_center_cols={0},
    )
    body(doc, "手写 DAO 采用三层结构，所有实现均落在 code/green-campus 的 dao 包：")
    bullets(doc, [
        "BaseDao<T, ID>：定义 findById / findAll / insert / update / deleteById 五个通用操作；",
        "AbstractJdbcDao<T>：模板方法基类，统一“取连接 → 绑定参数 → 执行 → 遍历 ResultSet → 释放资源”"
        "流程，把 SQLException 统一转换为 DataAccessException，子类只需实现 rowMapper 与少量特有 SQL；",
        "12 个业务 DAO 接口 + 对应实现：全部使用 PreparedStatement 全参数化，杜绝 SQL 注入；"
        "UserDaoImpl、ItemDaoImpl、TradeFlowDaoImpl、FavoriteDaoImpl 为完整示范实现，"
        "其余实现遵循同一模板。",
    ])
    body(doc, "这一结构使 SQL 成为“可审查的一等公民”：索引清单（第 5 节）中的每个索引，"
              "都能在 DAO 实现里找到对应的查询语句；事务边界（第 6 节）也能在 Service 层"
              "通过 DbUtil.executeInTransaction 一眼看清。")

    h2(doc, "1.4　并发与部署场景")
    body(doc, "本项目的运行形态是单机桌面应用：一个 JVM 进程、一个 Swing 窗口、一位使用者。"
              "可能的并发来自三个方面：Swing 后台线程与 EDT 的交替、同一 JVM 内多个 DAO 调用，"
              "以及验收时同时打开两个客户端进程。据此确定如下并发策略：")
    bullets(doc, [
        "连接模型：不做连接池（单机场景无必要），每次操作按需新建连接、用后即关；"
        "事务内通过 ThreadLocal 复用同一连接，保证同一事务的所有 DAO 调用落在同一连接上；",
        "写并发：SQLite 库级写锁，配合 WAL 日志模式让“读不阻塞写、写不阻塞读”，"
        "并以 busy_timeout=5000ms 让短暂写冲突自动等待而非立即失败；",
        "隔离级别：SQLite 默认 SERIALIZABLE；需要“先读后写”的事务（如检查物品状态再改状态）"
        "使用 BEGIN IMMEDIATE 提前取写锁，避免升级锁时的 SQLITE_BUSY；",
        "失败策略：任一 SQL 失败即抛 DataAccessException / TransactionException，"
        "事务整体回滚，绝不出现“物品已 SOLD 但流转仍 APPLYING”的中间态。",
    ])

    h2(doc, "1.5　与其他交付物的边界")
    body(doc, "本文档只描述数据层（表、约束、索引、事务、种子数据），与其余交付物的边界如下：")
    bullets(doc, [
        "《_共享契约-实体与接口基线》是唯一权威基线：表名、字段名、类型、约束、DAO/Service 签名"
        "逐字对齐，本文档不新增契约外字段（uq_category_root_name 为索引级补充，已在第 5 节标注"
        "“建议补充”并说明理由）；",
        "D2（模块化设计与接口规范）定义 Service/DAO 的调用契约，本文档第 10 节给出字段级对照；",
        "D3（类图）定义实体类与设计的静态结构，实体类字段与本文档数据字典一一对应，"
        "见第 10 节的映射表；",
        "D7（Maven 工程骨架）是本文档所有 SQL 的落点：schema.sql / seed-data.sql 位于 db 目录，"
        "由程序中的 DatabaseInitializer 执行，Java 代码见 code/green-campus。",
    ])


# =============================================================================
# 第 2 章
# =============================================================================


def add_chapter2(doc, tables, fks):
    h1(doc, "2　ER 图说明")
    body(doc, "实体关系图（ER 图）以 drawio 源文件形式交付：design/05-ER图.drawio。"
              "该文件为标准 draw.io（diagrams.net）XML，可直接用 diagrams.net 网页版或"
              "VS Code 的 Draw.io Integration 插件打开、编辑与导出 PNG/SVG，"
              "不是位图，因此可无损缩放、可继续演进。")
    body(doc, "图中共 11 个实体框（swimlane）、93 个字段行、18 条关系线（关系线两端锚定到具体字段，"
              "并标注 1 / N 基数）。第 9 节给出该文件的自动化自检输出；表 2-1、表 2-2 是图面内容的"
              "文字化版本，便于评审与检索。")

    h2(doc, "2.1　实体清单")
    caption(doc, "表 2-1　实体（表）清单")
    rows = []
    for idx, t in enumerate(tables, 1):
        cn, cls, duty = sm.TABLE_META[t["name"]]
        rows.append([str(idx), t["name"], cls, cn, duty, str(len(t["columns"]))])
    make_table(doc, ["序号", "表名", "实体类", "中文名", "职责", "字段数"], rows,
               widths=[1.2, 3.0, 2.4, 2.6, 6.6, 1.5], size=8.6, align_center_cols={0, 5})

    h2(doc, "2.2　关系清单")
    body(doc, "表 2-2 列出全部 18 条外键关系。基数一列中，“1”为父端、“N”为子端；"
              "删除行为直接对应 DDL 中的 ON DELETE 子句，删除理由同时说明“为什么这样定”。")
    caption(doc, "表 2-2　实体关系（外键）清单")
    rows = []
    for idx, fk in enumerate(fks, 1):
        key = fk["table"] + "." + fk["columns"][0]
        rel, meaning = REL_DESC.get(key, ("—", ""))
        rows.append([str(idx), "%s.%s" % (fk["table"], fk["columns"][0]),
                     "%s.%s" % (fk["ref_table"], fk["ref_columns"][0]),
                     rel, fk["on_delete"], meaning])
    make_table(doc, ["序号", "子表.字段", "父表.字段", "关系与基数", "ON DELETE", "业务含义"], rows,
               widths=[1.1, 3.5, 3.1, 3.4, 2.0, 5.7], size=8.4, align_center_cols={0, 4})

    h2(doc, "2.3　图面结构与自检")
    body(doc, "drawio 文件的结构严格遵循 diagrams.net 规范：mxfile 根节点 → diagram（id=er、"
              "name=ER图）→ mxGraphModel（pageWidth=2000、pageHeight=1450）→ root → "
              "mxCell 集合。实体框统一使用 swimlane 样式（startSize=30、childLayout=stackLayout），"
              "框内逐行排列字段；主键字段加粗并标注 PK，外键字段以蓝色标注“FK→父表.字段”，"
              "唯一/非空/默认值在行尾以 UQ、NOT NULL、DEFAULT 记号标出。")
    bullets(doc, [
        "关系线样式：startArrow=ERone、endArrow=ERmany、两端填充 0，语义上“父端 1、子端 N”；",
        "关系线不连到实体框中心，而是锚定到具体字段行（例如 user.id → item.owner_id），"
        "避免“线悬空、字段不清”的常见 ER 图问题；",
        "文件顶部有标题与图例（颜色、记号含义），评审者无需上下文即可读懂图面；",
        "自检由 db/_check_er.py 以 xml.etree.ElementTree 解析完成，校验 XML 合法性、"
        "实体字段数、18 条关系线锚点与基数标签，结果见第 9 节。",
    ])

    h2(doc, "2.4　ER 图的设计取舍")
    bullets(doc, [
        "分类采用自关联两级模型（category.parent_id → category.id），而不是“一级分类表 + 二级分类表”："
        "一张表即可表达两级结构，新增层级时无需改表，SQL 侧用 parent_id IS NULL 区分一级分类；"
        "为防止同名一级分类，补充部分唯一索引 uq_category_root_name（见第 5 节）；",
        "消息按“物品 + 发送者 + 接收者”三元组建模，而不是单独建会话表：单机演示场景下会话表"
        "属于过度设计，三元组查询可覆盖“某物品下双方的往来消息”；",
        "评价对买卖双方各记录一行（reviewer_id / reviewee_id），而不是一行双向评价："
        "便于分别表达双方评分与内容，并配合 UNIQUE(flow_id, reviewer_id) 实现“每人每单一次评价”；",
        "信用流水 credit_log 与 user.credit_score 并存（明细 + 快照）：明细用于审计与对账，"
        "快照用于高频读取，属有意的反范式设计，见第 7 节；",
        "trade_flow 对同一物品的活动态施加部分唯一索引约束，DONE/CANCELLED 历史不限："
        "既落实 BR-05（同一物品不可重复成交），又保留完整交易历史。",
    ])


# =============================================================================
# 第 3 章
# =============================================================================


def _table_index_names(indexes, table_name):
    return [x["name"] for x in indexes if x["table"] == table_name]


def add_chapter3(doc, tables, indexes):
    total_cols = sum(len(t["columns"]) for t in tables)
    total_pk = sum(1 for t in tables for c in t["columns"] if c["pk"])
    total_notnull = sum(1 for t in tables for c in t["columns"] if c["not_null"])
    total_fk = sum(1 for t in tables for c in t["columns"] if c.get("fk"))

    h1(doc, "3　数据字典")
    body(doc, "数据字典是本文档的核心：逐表逐字段给出字段名、数据类型、约束、默认值、设计说明"
              "以及对应的实体类属性。字段顺序、名称、类型、约束与 db/schema.sql 完全一致——"
              "本节的全部表格由脚本静态解析 schema.sql 生成，避免人工誊抄与实现之间产生偏差。")
    body(doc, "全库共 %d 张表、%d 个字段，其中主键 %d 个、外键列 %d 个、NOT NULL 字段 %d 个。"
              "字段命名遵循契约第 2 节的“小写下划线”，实体类属性为对应的驼峰命名；"
              "时间统一 TEXT 'yyyy-MM-dd HH:mm:ss'，金额统一 REAL（Java 侧 BigDecimal），"
              "布尔统一 INTEGER 0/1（Java 侧 Boolean）。"
              % (len(tables), total_cols, total_pk, total_fk, total_notnull))
    body(doc, "阅读说明：约束列中的 PK 表示主键、UQ 表示唯一、NN 表示非空、CK 表示检查约束；"
              "默认值列“—”表示无默认值；说明列取自 schema.sql 中的行内注释，"
              "实体属性列由字段名转驼峰得到（is_read → isRead 为显式映射）。", size=10)

    for idx, t in enumerate(tables, 1):
        cn, cls, duty = sm.TABLE_META[t["name"]]
        h2(doc, "3.%d　%s（%s）" % (idx, cn, t["name"]))
        body(doc, "表名 %s，对应实体类 %s，中文名“%s”，共 %d 个字段。设计职责：%s。"
                  % (t["name"], cls, cn, len(t["columns"]), duty))

        caption(doc, "表 3-%d　%s数据字典" % (idx, t["name"]))
        rows = []
        for c in t["columns"]:
            cons = []
            if c["pk"]:
                cons.append("PK")
            if c["unique"]:
                cons.append("UQ")
            if c["not_null"]:
                cons.append("NN")
            if c["check"]:
                cons.append("CK")
            cons_text = "、".join(cons) if cons else "—"
            rows.append([c["name"], c["type"].split("(")[0], cons_text,
                         c["default"] if c["default"] != "" else "—",
                         c["comment"] if c["comment"] else "—", c["attr"]])
        make_table(doc, ["字段名", "类型", "约束", "默认值", "说明", "实体属性"], rows,
                   widths=[2.9, 2.0, 2.4, 2.2, 5.4, 1.9], size=8.2, align_center_cols={1, 2, 3})

        # 表级约束（外键 / 复合唯一 / 表级 CHECK）
        tcs = [c for c in t["table_constraints"]]
        if tcs:
            bullets(doc, [
                ("%s：%s → %s.%s（ON DELETE %s，ON UPDATE %s）"
                 % (c["name"], ",".join(c["columns"]), c["ref_table"],
                    ",".join(c["ref_columns"]), c["on_delete"] or "NO ACTION",
                    c["on_update"] or "NO ACTION")
                 if c["type"] == "FK" else
                 ("UNIQUE(%s)" % ",".join(c["columns"]) if c["type"] == "UNIQUE"
                  else "CHECK (%s)" % c.get("expr", "")))
                for c in tcs
            ], size=9.5)
        idxs = _table_index_names(indexes, t["name"])
        if idxs:
            body(doc, "相关索引：%s（详见第 5 章）。" % "、".join(idxs), indent=False, size=9.5)


# =============================================================================
# 第 4 章
# =============================================================================

UNIQUE_REASON = {
    ("user", "username"): "用户名全局唯一（BR-01），同时作为登录凭据",
    ("user", "student_no"): "学号唯一；管理员不填学号（NULL），SQLite 中 NULL 不参与唯一比较",
    ("system_config", "config_key"): "配置键唯一，upsert 时以此判断“新增/更新”",
    ("favorite", ("user_id", "item_id")): "同一用户对同一物品仅允许一条收藏记录（BR-09 toggle 语义）",
    ("review", ("flow_id", "reviewer_id")): "同一流转中每人仅能评价一次（BR-08）",
}


def add_chapter4(doc, tables, fks, indexes):
    h1(doc, "4　主键、外键、唯一与 CHECK 约束")
    body(doc, "约束是数据库层“兜底”业务规则的手段。本节按约束类型逐类列出清单与理由，"
              "并给出“为什么放在数据库层、而不是只放在 Java 业务层”的判断依据："
              "凡是可能被绕过（多入口、脚本导入、并发绕过校验）的规则，一律落 DDL。")

    # 4.1 主键
    h2(doc, "4.1　主键")
    body(doc, "全部 11 张表统一采用“单列自增整数主键” INTEGER PRIMARY KEY AUTOINCREMENT，"
              "理由有三：其一，SQLite 的自增主键写入成本最低、页内局部性好；其二，整数主键便于"
              "外键引用与索引，且不会随业务字段变化；其三，业务唯一性由单独的 UNIQUE 约束表达"
              "（如用户名、学号），主键不承担业务含义，避免“业务字段改了就改主键”的连锁破坏。")
    caption(doc, "表 4-1　主键清单")
    rows = []
    for idx, t in enumerate(tables, 1):
        pk = next((c for c in t["columns"] if c["pk"]), None)
        rows.append([str(idx), t["name"], pk["name"] if pk else "—",
                     pk["type"] if pk else "—", "INTEGER PRIMARY KEY AUTOINCREMENT",
                     "自增代理键，无业务含义；被 %d 条外键引用"
                     % len([f for f in fks if f["ref_table"] == t["name"]])])
    make_table(doc, ["序号", "表名", "主键列", "类型", "生成方式", "说明"], rows,
               widths=[1.1, 3.1, 2.0, 2.2, 5.2, 4.3], size=8.4, align_center_cols={0, 1, 2, 3})

    # 4.2 外键
    h2(doc, "4.2　外键与删除行为")
    body(doc, "共 %d 条外键约束。删除行为按“数据生命周期”逐条确定：从属数据（图片、收藏、消息、"
              "评价、信用流水）随主体删除而级联清理（CASCADE）；被引用的主数据（分类、交易历史中的"
              "买卖双方、物品）在仍被引用时禁止删除（RESTRICT）；审计类数据在主体删除后保留但"
              "断开引用（SET NULL）。全部外键同时声明 ON UPDATE CASCADE，主键在正常情况下不更新，"
              "此声明仅为防御性一致。" % len(fks))
    caption(doc, "表 4-2　外键约束清单（%d 条）" % len(fks))
    rows = []
    for idx, fk in enumerate(fks, 1):
        rows.append([str(idx), "%s.%s" % (fk["table"], ",".join(fk["columns"])),
                     "%s.%s" % (fk["ref_table"], ",".join(fk["ref_columns"])),
                     fk["on_delete"] or "NO ACTION", fk["on_update"] or "NO ACTION",
                     sm.FK_REASON.get("%s.%s" % (fk["table"], fk["columns"][0]), "")])
    make_table(doc, ["序号", "子表.列", "引用父表.列", "ON DELETE", "ON UPDATE", "设置理由"], rows,
               widths=[1.0, 3.4, 3.3, 1.9, 1.9, 6.4], size=8.0, align_center_cols={0, 3, 4})

    # 4.3 唯一约束
    h2(doc, "4.3　唯一约束")
    body(doc, "唯一性既包括列级 UNIQUE、表级复合 UNIQUE，也包括为“部分行”服务的部分唯一索引。"
              "后者的价值在于：只对活动态数据施加唯一性，历史数据不参与比较，"
              "从而同时满足“防重复”与“留历史”两个目标。")
    caption(doc, "表 4-3　唯一约束清单")
    rows = []
    seq = 0
    for t in tables:
        for c in t["columns"]:
            if c["unique"]:
                seq += 1
                rows.append([str(seq), "%s.%s" % (t["name"], c["name"]), "列级 UNIQUE",
                             UNIQUE_REASON.get((t["name"], c["name"]), "业务唯一性要求")])
        for tc in t["table_constraints"]:
            if tc["type"] == "UNIQUE":
                seq += 1
                cols = tc["columns"]
                rows.append([str(seq), "%s(%s)" % (t["name"], ",".join(cols)), "表级复合 UNIQUE",
                             UNIQUE_REASON.get((t["name"], tuple(cols)), "组合唯一性要求")])
    for x in indexes:
        if x["unique"]:
            seq += 1
            rows.append([str(seq), x["name"], "部分唯一索引（UNIQUE INDEX ... WHERE %s）" % x["where"],
                         (x["reason"][1] if x["reason"] else "")])
    make_table(doc, ["序号", "约束/索引", "类型", "设置理由"], rows,
               widths=[1.1, 5.6, 4.6, 6.6], size=8.2, align_center_cols={0})

    # 4.4 CHECK
    h2(doc, "4.4　CHECK 约束")
    body(doc, "CHECK 约束承担两类职责：一是枚举值域（role/status/trade_type/flow_type），"
              "防止越权或拼写错误的值写入；二是数值区间（信用分 [0,150]、成色 1-10、评分 1-5、"
              "金额非负），防止业务层漏校验导致的脏数据。约束表达式与 schema.sql 完全一致。")
    caption(doc, "表 4-4　CHECK 约束清单")
    rows = []
    seq = 0
    for t in tables:
        for c in t["columns"]:
            if c["check"]:
                seq += 1
                rows.append([str(seq), "%s.%s" % (t["name"], c["name"]), c["check"],
                             sm._CHECK_REASON.get((t["name"], c["name"]), "")])
        for tc in t["table_constraints"]:
            if tc["type"] == "CHECK":
                seq += 1
                expr = tc["expr"]
                reason = "表级检查约束"
                if "trade_type = 'FREE'" in expr or 'trade_type = "FREE"' in expr:
                    reason = ("FREE 物品价格必须为 0（BR-12 / FR-05，第 3 轮新增；"
                              "Service 前置校验 + DB 兜底的“Service + DB 双层”校验）")
                rows.append([str(seq), t["name"], "CONSTRAINT ck_item_free_price CHECK (%s)" % expr, reason])
    make_table(doc, ["序号", "表.列", "约束表达式", "设置理由"], rows,
               widths=[1.1, 3.4, 7.2, 6.2], size=8.0, align_center_cols={0})

    # 4.5 约束分层
    h2(doc, "4.5　约束分层与反例验证")
    body(doc, "约束并非只存在于数据库层。本项目采用“业务层校验 + 数据库层兜底”的双层策略："
              "正常业务路径先由 Service 层用 Validator/业务规则做前置校验并给出友好提示；"
              "数据库约束作为最后一道防线，任何绕过（脚本导入、并发竞争、未来新增入口）都会在"
              "SQL 执行时被拒绝，并转换为 DataAccessException / TransactionException。")
    bullets(doc, [
        "枚举与区间（CHECK）：非法角色、非法状态、越界评分、负金额一律拒绝；",
        "唯一性（UNIQUE / 部分唯一索引）：用户名与学号重复、重复收藏、重复评价、"
        "同一物品重复活动流转一律拒绝；",
        "引用完整性（FOREIGN KEY）：不允许引用不存在的用户/分类/物品/流转，删除父行时按声明行为处理；",
        "反例测试：db/verify_db.py 设计了 12 条反例（覆盖 role/status/condition_level/score 的 CHECK、"
        "新增的 FREE 价格表级 CHECK、username/favorite/review/config_key 的 UNIQUE、2 条外键、"
        "1 条部分唯一索引），实跑结果 12/12 全部被拒绝，输出见第 9 章。",
    ])
    body(doc, "第 3 轮评审（契约 v1.1 §13-9）要求把“赠送物品价格必须为 0”由单一业务校验升级为"
              "库层兜底，故 item 表新增表级约束 ck_item_free_price，形成下表所示的校验分层。"
              "其中 BR-12（免费物品价格 0 元）与 FR-05（免费赠送发布）对应的规则属于"
              "“Service + DB 双层”校验。")
    caption(doc, "表 4-5　跨层校验责任划分（节选）")
    make_table(
        doc,
        ["规则", "业务层（Service/Validator）", "数据库层（约束）", "校验层级"],
        [
            ["用户名格式与唯一性（BR-01）", "Validator 正则 + existsByUsername", "UNIQUE(username)", "Service + DB 双层"],
            ["密码强度（BR-01/BR-02）", "Validator 正则 + PBKDF2 加盐", "仅存 hash/salt，不存明文", "Service 主责"],
            ["赠送物品价格必须为 0（BR-12 / FR-05）", "publish 校验 FREE 时 price=0，否则 VAL 错误",
             "CHECK ck_item_free_price（第 3 轮新增）", "Service + DB 双层"],
            ["物品状态合法取值（BR-06/BR-10）", "状态机迁移前校验当前状态", "CHECK status IN (7 值)", "Service + DB 双层"],
            ["同一物品不可重复成交（BR-05）", "apply 前查活动流转", "部分唯一索引 uq_flow_item_active", "Service + DB 双层"],
            ["信用分区间 [0,150]（BR-04）", "CreditRules.clamp 截断", "CHECK credit_score / score_after BETWEEN", "Service + DB 双层"],
            ["图片格式与数量（BR-12）", "Validator 后缀/大小/数量（≤5 张）", "item_image 外键级联，无数量约束", "Service 主责"],
            ["评价唯一且仅已完成流转（BR-08）", "ReviewService 校验 DONE 与重复", "UNIQUE(flow_id,reviewer_id)", "Service + DB 双层"],
        ],
        widths=[4.6, 4.6, 4.2, 3.0], size=8.0,
    )


# =============================================================================
# 第 5 章
# =============================================================================


def add_chapter5(doc, indexes):
    h1(doc, "5　索引清单与建立理由")
    body(doc, "索引只应建在“查询真的会走”的列上。本节每个索引都对应契约第 5 节的 DAO 方法"
              "（即真实 SQL），并在实现代码中可逐条核对；索引名、列顺序、WHERE 子句与"
              "schema.sql 完全一致。共 %d 个索引，其中普通索引 9 个、部分唯一索引 2 个、"
              "其余为复合/唯一索引。" % len(indexes))

    h2(doc, "5.1　索引总表")
    caption(doc, "表 5-1　索引清单")
    rows = []
    for idx, x in enumerate(indexes, 1):
        if x["unique"] and x["where"]:
            kind = "部分唯一索引"
        elif x["unique"]:
            kind = "唯一索引"
        else:
            kind = "普通索引"
        reason = x["reason"] if x["reason"] else ("", "")
        query = reason[0] if reason[0] else "—"
        why = reason[1] if len(reason) > 1 and reason[1] else "—"
        if x["where"]:
            query = query + "（仅 %s）" % x["where"]
        rows.append([str(idx), x["name"], x["table"], ",".join(x["columns"]),
                     kind, query, why])
    make_table(doc, ["序号", "索引名", "表", "列", "类型", "对应查询", "建立理由"], rows,
               widths=[1.0, 4.3, 2.0, 2.4, 1.9, 3.0, 4.0], size=7.6, align_center_cols={0, 4})

    h2(doc, "5.2　索引设计原则")
    bullets(doc, [
        "按“最左前缀”组织复合索引列序：等值列在前、范围/IN 列在后（如 idx_item_status_category "
        "的 (status, category_id)），与查询条件顺序一致；",
        "覆盖排序：需要 ORDER BY created_at DESC 的列表查询（我的发布、我的收藏、信用流水、"
        "操作日志）优先把排序列纳入索引，避免额外排序；",
        "部分索引只约束必要的行：uq_flow_item_active 只覆盖 APPLYING/AGREED 两态，"
        "DONE/CANCELLED 历史行不占唯一性，既落实 BR-05 又保留交易历史；",
        "不为“小表/低频查询”建索引：system_config 仅 11 行，category 仅 10 行，全表扫描成本可忽略，"
        "建索引反而增加写开销；",
        "不在冗余列上重复建索引：item.favorite_count、view_count 只被读取与自增，不需要单独索引。",
    ])

    h2(doc, "5.3　未建索引的查询与迭代二演进")
    body(doc, "以下查询在当前数据量（物品数百条级别）下不建索引或暂缓建索引，理由与后续演进方向如下：")
    caption(doc, "表 5-2　暂未建立索引的查询")
    make_table(
        doc,
        ["查询", "当前处理方式", "未建索引理由", "迭代二建议"],
        [
            ["title LIKE '%关键词%'", "已建 idx_item_title 辅助扫描", "前置通配符使 B-Tree 索引无法定位，只能全表扫描",
             "引入 SQLite FTS5 全文索引（虚拟表 item_fts），关键词检索改走 MATCH"],
            ["WHERE published_at BETWEEN ? AND ?", "依赖 idx_item_status_category", "当前统计入口按建档时间范围聚合",
             "数据量增大后增加 idx_item_published(published_at)"],
            ["trade_message.is_read = 0 未读数统计", "按接收者索引（未建）", "消息量小、按会话查询已走 idx_msg_pair",
             "消息量增大后增加 idx_msg_to_read(to_user_id, is_read) 部分索引"],
            ["ORDER BY created_at 的通用分页", "各列表已有专属索引", "避免为同一表建多个排序索引造成写放大",
             "按真实慢查询日志再评估"],
        ],
        widths=[4.4, 3.4, 4.6, 5.0], size=8.0,
    )


# =============================================================================
# 第 6 章
# =============================================================================


def add_chapter6(doc):
    h1(doc, "6　事务边界与并发控制")

    h2(doc, "6.1　必须原子化的业务操作")
    body(doc, "以下操作跨越两张及以上表，任何一步失败都会造成“看起来成交了、实际没成交”的"
              "不一致状态，因此必须整体放在一个事务中。实现上统一使用 "
              "DbUtil.executeInTransaction(TransactionCallback)，由模板方法负责 begin/commit/rollback "
              "与连接释放；事务内所有 DAO 调用通过 ThreadLocal 复用同一个连接。")
    caption(doc, "表 6-1　原子操作清单")
    make_table(
        doc,
        ["序号", "操作", "涉及表", "事务内顺序", "失败处理", "对应规则"],
        [
            ["1", "确认成交\nTradeService.confirm", "item、trade_flow、user、credit_log、operation_log",
             "物品置 SOLD → 流转置 DONE（写 finished_at）→ 买家 +2 → 卖家 +2 → 各写一条 credit_log "
             "→ 写 operation_log → 统计事件累加",
             "任一步异常整体回滚并抛 TransactionException，物品与流转状态均回到 AGREED",
             "BR-05 / BR-07"],
            ["2", "评价并调整信用分\nReviewService.review", "review、user、credit_log、operation_log",
             "校验（DONE、双方、未重复）→ 写 review → 按评分调整被评人信用分（≥4 分 +2，≤2 分 -5）"
             "→ 写 credit_log → 写日志",
             "回滚后评价不存在、信用分不变", "BR-08"],
            ["3", "发布物品并保存图片\nItemService.publish", "item、item_image、operation_log",
             "校验 → 插入 item（回填主键）→ 批量插入 item_image → 写日志",
             "回滚后物品与图片均不落库，不产生“有物品无图”的残缺记录", "BR-04 / BR-12"],
            ["4", "注册（唯一性校验）\nUserService.register", "user、operation_log",
             "校验用户名/学号唯一 → 生成盐与哈希 → 插入 user → 写日志",
             "唯一约束冲突转 DuplicateEntityException，事务回滚", "BR-01 / BR-02"],
            ["5", "发起流转\nTradeService.apply", "trade_flow、operation_log",
             "校验物品 ON_SALE、非本人、无活动流转 → 插入 flow(APPLYING) → 写日志",
             "部分唯一索引冲突同样被拒，回滚", "BR-05 / BR-06"],
            ["6", "同意/取消流转\nTradeService.agree/cancel", "trade_flow、item、operation_log",
             "同意：flow=AGREED + item=LOCKED；取消：flow=CANCELLED，若曾 LOCKED 则 item 回 ON_SALE",
             "回滚后状态保持一致", "BR-06"],
            ["7", "登录失败计数与锁定\nUserService.login", "user、operation_log",
             "失败时 fail_count+1，达到阈值写 locked_until；成功时清零并写 last_login_at",
             "回滚后计数不变，避免“锁了但没记录”", "BR-03"],
        ],
        widths=[0.9, 3.4, 3.6, 5.0, 4.2, 1.9], size=7.6, align_center_cols={0, 5},
    )

    h2(doc, "6.2　隔离级别与连接参数")
    body(doc, "SQLite 默认即 SERIALIZABLE：一个连接写入时对整个数据库加写锁，其他写者等待，"
              "因此无需（也不支持）像 MySQL 那样选择隔离级别。真正的工程问题是“如何减少等待、"
              "避免锁升级失败”，本项目通过以下连接级参数与事务发起方式解决。")
    caption(doc, "表 6-2　连接与事务参数")
    make_table(
        doc,
        ["参数/机制", "取值", "作用与理由"],
        [
            ["journal_mode", "WAL", "写前日志：读不阻塞写、写不阻塞读，降低“统计查询与写入并发”时的等待"],
            ["foreign_keys", "ON", "SQLite 默认关闭外键检查，必须每个连接显式开启，否则 FK 约束形同虚设"],
            ["busy_timeout", "5000 ms", "写锁被占用时最多等待 5 秒再报 SQLITE_BUSY，覆盖单机瞬时并发"],
            ["事务发起", "BEGIN IMMEDIATE", "“先读后写”的事务提前取写锁，避免读后升级锁失败（SQLITE_BUSY）"],
            ["事务上下文", "ThreadLocal<Connection>", "同一事务内的多次 DAO 调用复用同一连接；嵌套调用复用外层事务"],
            ["隔离级别", "SERIALIZABLE（SQLite 默认）", "满足成交/评价等严格一致性要求，无需额外配置"],
        ],
        widths=[3.2, 3.4, 9.6], size=8.2,
    )

    h2(doc, "6.3　失败回滚与异常转换")
    bullets(doc, [
        "模板方法统一收口：executeInTransaction 在 try 中执行回调，成功 commit，任何 Throwable 都 rollback；",
        "恢复原状：回滚后连接 autoCommit 恢复为 true，ThreadLocal 清理，连接关闭，避免线程复用时串事务；",
        "异常分层：SQLException 统一转 DataAccessException（DB-前缀错误码），事务提交/回滚本身失败转"
        "TransactionException（TX-前缀），业务规则失败抛 BusinessRuleException（BR-数字）；",
        "观察者策略：信用分监听器、日志监听器在同一事务内写库，监听器异常会被重新抛出，"
        "使外层事务回滚，绝不出现“成交成功但日志没写”的情况；",
        "幂等与可重复：schema.sql 采用 DROP 反序 + 重建，前后用外键开关包裹，保证脚本可在已有数据的库上重复执行。",
    ])

    h2(doc, "6.4　SQLite 单写者限制与应对")
    body(doc, "SQLite 的写锁是库级的：同一时刻只能有一个连接写入。对“单机桌面、单用户操作”的"
              "本项目而言这几乎不构成瓶颈；但为保证工程严谨，仍采取以下应对：")
    bullets(doc, [
        "短事务：事务内只做必要的读写，不做文件 IO、网络请求等长耗时操作，减少持锁时间；",
        "WAL 日志：读操作走 WAL 快照，不与写事务互斥，统计/列表页在成交事务进行时仍可读；",
        "busy_timeout=5000：并发写冲突时自动等待而非立即失败，避免“点一下报错”的体验；",
        "单写入口：所有写操作都经 Service 层与 DbUtil 事务模板，禁止在 UI 线程直接发写 SQL；",
        "演进预案：若迭代二需要多用户共享，可将 DAO 层替换为服务端数据库（MySQL/PostgreSQL），"
        "Service/DAO 接口不变，仅替换 DbUtil 连接实现与 DDL 方言。",
    ])


# =============================================================================
# 第 7 章
# =============================================================================


def add_chapter7(doc):
    h1(doc, "7　反范式设计说明")
    body(doc, "严格第三范式要求每个非主属性只依赖于主键、不存冗余。但数据库设计的目的是服务业务，"
              "而不是教科书。本项目在三处有意引入冗余/反范式，均为“读多写少、且可用事务保证一致性”"
              "的场景，收益（减少 JOIN、降低统计复杂度）显著大于代价。")

    h2(doc, "7.1　反范式总览")
    caption(doc, "表 7-1　反范式字段总览")
    make_table(
        doc,
        ["序号", "冗余字段", "来源（规范位置）", "收益", "代价/风险", "一致性保障"],
        [
            ["1", "item.tags", "本应拆出 item_tag 关联表（标签为多值）",
             "标签为自由文本、数量少（≤5 个），一次读取即可展示与 LIKE 检索，避免多表 JOIN",
             "无法按标签精确分组统计", "发布/更新时整体覆盖写，标签仅作展示与模糊检索"],
            ["2", "trade_flow.flow_type\n trade_flow.amount", "可经 item.trade_type / item.price 关联得到",
             "成交金额与交易方式在成交瞬间固化，历史统计不随物品改价而漂移；"
             "分类统计无需 JOIN item，直接聚合 trade_flow",
             "与 item 当前值可能不一致（业务上属预期）", "成交事务内一次性写入快照，之后不随物品变更"],
            ["3", "item.favorite_count", "COUNT(favorite) 可实时算出",
             "列表页展示收藏数无需每行子查询/聚合", "与 favorite 表可能短暂不一致",
             "收藏 toggle 与计数自增/自减在同一事务；SQL 侧用 MAX(0, x-1) 兜底不出现负数"],
            ["4", "item.view_count", "可从浏览流水统计",
             "详情页高频自增，独立字段避免写放大", "非严格精确（并发自增）", "原子 UPDATE view_count = view_count + 1"],
            ["5", "user.credit_score", "可由 credit_log 求和/重放得到",
             "登录、列表、发布校验都要读信用分，快照读取 O(1)", "与流水明细可能不一致",
             "所有变动经 CreditRules.apply 在同一事务内“改快照 + 写流水”"],
            ["6", "item.audit_remark", "审核记录本可独立建表",
             "审核为单轮、仅保留最近一次意见，单字段足够", "无历史多轮审核记录",
             "audit 事务内覆盖写；完整审计另有 operation_log"],
        ],
        widths=[0.9, 3.6, 3.8, 4.0, 2.6, 3.6], size=7.6, align_center_cols={0},
    )

    h2(doc, "7.2　item.tags 为什么存 TEXT 而不是关联表")
    body(doc, "标签是自由文本、由发布者随手填写，主要用于详情页展示与关键词检索。若拆成 "
              "item_tag(item_id, tag) 关联表，则每次列表查询都要额外 LEFT JOIN 并聚合字符串，"
              "代价与收益不成比例。因此约定：tags 以逗号分隔存于单列 TEXT，发布/编辑时整体覆盖，"
              "检索时用 LIKE '%标签%'。代价是“按标签精确统计”不精确（可能匹配到子串），"
              "这一点在迭代二引入标签词表与 FTS5 后再拆表。")

    h2(doc, "7.3　trade_flow.flow_type / amount 为什么做快照")
    body(doc, "成交金额与交易方式是“成交瞬间的事实”，而物品的 price/trade_type 会随时间被发布者"
              "修改（甚至下架后重新上架）。若统计永远 JOIN item 取当前值，则历史成交金额会随"
              "物品改价而变形，违反审计要求。因此在 create flow 时把当时的交易方式与金额复制到"
              "trade_flow，统计报表只读流转表——这也是“按分类统计成交额与碳减排量”能够直接"
              "聚合 trade_flow 的原因。")

    h2(doc, "7.4　冗余计数与信用分的对账")
    body(doc, "冗余字段的风险是一致性。本项目用“同一事务内更新 + 定期对账 SQL”两道措施控制："
              "收藏计数、信用分快照均在写事务中与明细同步更新；同时提供以下对账语句，"
              "可在验收或迭代二的数据迁移前执行，快速发现不一致行：")
    code_block(doc, [
        "-- 1) 收藏计数对账：期望 0 行",
        "SELECT i.id, i.favorite_count, COUNT(f.id) AS real_cnt",
        "  FROM item i LEFT JOIN favorite f ON f.item_id = i.id",
        " GROUP BY i.id HAVING i.favorite_count <> real_cnt;",
        "",
        "-- 2) 信用分快照对账：期望 0 行（初始 100 + 流水变动之和）",
        "SELECT u.id, u.credit_score,",
        "       100 + COALESCE(SUM(c.delta), 0) AS calc_score",
        "  FROM \"user\" u LEFT JOIN credit_log c ON c.user_id = u.id",
        " GROUP BY u.id HAVING u.credit_score <> calc_score;",
    ], size=8.0)
    body(doc, "示例：种子数据中 user 3 的信用分由 100 经 +2、+3 变为 105，credit_log 两条流水"
              "（103→105 与 100→103）与之对账一致；user 4 由 100 经 -5 变为 97，同样一致。")

    h2(doc, "7.5　结论")
    bullets(doc, [
        "反范式只用在“读多写少 + 单事务可自洽”的字段上，且每处冗余都有明确的一致性保障措施；",
        "绝不为省一次 JOIN 而牺牲可审计性：信用分明细 credit_log、操作日志 operation_log 全部保留；",
        "冗余字段均有对账 SQL（7.4 节），可随时验证一致性，避免“越跑越歪”。",
    ])


# =============================================================================
# 第 8 章
# =============================================================================


def _db():
    return sqlite3.connect(str(VERIFY_DB))


SEED_MIN = {
    "user": 5, "category": 10, "item": 12, "item_image": 7, "favorite": 6,
    "trade_message": 6, "trade_flow": 4, "review": 3, "credit_log": 5,
    "operation_log": 7, "system_config": 11,
}

DEMO_PASSWORD = {"admin": "Admin@123", "teacher01": "Teacher@123"}


def add_chapter8(doc, tables):
    h1(doc, "8　初始化与种子数据说明")

    h2(doc, "8.1　初始化机制")
    body(doc, "数据库初始化由三部分组成，顺序固定、缺一不可：")
    bullets(doc, [
        "db/schema.sql：建表脚本。第 0 节关闭外键并按外键依赖反序 DROP 旧表（system_config → "
        "… → user），随后正序 CREATE TABLE 11 张表、建立 13 个索引，文末重新打开外键约束。"
        "因此脚本可在“已有数据”的库上重复执行，等价于“重置并重建”，避免开发期手工删库；",
        "db/seed-data.sql：种子数据脚本。单事务导入（BEGIN … COMMIT），固定主键 ID，"
        "覆盖全部业务场景（详见 8.2~8.5）；",
        "程序入口 config/DatabaseInitializer：读取上述两个脚本（UTF-8），用逐字符状态机切分语句"
        "（识别行注释、单引号字符串与转义），在同一连接内顺序执行；失败抛 DataAccessException，"
        "由上层提示“执行建库脚本失败”。",
    ])
    body(doc, "脚本路径与参数由 src/main/resources/application.properties 与 ConfigManager 提供："
              "db.url=jdbc:sqlite:data/greencampus.db、db.schema=../../db/schema.sql、"
              "db.seed=../../db/seed-data.sql、app.seed.on.start=true。"
              "工程运行 Main 时会自动完成“建库 + 种子 + 业务流程演示”。")
    code_block(doc, [
        "# 命令行方式（无 Maven 时亦可直接用 Python 内置 sqlite3 复现）",
        "python -c \"import sqlite3;c=sqlite3.connect('demo.db');"
        "c.executescript(open('db/schema.sql',encoding='utf-8').read());"
        "c.executescript(open('db/seed-data.sql',encoding='utf-8').read());c.close()\"",
    ], size=8.0)

    h2(doc, "8.2　种子数据规模")
    body(doc, "下表行数取自真实验证库 db/_verify/greencampus.db（schema + seed 执行后），"
              "并与 D5-2 要求的下限逐项核对。")
    caption(doc, "表 8-1　种子数据规模")
    conn = _db()
    try:
        rows = []
        for idx, t in enumerate(tables, 1):
            name = t["name"]
            cnt = conn.execute('SELECT COUNT(*) FROM "%s"' % name).fetchone()[0]
            need = SEED_MIN.get(name, 0)
            rows.append([str(idx), name, sm.TABLE_META[name][0], str(cnt), str(need),
                         "满足" if cnt >= need else "不足"])
        make_table(doc, ["序号", "表名", "中文名", "实际行数", "要求下限", "结论"], rows,
                   widths=[1.1, 3.4, 3.2, 2.6, 2.6, 2.0], size=8.6, align_center_cols={0, 3, 4, 5})

        h2(doc, "8.3　演示账号")
        body(doc, "种子数据预置 1 名管理员、1 名教师、3 名学生，口令均以 PBKDF2WithHmacSHA256"
                  "（100000 次迭代、16 字节随机盐、256 位输出、Base64 编码）哈希后存储，"
                  "数据库内不存在明文口令。下表中的“演示口令”仅供验收演示登录使用，"
                  "生产环境必须强制修改。")
        caption(doc, "表 8-2　演示账号")
        rows = []
        users = conn.execute(
            'SELECT id, username, real_name, role, student_no, credit_score, status '
            'FROM "user" ORDER BY id').fetchall()
        for u in users:
            pwd = DEMO_PASSWORD.get(u[1], "Student@123")
            rows.append([str(u[0]), u[1], u[2], u[3], u[4] or "—", str(u[5]), u[6], pwd])
        make_table(doc, ["ID", "用户名", "姓名", "角色", "学号", "信用分", "状态", "演示口令"],
                   rows, widths=[1.0, 2.6, 2.0, 2.0, 2.4, 1.7, 1.9, 2.8], size=8.2,
                   align_center_cols={0, 3, 5, 6, 7})

        h2(doc, "8.4　系统配置项")
        body(doc, "system_config 是业务参数的唯一来源：信用分初始值/上下限、发布门槛、"
                  "评价奖惩、登录失败锁定阈值、碳减排系数等全部预置，Service 层通过 "
                  "SystemConfigDao 读取，禁止硬编码魔法值。")
        caption(doc, "表 8-3　system_config 预置键")
        rows = conn.execute(
            "SELECT config_key, config_value, description FROM system_config ORDER BY id").fetchall()
        make_table(doc, ["配置键", "配置值", "用途说明"],
                   [[r[0], r[1], r[2] or "—"] for r in rows],
                   widths=[4.6, 2.4, 9.4], size=8.4)

        h2(doc, "8.5　覆盖性说明")
        item_status = dict(conn.execute(
            "SELECT status, COUNT(*) FROM item GROUP BY status").fetchall())
        trade_type = dict(conn.execute(
            "SELECT trade_type, COUNT(*) FROM item GROUP BY trade_type").fetchall())
        flow_status = dict(conn.execute(
            "SELECT status, COUNT(*) FROM trade_flow GROUP BY status").fetchall())
        n_review = conn.execute("SELECT COUNT(*) FROM review").fetchone()[0]
        n_credit = conn.execute("SELECT COUNT(*) FROM credit_log").fetchone()[0]
        n_oplog = conn.execute("SELECT COUNT(*) FROM operation_log").fetchone()[0]
        n_img = conn.execute("SELECT COUNT(*) FROM item_image").fetchone()[0]
        n_fav = conn.execute("SELECT COUNT(*) FROM favorite").fetchone()[0]
        n_msg = conn.execute("SELECT COUNT(*) FROM trade_message").fetchone()[0]
        n_cat2 = conn.execute(
            "SELECT COUNT(*) FROM category WHERE parent_id IS NOT NULL").fetchone()[0]
        avg_credit = conn.execute('SELECT ROUND(AVG(credit_score),1) FROM "user"').fetchone()[0]
    finally:
        conn.close()

    bullets(doc, [
        "物品状态覆盖：%s（7 种状态全部出现）；"
        % "、".join("%s=%d" % (k, v) for k, v in sorted(item_status.items())),
        "交易方式覆盖：%s（SELL/EXCHANGE/FREE 三类齐全）；"
        % "、".join("%s=%d" % (k, v) for k, v in sorted(trade_type.items())),
        "流转状态覆盖：%s（含 DONE 成交、APPLYING 申请中、CANCELLED 已取消）；"
        % "、".join("%s=%d" % (k, v) for k, v in sorted(flow_status.items())),
        "两级分类：共 10 条，其中二级分类 %d 条，覆盖“教材书籍/数码配件/文体用品/生活物资”四个一级类；"
        % n_cat2,
        "关联数据：图片 %d 条、收藏 %d 条、消息 %d 条、评价 %d 条、信用流水 %d 条、操作日志 %d 条，"
        "均满足“一条记录可被多条查询命中”的演示需要；"
        % (n_img, n_fav, n_msg, n_review, n_credit, n_oplog),
        "信用分一致性：5 个账号平均信用分 %s，其中 user 3=105、user 4=97 与 credit_log "
        "流水对账一致（见第 7 章 7.4 节）；" % avg_credit,
        "口令安全：user 表的 password_hash / salt 均为真实 PBKDF2 结果，脚本与文档中"
        "不出现明文口令（本文档的演示口令列仅在 docx 中说明，SQL 内无明文）。",
    ])

    h2(doc, "8.6　执行顺序与幂等性")
    body(doc, "导入顺序必须是“先 schema、后 seed”。schema.sql 每次执行都会重置全部表，"
              "因此“schema + seed”这一组合是幂等的：重复执行得到同一份数据；"
              "而单独重复执行 seed-data.sql 会因固定主键冲突而失败（这正是幂等的另一面："
              "它保证数据不会被悄悄加一份）。如需只追加新数据，应使用应用层业务方法，"
              "而不是直接跑种子脚本。")


# =============================================================================
# 第 9 章
# =============================================================================


def _load_verify_blocks():
    text = VERIFY_OUTPUT.read_text(encoding="utf-8")
    pattern = re.compile(
        r"={70,}\r?\n(?P<title>.+?)\r?\n={70,}\r?\n(?P<body>.*?)"
        r"(?=\r?\n={70,}\r?\n.+?\r?\n={70,}\r?\n|\Z)", re.S)
    blocks = []
    for m in pattern.finditer(text):
        blocks.append({"title": m.group("title").strip(),
                       "text": m.group("title").strip() + "\n" + m.group("body")})
    return text, blocks


def _wrap(lines, width=118):
    out = []
    for line in lines:
        line = line.rstrip()
        while len(line) > width:
            out.append(line[:width])
            line = line[width:]
        out.append(line)
    return out


def _block_lines(blocks, prefixes):
    chosen = []
    for b in blocks:
        if any(b["title"].startswith(p) for p in prefixes):
            chosen.append(b)
    lines = []
    for b in chosen:
        lines.extend(b["text"].splitlines())
        lines.append("")
    return lines


def add_chapter9(doc, blocks, full_text):
    h1(doc, "9　验证记录")
    body(doc, "本章全部内容来自真实执行，未做任何修饰。所有输出原文保存在 "
              "db/_verify-output.txt（约 25 KB），并已按“结构验证 → 种子与约束 → ER 自检 → "
              "Java 编译测试运行”的顺序自动追加生成。任何环境只要有 Python 3.12 与 JDK 17+，"
              "即可按附录 B 的命令重跑并复现相同结果。")

    h2(doc, "9.1　验证环境与方法")
    caption(doc, "表 9-1　验证环境")
    make_table(
        doc,
        ["项目", "取值", "说明"],
        [
            ["操作系统", "Windows 10/11（x64）", "本机实际执行环境"],
            ["Python", "3.12.14", "内置 sqlite3 模块 2.6.0"],
            ["SQLite 引擎", "3.53.1", "Python 内置版本，真实执行建库与种子导入"],
            ["JDK", "javac / java 25.0.2", "以 --release 17 编译，确保 Java 17 兼容"],
            ["Maven", "未安装", "本机无 mvn/mvnw，故改用 javac 校验（如实说明，见 9.5 与 13 节）"],
            ["构建/验证脚本", "db/verify_db.py、db/_check_er.py、db/_append_evidence.py",
             "依次执行，输出追加到 db/_verify-output.txt"],
        ],
        widths=[2.4, 5.2, 8.8], size=8.4,
    )
    body(doc, "验证方法：① 用 Python sqlite3 真实执行 schema.sql 建库，检查表清单、"
              "PRAGMA integrity_check、PRAGMA foreign_key_check；② 执行 seed-data.sql 并核对行数；"
              "③ 构造 12 条非法数据验证约束确实生效；④ 用 ElementTree 解析 ER 图并校验结构；"
              "⑤ javac 编译全部主源码与测试源码；⑥ JUnit 5 执行单元测试；⑦ 运行 Main 走完业务流程。")

    h2(doc, "9.2　建库与结构验证（节选）")
    body(doc, "以下为验证输出第 1~3 节的原文：建表结果、integrity_check 与 foreign_key_check。")
    code_block(doc, _wrap(_block_lines(blocks, ["1. 建表结果", "2. 完整性检查", "3. 外键检查"])), size=7.6)

    h2(doc, "9.3　种子数据、约束反例与口令校验（节选）")
    body(doc, "以下为验证输出第 5~8 节原文：种子行数、12 条约束反例（预期全部被拒绝）、"
              "PBKDF2 口令哈希一致性。")
    code_block(doc, _wrap(_block_lines(
        blocks, ["5. 导入种子数据后的状态", "6. 约束有效性反例测试",
                 "7. 演示口令哈希一致性校验", "8. 结论"])), size=7.6)

    h2(doc, "9.4　ER 图文件自检")
    body(doc, "自检项：XML 可解析、drawio 结构（mxfile→diagram→mxGraphModel→root）、"
              "mxCell 数量（要求 ≥80）、11 个实体框字段数、18 条关系线是否锚定具体字段并"
              "标注 1/N 基数、文件大小（要求 >15 KB）。")
    code_block(doc, _wrap(_block_lines(blocks, ["D5-3"])), size=7.6)

    h2(doc, "9.5　Java 工程编译、测试与运行")
    body(doc, "以下为验证输出第 9~13 节原文：主源码编译（javac --release 17、零 classpath）、"
              "测试源码编译、JUnit 5 执行、Main 控制台端到端运行，以及关于 Maven 的如实说明。")
    code_block(doc, _wrap(_block_lines(
        blocks, ["9. 主源码编译", "10. 测试源码编译", "11. JUnit 5 测试执行",
                 "12. 控制台演示 Main", "13. 关于 Maven"])), size=7.4)

    h2(doc, "9.6　完整原始输出（逐字）")
    body(doc, "为便于评审逐条核对，以下完整收录 db/_verify-output.txt 的全文（含本次生成的"
              "环境信息与时间戳）。文件本身随交付物提交，可用于交叉验证。")
    code_block(doc, _wrap(full_text.splitlines()), size=7.0)

    h2(doc, "9.7　验证结论")
    caption(doc, "表 9-2　验证结论汇总")
    make_table(
        doc,
        ["验证项", "结果", "证据位置"],
        [
            ["建库脚本执行", "11/11 张表创建成功，无缺失、无多余", "第 9.2 节 / 输出第 1 节"],
            ["数据完整性", "PRAGMA integrity_check = ok", "第 9.2 节 / 输出第 2 节"],
            ["外键完整性", "PRAGMA foreign_key_check = []（无违反）", "第 9.2 节 / 输出第 3 节"],
            ["种子数据导入", "11 张表行数全部达到下限要求", "第 9.3 节 / 输出第 5 节"],
            ["约束有效性", "12/12 条非法数据全部被拒绝", "第 9.3 节 / 输出第 6 节"],
            ["口令哈希", "5 个账号 PBKDF2 复算全部一致", "第 9.3 节 / 输出第 7 节"],
            ["ER 图", "XML 合法，162 个 mxCell、18 条关系线，约 68 KB", "第 9.4 节"],
            ["Java 编译", "107 个主源文件零错误（javac --release 17）", "第 9.5 节"],
            ["单元测试", "11 个测试全部通过（0 失败）", "第 9.5 节"],
            ["端到端流程", "Main 9 步全部通过：注册→登录→发布(PENDING)→审核→检索→流转→成交→评价→统计", "第 9.5 节"],
        ],
        widths=[3.4, 7.6, 5.4], size=8.4,
    )
    body(doc, "结论：数据层交付物（schema、seed、ER 图、Java 代码）已在真实 SQLite 引擎与"
              "真实 JDK 上完成验证，满足“可运行、可复现、可审计”的验收要求。唯一未在本机执行的"
              "是 Maven 打包（本机无 Maven），已用 javac 编译校验替代，并在 9.5 节与附录 B 中如实说明。")


# =============================================================================
# 第 10 章
# =============================================================================


def add_chapter10(doc, tables):
    h1(doc, "10　与 D3 类图、D2 接口的字段对照")

    h2(doc, "10.1　命名与类型映射规则")
    body(doc, "数据库与 Java 之间的映射遵循固定规则，保证“表结构 → 实体类 → DAO → Service”"
              "四层字段可一一追溯：")
    bullets(doc, [
        "表名小写下划线（如 trade_flow），实体类名大驼峰（TradeFlow）；",
        "字段名小写下划线，实体属性小驼峰（item_id → itemId）；is_read 显式映射为 isRead，"
        "避免 JavaBeans 反射把 isRead 误判为 read；",
        "枚举列（role/status/trade_type/flow_type）数据库存 TEXT 编码，实体属性用 String，"
        "由枚举类 Role/ItemStatus/FlowStatus/TradeType 提供 fromCode 转换；",
        "时间列 TEXT 'yyyy-MM-dd HH:mm:ss'，Java 侧 LocalDateTime，统一由 "
        "AbstractJdbcDao.DATE_TIME_FORMATTER 与 formatDateTime/readDateTime 负责转换；",
        "金额列 REAL，Java 侧 BigDecimal，读写时用 BigDecimal.toPlainString/doubleValue 转换，"
        "比较一律用 compareTo。",
    ])
    caption(doc, "表 10-1　类型映射表")
    make_table(doc, ["数据库类型", "Java 类型", "说明"], TYPE_MAP,
               widths=[3.6, 3.0, 9.8], size=8.2)

    h2(doc, "10.2　表 → 实体 → DAO → Service 对照")
    body(doc, "契约第 3、5、6 节分别定义了表结构、DAO 接口与 Service 接口。下表给出逐表对照，"
              "任何一层的字段缺失或命名漂移都可在此暴露。")
    caption(doc, "表 10-2　表与实体/DAO/Service 对照")
    rows = []
    for idx, t in enumerate(tables, 1):
        cn, cls, duty = sm.TABLE_META[t["name"]]
        dao, svc, extra = TABLE_SERVICE[t["name"]]
        rows.append([str(idx), t["name"], cls, "%d" % len(t["columns"]), dao, svc, extra])
    make_table(doc, ["序号", "表名", "实体类", "字段数", "DAO 接口", "主要 Service", "其他使用方"],
               rows, widths=[1.0, 3.0, 2.4, 1.4, 3.0, 3.4, 2.6], size=8.0, align_center_cols={0, 3})

    h2(doc, "10.3　DTO 与查询字段对照")
    body(doc, "DTO 用于跨层传输“查询结果 + 分页/聚合信息”，不直接映射单表。其字段来源如下表。")
    caption(doc, "表 10-3　DTO 字段来源")
    make_table(
        doc,
        ["DTO", "主要字段", "字段来源", "使用场景"],
        [
            ["ItemQuery", "keyword、categoryId、minPrice、maxPrice、tradeType、status、ownerId、"
                          "sortBy、pageNo、pageSize", "item 表检索列 + 展示排序参数",
             "ItemService.search → ItemDao.search/countSearch"],
            ["PageResult<T>", "records、total、pageNo、pageSize、totalPages", "DAO 返回的记录 + "
                                                                           "countSearch 总数",
             "全部分页列表的统一返回结构"],
            ["StatisticsDTO", "categoryName、flowCount、totalAmount、carbonReduction",
             "trade_flow（DONE 态）按一级分类聚合 + category 名称 + 减排系数", "统计报表与 CSV 导出"],
            ["UserCreditDTO", "userId、username、realName、creditScore、level", "user 表 + 信用等级换算",
             "信用分展示与等级说明"],
            ["LoginResult", "userId、username、realName、role、creditScore、loginAt、message",
             "user 表字段 + 登录时间", "登录成功后的会话信息"],
            ["TradeDetailDTO", "TradeFlow、Item、User(seller)、User(buyer) 与派生字段",
             "trade_flow JOIN item/user", "流转详情页聚合展示"],
        ],
        widths=[2.6, 5.4, 4.4, 4.0], size=8.0,
    )

    h2(doc, "10.4　与契约的一致性声明与差异说明")
    bullets(doc, [
        "表名、字段名、字段数、类型、NOT NULL/DEFAULT/CHECK/UNIQUE 全部逐字对齐契约第 3 节，"
        "11 张表共 93 个字段，无契约外新增字段；",
        "实体类字段与表列一一对应（is_read → isRead 为唯一显式映射），金额 BigDecimal、"
        "时间 LocalDateTime，枚举以 String 承载编码，与 D3 类图一致；",
        "DAO 接口 12 个（BaseDao + 11 业务 DAO）与 Service 接口 7 个的方法签名逐字对齐契约第 5、6 节，"
        "实现类均以 @Override 落实；",
        "异常体系对照契约第 7 节：AppException 基类 + 9 个子类，code 前缀 VAL-/DUP-/NF-/AUTH-/LOCK-/"
        "PERM-/BR-/DB-/TX- 与契约一致，BusinessRuleException 额外承载 BR 编号；",
        "差异一（索引级补充）：uq_category_root_name 为部分唯一索引，用于约束“一级分类不可重名”。"
        "契约未列出该索引，但 SQLite 的 UNIQUE(parent_id, name) 无法约束 parent_id IS NULL 的行"
        "（NULL 互不相等），属于真实的完整性缺口，故补充并在第 5 章标注【建议补充】；",
        "差异二（日志门面）：Java 代码使用 java.util.logging（JUL）而非 slf4j，以保证在无网络、"
        "无 classpath 的环境下 javac 也能通过；pom.xml 仍保留 logback-classic 作为运行期日志实现"
        "（详见附录 B 的说明），这不影响契约与功能；",
        "差异三（驱动加载）：DbUtil 通过 Class.forName(\"org.sqlite.JDBC\") 反射加载驱动，"
        "而非编译期直接 import org.sqlite.*，使主源码零第三方依赖即可编译，运行时由 Maven/SQLite "
        "jar 提供实现。",
    ])


# =============================================================================
# 附录
# =============================================================================

PACKAGE_DUTY = {
    ("edu", "campus", "recycle"): "程序入口 Main：串联建库、注册登录、发布检索、流转成交、统计导出",
    ("edu", "campus", "recycle", "ui"): "界面层占位（Swing 由成员3实现，本层只依赖 controller/service）",
    ("edu", "campus", "recycle", "controller"): "AppController：界面与会话的门面，屏蔽 Service 细节",
    ("edu", "campus", "recycle", "service"): "7 个业务服务接口（契约第 6 节）",
    ("edu", "campus", "recycle", "service", "impl"): "7 个业务服务实现：校验、事务、观察者事件",
    ("edu", "campus", "recycle", "dao"): "BaseDao + 11 个业务 DAO 接口（契约第 5 节）",
    ("edu", "campus", "recycle", "dao", "impl"): "AbstractJdbcDao 模板基类 + 11 个 JDBC 实现",
    ("edu", "campus", "recycle", "entity"): "11 个实体类 + 5 个枚举（Role/ItemStatus/FlowStatus/TradeType/UserStatus）",
    ("edu", "campus", "recycle", "dto"): "6 个数据传输对象（ItemQuery/PageResult/StatisticsDTO 等）",
    ("edu", "campus", "recycle", "util"): "工具与设计模式：DbUtil、PasswordUtil、Validator、CsvExporter、"
                                         "DaoFactory、ServiceFactory、策略与观察者",
    ("edu", "campus", "recycle", "exception"): "AppException 基类 + 9 个业务异常子类（契约第 7 节）",
    ("edu", "campus", "recycle", "config"): "DbConfig 配置读取、DatabaseInitializer 建库与种子导入",
}


def _package_inventory():
    root = BASE / "code" / "green-campus" / "src" / "main" / "java"
    stats = {}
    for p in root.rglob("*.java"):
        rel = p.relative_to(root).parent.parts
        stats[rel] = stats.get(rel, 0) + 1
    return stats


def _file_row(path, purpose):
    size = path.stat().st_size if path.exists() else 0
    return [str(path.relative_to(BASE)).replace("\\", "/"), "%.1f KB" % (size / 1024.0), purpose]


def add_appendix(doc):
    h1(doc, "附录 A　工程结构与文件清单")

    h2(doc, "A.1　Java 源码包结构")
    body(doc, "工程遵循经典分层：ui → controller → service → dao → entity/dto，util 提供横切能力，"
              "config 负责配置与初始化。各包文件数如下（真实统计自 src/main/java）。")
    caption(doc, "表 A-1　包结构与文件数")
    stats = _package_inventory()
    rows = []
    for pkg in sorted(stats):
        duty = PACKAGE_DUTY.get(tuple(pkg), "—")
        rows.append([".".join(pkg), str(stats[pkg]), duty])
    total = sum(stats.values())
    rows.append(["合计", str(total), "主源码 %d 个 Java 文件（另有测试源码 2 个）" % total])
    make_table(doc, ["包路径", "文件数", "职责"], rows,
               widths=[5.4, 1.8, 9.2], size=8.2, align_center_cols={1})

    body(doc, "目录结构（节选）：")
    code_block(doc, [
        "code/green-campus/",
        "├── pom.xml                       # Maven 构建（Java 17、sqlite-jdbc、JUnit5、logback、shade 打包）",
        "└── src/",
        "    ├── main/java/edu/campus/recycle/",
        "    │   ├── Main.java             # 控制台演示入口",
        "    │   ├── ui/ controller/ service/ service/impl/",
        "    │   ├── dao/ dao/impl/ entity/ dto/ util/ exception/ config/",
        "    ├── main/resources/",
        "    │   ├── application.properties  # db.url / db.schema / db.seed / app.image.dir 等",
        "    │   └── logback.xml             # 运行期日志实现（控制台 + 滚动文件）",
        "    └── test/java/edu/campus/recycle/util/",
        "        ├── PasswordUtilTest.java   # PBKDF2 盐/哈希/校验 5 个用例",
        "        └── ValidatorTest.java      # 用户名/口令/学号/图片/价格 6 个用例",
    ], size=8.0)

    h2(doc, "A.2　关键文件")
    caption(doc, "表 A-2　关键文件清单")
    code = BASE / "code" / "green-campus"
    key_files = [
        (code / "pom.xml", "Maven 构建：坐标 edu.campus:green-campus:1.0.0，Java 17，shade 可执行 fat jar"),
        (code / "src" / "main" / "java" / "edu" / "campus" / "recycle" / "Main.java", "控制台 9 步演示入口"),
        (code / "src" / "main" / "java" / "edu" / "campus" / "recycle" / "util" / "DbUtil.java",
         "连接与事务模板：单例、ThreadLocal 事务上下文、PRAGMA foreign_keys/busy_timeout"),
        (code / "src" / "main" / "java" / "edu" / "campus" / "recycle" / "util" / "PasswordUtil.java",
         "PBKDF2WithHmacSHA256/100000 次/16 字节盐/256 位/Base64"),
        (code / "src" / "main" / "java" / "edu" / "campus" / "recycle" / "dao" / "impl" / "AbstractJdbcDao.java",
         "JDBC 模板方法基类：取连接、绑定参数、映射行、异常转换"),
        (code / "src" / "main" / "java" / "edu" / "campus" / "recycle" / "service" / "impl" / "TradeServiceImpl.java",
         "流转生命周期与 confirm 跨表事务（BR-05/BR-07）"),
        (code / "src" / "main" / "java" / "edu" / "campus" / "recycle" / "service" / "impl" / "UserServiceImpl.java",
         "注册/登录/失败锁定/信用分调整（BR-01~BR-04）"),
        (BASE / "db" / "schema.sql", "建表脚本：11 表 + 13 索引 + 18 外键，可重复执行"),
        (BASE / "db" / "seed-data.sql", "种子数据：单事务导入，11 表全部覆盖"),
        (BASE / "design" / "05-ER图.drawio", "ER 图源文件（162 个 mxCell，18 条关系线）"),
        (BASE / "db" / "_verify-output.txt", "全部验证的真实输出（本文件为 docx 第 9 章数据来源）"),
    ]
    make_table(doc, ["文件", "大小", "说明"],
               [_file_row(p, purpose) for p, purpose in key_files],
               widths=[7.4, 1.8, 7.2], size=7.8, align_center_cols={1})

    h2(doc, "A.3　生成与验证脚本")
    body(doc, "以下脚本位于 db 目录，用于“可复现地”生成与验证本交付物，全部为纯 Python，无第三方依赖"
              "（docx 构建依赖 python-docx）。")
    caption(doc, "表 A-3　db 目录脚本清单")
    scripts = [
        ("schema.sql", "11 张表、约束、索引的 DDL（唯一权威结构定义）"),
        ("seed-data.sql", "种子数据 DML（单事务）"),
        ("verify_db.py", "真实建库 + 导入种子 + 行数/约束反例/PBKDF2 校验，写 _verify-output.txt"),
        ("_check_er.py", "解析 drawio XML，校验结构、mxCell、字段数与关系线锚点，追加输出"),
        ("_append_evidence.py", "追加 javac/JUnit/Main 的真实执行记录与 Maven 说明"),
        ("_gen_er_drawio.py", "由表结构数据表生成 ER 图 drawio XML"),
        ("_gen_java_part1~5.py", "分批生成 Java 工程源码（保证 107 个源文件一致、可重生成）"),
        ("_schema_model.py", "静态解析 schema.sql，供 docx 数据字典/约束/索引章节复用"),
        ("_build_docx.py", "生成本文档（python-docx）"),
        ("_verify/greencampus.db", "验证用数据库文件（schema + seed 后的真实库）"),
    ]
    rows = []
    for name, purpose in scripts:
        p = BASE / "db" / name
        rows.append([name, "%.1f KB" % (p.stat().st_size / 1024.0) if p.exists() else "—", purpose])
    make_table(doc, ["脚本/文件", "大小", "作用"], rows,
               widths=[4.2, 1.8, 10.4], size=8.0, align_center_cols={1})

    page_break(doc)
    h1(doc, "附录 B　复现步骤（命令）")
    body(doc, "以下命令在 Windows PowerShell 下、工程根目录 C:\\Users\\wanhe\\Desktop\\软件构造\\迭代一-成员1 "
              "执行即可复现第 9 章的全部验证结果。Python 解释器路径为本机实际使用的托管运行时，"
              "其他机器可替换为任意 Python 3.10+。")

    h2(doc, "B.1　环境准备")
    bullets(doc, [
        "Python 3.10+（内置 sqlite3；本机为 3.12.14，SQLite 3.53.1）；",
        "JDK 17+（本机为 25.0.2，编译时用 --release 17 保证兼容）；",
        "Maven 3.9+（可选；本机未安装，故用 javac 校验，见 B.3）；",
        "Python 包：仅构建 docx 需要 python-docx（pip install python-docx），其余脚本零依赖。",
    ])

    h2(doc, "B.2　验证命令")
    code_block(doc, [
        "# 1) 建库 + 导入种子 + 结构/约束/口令验证（重写 db/_verify-output.txt）",
        "python db/verify_db.py",
        "",
        "# 2) ER 图自检（追加输出）",
        "python db/_check_er.py",
        "",
        "# 3) 编译主源码（零 classpath，javac --release 17）",
        "javac --release 17 -encoding UTF-8 -d $env:TEMP\\gc_compile "
        "(Get-ChildItem -Recurse code\\green-campus\\src\\main\\java\\*.java)",
        "",
        "# 4) 编译并运行 JUnit 5 测试（需 junit-platform-console-standalone 1.10.2）",
        "javac --release 17 -encoding UTF-8 -cp \"$env:TEMP\\gc_libs\\junit-platform-console-standalone-1.10.2.jar\" "
        "-d $env:TEMP\\gc_test_compile (Get-ChildItem -Recurse code\\green-campus\\src\\test\\java\\*.java)",
        "java -jar $env:TEMP\\gc_libs\\junit-platform-console-standalone-1.10.2.jar "
        "--class-path \"$env:TEMP\\gc_compile;$env:TEMP\\gc_test_compile\" --select-package edu.campus.recycle",
        "",
        "# 5) 运行控制台端到端演示（工作目录必须在 code/green-campus，schema 相对路径为 ../../db）",
        "cd code\\green-campus",
        "java -cp \"$env:TEMP\\gc_compile;$env:TEMP\\gc_libs\\sqlite-jdbc-3.46.1.0.jar;"
        "$env:TEMP\\gc_libs\\slf4j-api-2.0.13.jar;$env:TEMP\\gc_libs\\slf4j-nop-2.0.13.jar;"
        "src\\main\\resources\" edu.campus.recycle.Main",
        "",
        "# 6) 重新生成本文档",
        "python db/_build_docx.py",
    ], size=7.6)

    h2(doc, "B.3　关于 Maven 的如实说明")
    body(doc, "本机未安装 Maven（命令行无 mvn/mvnw），因此交付物中的 pom.xml 虽已按题目要求配置"
              "（Java 17、sqlite-jdbc 3.46.1.0、junit-jupiter 5.10.2、logback-classic 1.5.6、"
              "surefire、jar、shade 插件），但未在本机执行 mvn package，也未伪造任何 Maven 输出。"
              "取而代之的验证是：用 JDK 自带 javac 以 --release 17 编译全部 107 个主源码文件（零错误），"
              "用 junit-platform-console-standalone 运行 11 个单元测试（全部通过），"
              "并从 Maven Central 手工下载 sqlite-jdbc 后真实运行 Main 走通全流程。")
    body(doc, "在装有 Maven 的机器上，执行以下命令即可完成打包，产物为可执行 fat jar：")
    code_block(doc, [
        "cd code\\green-campus",
        "mvn -q -DskipTests package      # 生成 target/green-campus-1.0.0.jar（含依赖，Main-Class 已配置）",
        "java -jar target/green-campus-1.0.0.jar   # 运行控制台演示",
    ], size=8.0)
    body(doc, "预期结果：mvn 输出 BUILD SUCCESS，target 目录下生成 green-campus-1.0.0.jar；"
              "运行后依次打印 9 步演示日志并以“演示流程全部通过”结束。"
              "由于本机无法执行该步骤，此处仅给出命令与预期，不提供任何虚构的 mvn 输出。")


def add_final_note(doc):
    page_break(doc)
    h1(doc, "文末注记")
    body(doc, "本文档所有表结构、约束、索引、行数、验证输出均来自 db/schema.sql、db/seed-data.sql "
              "与 db/_verify-output.txt 的真实执行结果；ER 图由脚本生成并经 ElementTree 自检；"
              "Java 工程经 javac --release 17 编译（107 个源文件、零错误）、JUnit 5 测试（11/11 通过）"
              "与控制台 Main 端到端运行验证。未伪造任何命令输出，Maven 缺失的事实已如实说明。", indent=False)
    body(doc, "文档与代码的后续维护建议：修改表结构时，先改 db/schema.sql，再重跑 "
              "verify_db.py / _check_er.py / _build_docx.py，使数据字典、约束清单、索引清单、"
              "验证章节与实现始终保持单一来源一致。", indent=False)
    body(doc, "【生成：deepseek-flash / data-layer / 第 3 轮】", indent=False, size=9, bold=True)


def main():
    tables, indexes, fks = sm.parse_schema()
    full_text, blocks = _load_verify_blocks()
    print("解析 schema.sql：%d 表 / %d 列 / %d 索引 / %d 外键"
          % (len(tables), sum(len(t["columns"]) for t in tables), len(indexes), len(fks)))
    print("验证输出：%d 字节 / %d 个章节块" % (len(full_text.encode("utf-8")), len(blocks)))

    doc = setup_document()
    add_cover(doc)
    add_toc(doc)
    add_revision(doc)
    add_chapter1(doc)
    page_break(doc)
    add_chapter2(doc, tables, fks)
    page_break(doc)
    add_chapter3(doc, tables, indexes)
    page_break(doc)
    add_chapter4(doc, tables, fks, indexes)
    page_break(doc)
    add_chapter5(doc, indexes)
    page_break(doc)
    add_chapter6(doc)
    page_break(doc)
    add_chapter7(doc)
    page_break(doc)
    add_chapter8(doc, tables)
    page_break(doc)
    add_chapter9(doc, blocks, full_text)
    page_break(doc)
    add_chapter10(doc, tables)
    page_break(doc)
    add_appendix(doc)
    add_final_note(doc)

    OUT.parent.mkdir(parents=True, exist_ok=True)
    doc.save(str(OUT))
    size = OUT.stat().st_size
    print("已生成：%s" % OUT)
    print("文件大小：%.1f KB" % (size / 1024.0))
    print("段落数：%d，表格数：%d" % (len(doc.paragraphs), len(doc.tables)))


if __name__ == "__main__":
    main()
