# -*- coding: utf-8 -*-
"""D6 定点修补（Lead 最终一致性修改）：
1) 交付物唯一口径段：D5 补 design/05-ER图.drawio，D7 补 部署说明.md 路径
2) 表内成员1 数据层产出补 ER 图
保持原 run 格式：改写首个 run 文本、清空其余 run。
"""
import sys, copy
from docx import Document

BASE = r"C:\Users\wanhe\Desktop\软件构造\迭代一-成员1"
PATH = BASE + r"\docs\06-小组分工与两周迭代计划.docx"
sys.stdout.reconfigure(encoding="utf-8", errors="replace")

doc = Document(PATH)
REPL = [
    ("db/seed-data.sql；D6", "db/seed-data.sql + design/05-ER图.drawio；D6"),
    ("D7 = 部署说明 + Maven 骨架（code/pom.xml、start.bat）",
     "D7 = 部署说明（code/green-campus/部署说明.md）+ Maven 骨架（code/pom.xml、start.bat）"),
    ("docs/05-数据库设计说明书.docx（D5）、db/schema.sql、db/seed-data.sql",
     "docs/05-数据库设计说明书.docx（D5）、design/05-ER图.drawio、db/schema.sql、db/seed-data.sql"),
]
hits = []


def rewrite(par, new_text, where):
    runs = par.runs
    if not runs:
        par.text = new_text
        hits.append(where + "（无 run，整段写入）")
        return
    runs[0].text = new_text
    for r in runs[1:]:
        r.text = ""
    hits.append(where)


for i, par in enumerate(doc.paragraphs):
    t = par.text
    for old, new in REPL:
        if old in t:
            rewrite(par, t.replace(old, new), "P%d" % i)

for ti, tab in enumerate(doc.tables):
    for ri, row in enumerate(tab.rows):
        for ci, cell in enumerate(row.cells):
            for pi, par in enumerate(cell.paragraphs):
                t = par.text
                for old, new in REPL:
                    if old in t:
                        rewrite(par, t.replace(old, new), "T%d/R%d/C%d/P%d" % (ti, ri, ci, pi))

if hits:
    doc.save(PATH)
print("hits:", len(hits))
for h in hits:
    print("  ", h)
