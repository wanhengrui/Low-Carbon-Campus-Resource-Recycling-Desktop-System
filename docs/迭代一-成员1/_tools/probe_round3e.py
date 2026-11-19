# -*- coding: utf-8 -*-
"""D1 错误码总表逐行导出 + D6 交付物清单段落定位。"""
import sys
from docx import Document

BASE = r"C:\Users\wanhe\Desktop\软件构造\迭代一-成员1"
sys.stdout.reconfigure(encoding="utf-8", errors="replace")

d1 = Document(BASE + r"\docs\01-需求规格说明书.docx")
for i, t in enumerate(d1.tables):
    txt = "\n".join(c.text for r in t.rows for c in r.cells)
    if "DB-101" in txt:
        print("D1 错误码总表 = 表#%d，行数=%d" % (i, len(t.rows)))
        for r in t.rows:
            cells = [c.text.strip().replace("\n", " ") for c in r.cells]
            print("  | " + " | ".join(cells))
        break

d6 = Document(BASE + r"\docs\06-小组分工与两周迭代计划.docx")
print("\n==== D6 含 D5 定义/交付物的段落 ====")
for p in d6.paragraphs:
    if "D5" in p.text and ("schema" in p.text or "数据库" in p.text):
        print("  [P] " + p.text.strip()[:400])
print("\n==== D6 含 D5 的表格行 ====")
for ti, t in enumerate(d6.tables):
    for r in t.rows:
        cells = [c.text.strip().replace("\n", " ") for c in r.cells]
        joined = " | ".join(cells)
        if "D5" in joined and ("schema" in joined or "ER" in joined or "数据库" in joined):
            print("  [T%d] %s" % (ti, joined[:400]))
