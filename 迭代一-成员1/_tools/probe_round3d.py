# -*- coding: utf-8 -*-
"""第 3 轮收尾核查（Lead）第 2 批：细节上下文定位。"""
import re, sys
from docx import Document

BASE = r"C:\Users\wanhe\Desktop\软件构造\迭代一-成员1"
sys.stdout.reconfigure(encoding="utf-8", errors="replace")


def doc_text(path):
    d = Document(path)
    parts = [p.text for p in d.paragraphs]
    for t in d.tables:
        for row in t.rows:
            for c in row.cells:
                parts.append("[T] " + c.text)
    return parts


def show(tag, parts, kw, width=110, limit=4):
    print("\n---- %s :: %s ----" % (tag, kw))
    n = 0
    for p in parts:
        if kw in p:
            s = p.replace("\n", " ")
            idx = s.find(kw)
            print("  ...%s..." % s[max(0, idx - width // 2): idx + width])
            n += 1
            if n >= limit:
                break
    if n == 0:
        print("  （无）")


p1 = doc_text(BASE + r"\docs\01-需求规格说明书.docx")
p2 = doc_text(BASE + r"\docs\02-模块化设计与接口规范.docx")
p5 = doc_text(BASE + r"\docs\05-数据库设计说明书.docx")
p6 = doc_text(BASE + r"\docs\06-小组分工与两周迭代计划.docx")

show("D1", p1, "DUP-041")
show("D1", p1, "DB-001")
show("D1", p1, "PERM-002")
show("D1", p1, "VAL-004")
show("D1", p1, "updateCredit")
show("D2", p2, "92")
show("D2", p2, "时序图")
show("D6", p6, "ER")
show("D6", p6, "实体关系")
show("D6", p6, "drawio")
print("\n---- 计数 ----")
for tag, parts, kws in (("D1", p1, ["updateCredit", "2 个参数", "delta", "flowId", "reason"]),
                        ("D2", p2, ["updateCredit", "delta", "flowId", "reason"]),
                        ("D6", p6, ["drawio", "05-ER", "design\\05", "design/05"])):
    print(tag, {k: sum(p.count(k) for p in parts) for k in kws})
