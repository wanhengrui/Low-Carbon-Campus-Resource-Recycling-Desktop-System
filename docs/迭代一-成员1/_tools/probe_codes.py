# -*- coding: utf-8 -*-
"""Enumerate error-code tokens in D1 / D2 / schema comments / code."""
import re, os, glob, collections

BASE = r"C:\Users\wanhe\Desktop\软件构造\迭代一-成员1"
DOCS = os.path.join(BASE, "docs")
OUT = os.path.join(BASE, "_tools", "round3_codes.txt")
from docx import Document

buf = []
def w(*a): buf.append(" ".join(str(x) for x in a))

def all_text(doc):
    parts = [p.text for p in doc.paragraphs]
    for t in doc.tables:
        for r in t.rows:
            for c in r.cells:
                parts.append(c.text)
    return "\n".join(parts)

PAT = re.compile(r"\b(?:VAL|DUP|NF|PERM|BR|DB|TX|LOCK|AUTH)-\d{2,3}\b")

d1 = Document(os.path.join(DOCS, "01-需求规格说明书.docx"))
d2 = Document(os.path.join(DOCS, "02-模块化设计与接口规范.docx"))
d5 = Document(os.path.join(DOCS, "05-数据库设计说明书.docx"))

for name, doc in (("D1", d1), ("D2", d2), ("D5", d5)):
    txt = all_text(doc)
    c = collections.Counter(PAT.findall(txt))
    w("=" * 20, name, "distinct", len(c))
    for k, v in sorted(c.items()):
        w(f"   {k} x{v}")
    byprefix = collections.defaultdict(set)
    for k in c:
        byprefix[k.split("-")[0]].add(k)
    w("   prefixes:", {k: len(v) for k, v in byprefix.items()})

# D1 table 56 (错误码清单) locate by header containing 码
for i, t in enumerate(d1.tables):
    head = " ".join(c.text for c in t.rows[0].cells)
    if "码" in head and len(t.rows) > 4:
        w("D1 candidate table", i, "head:", head[:120], "rows", len(t.rows))
        if i in (55, 56):
            for r in t.rows:
                w("    ", " | ".join(c.text.strip()[:60] for c in r.cells))

open(OUT, "w", encoding="utf-8").write("\n".join(buf))
print("written", OUT, len(buf))
