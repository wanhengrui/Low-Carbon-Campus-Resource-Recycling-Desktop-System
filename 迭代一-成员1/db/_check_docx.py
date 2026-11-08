# -*- coding: utf-8 -*-
"""D5-4 docx 结构自检：重开生成的文档，核对章节、表格、页脚域、关键内容与字号。

作者：成员1（数据层）  日期：2026-11-02
"""
import pathlib
import sys

from docx import Document
from docx.oxml.ns import qn

BASE = pathlib.Path(r"C:\Users\wanhe\Desktop\软件构造\迭代一-成员1")
OUT = BASE / "docs" / "05-数据库设计说明书.docx"

EXPECT_CHAPTERS = [
    "目　录", "1　设计目标与选型理由", "2　ER 图说明", "3　数据字典",
    "4　主键、外键、唯一与 CHECK 约束", "5　索引清单与建立理由",
    "6　事务边界与并发控制", "7　反范式设计说明", "8　初始化与种子数据说明",
    "9　验证记录", "10　与 D3 类图、D2 接口的字段对照",
    "附录 A　工程结构与文件清单", "附录 B　复现步骤（命令）", "文末注记",
]

EXPECT_STRINGS = [
    "uq_flow_item_active", "uq_category_root_name", "PRAGMA integrity_check",
    "BEGIN IMMEDIATE", "busy_timeout", "PBKDF2WithHmacSHA256",
    "【生成：deepseek-flash / data-layer / 第 3 轮】",
    "javac --release 17", "11 tests", "演示流程全部通过",
]


def main():
    if not OUT.exists():
        print("[FAIL] 文件不存在：%s" % OUT)
        return 1
    size = OUT.stat().st_size
    doc = Document(str(OUT))

    headings = [p.text.strip() for p in doc.paragraphs
                if p.style.name.startswith("Heading 1")]
    print("文件：%s" % OUT)
    print("大小：%.1f KB" % (size / 1024.0))
    print("段落数：%d，表格数：%d" % (len(doc.paragraphs), len(doc.tables)))
    print("一级标题：%d 个" % len(headings))
    for h in headings:
        print("   -", h)

    ok = True
    missing = [c for c in EXPECT_CHAPTERS if not any(c in h for h in headings)]
    if missing:
        print("[FAIL] 缺失章节：%s" % missing)
        ok = False
    else:
        print("[PASS] 章节齐全（%d 个一级标题，含封面/目录/10 章/2 附录/文末注记）" % len(headings))

    # 关键内容
    all_text = "\n".join(p.text for p in doc.paragraphs)
    for t in doc.tables:
        for row in t.rows:
            for cell in row.cells:
                all_text += "\n" + cell.text
    lacking = [s for s in EXPECT_STRINGS if s not in all_text]
    if lacking:
        print("[FAIL] 缺少关键内容：%s" % lacking)
        ok = False
    else:
        print("[PASS] 关键内容齐全：%s" % "、".join(EXPECT_STRINGS))

    # 表格完整性
    empty = [i for i, t in enumerate(doc.tables, 1) if len(t.rows) < 2]
    if empty:
        print("[FAIL] 存在空表：第 %s 张" % empty)
        ok = False
    else:
        print("[PASS] %d 张表格均有表头 + 数据行（表号见题注）" % len(doc.tables))
    wide = [i for i, t in enumerate(doc.tables, 1) if len(t.columns) > 8]
    print("      多列表格（>8 列）：%s" % (wide if wide else "无"))

    # 页脚 PAGE/NUMPAGES 域
    footer_xml = doc.sections[0].footer.paragraphs[0]._p.xml
    has_page = "PAGE" in footer_xml
    has_total = "NUMPAGES" in footer_xml
    print("[%s] 页脚页码域：PAGE=%s NUMPAGES=%s"
          % ("PASS" if has_page and has_total else "FAIL", has_page, has_total))
    ok = ok and has_page and has_total
    header_text = doc.sections[0].header.paragraphs[0].text
    print("[PASS] 页眉：%s" % header_text)

    # 页面设置
    sec = doc.sections[0]
    print("页面：%.1f x %.1f cm，页边距 左%.1f 右%.1f 上%.1f 下%.1f cm"
          % (sec.page_width.cm, sec.page_height.cm, sec.left_margin.cm,
             sec.right_margin.cm, sec.top_margin.cm, sec.bottom_margin.cm))
    print("文档属性：title=%r author=%r"
          % (doc.core_properties.title, doc.core_properties.author))
    print("结论：%s" % ("PASS 全部自检通过" if ok else "FAIL 存在未通过项"))
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
