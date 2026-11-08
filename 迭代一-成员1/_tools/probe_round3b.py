# -*- coding: utf-8 -*-
"""Round-3 probe #2: dump exact contexts needed for rulings."""
import re, os, glob

BASE = r"C:\Users\wanhe\Desktop\软件构造\迭代一-成员1"
DOCS = os.path.join(BASE, "docs")
OUT = os.path.join(BASE, "_tools", "round3_facts2.txt")
from docx import Document

buf = []
def w(*a): buf.append(" ".join(str(x) for x in a))

d1 = Document(os.path.join(DOCS, "01-需求规格说明书.docx"))
d2 = Document(os.path.join(DOCS, "02-模块化设计与接口规范.docx"))
d6 = Document(os.path.join(DOCS, "06-小组分工与两周迭代计划.docx"))

def dump_table(doc, idx, label, maxrow=40):
    w("=" * 15, label, "table", idx)
    t = doc.tables[idx]
    for r in t.rows[:maxrow]:
        w("   ", " || ".join(c.text.strip().replace("\n", " ")[:110] for c in r.cells))

# --- D1 FR-13 / FR-07 / FR-14 / FR-03 cards (field/value tables: 需求编号 marker) ---
def find_fr_card(doc, fr):
    for i, t in enumerate(doc.tables):
        vals = [r.cells[1].text.strip() if len(r.cells) > 1 else "" for r in t.rows]
        if vals and vals[0] == fr:
            return i, t
    return None, None

for fr in ("FR-03", "FR-05", "FR-07", "FR-10", "FR-12", "FR-13", "FR-14"):
    i, t = find_fr_card(d1, fr)
    if t is None:
        w("!! D1 card not found", fr); continue
    w("=" * 15, "D1 card", fr, "table", i)
    for r in t.rows:
        w("   ", " || ".join(c.text.strip().replace("\n", " ⏎ ")[:300] for c in r.cells))

# --- D1 error-code table: find table whose header has 错误码 ---
for i, t in enumerate(d1.tables):
    head = [c.text.strip() for c in t.rows[0].cells]
    if any("错误码" in h for h in head):
        w("=" * 15, "D1 error-table", i, "head", head, "rows", len(t.rows))
        for r in t.rows:
            w("   ", " || ".join(c.text.strip()[:70] for c in r.cells))
    if any("规则编号" in h or ("编号" in h and "违反" in " ".join(head)) for h in head):
        w("=" * 15, "D1 BR-table?", i, "head", head, "rows", len(t.rows))

# --- D2: tables of interest by content ---
for i, t in enumerate(d2.tables):
    flat = " ".join(c.text for r in t.rows for c in r.cells)
    if "M5 评价信用" in flat or ("FR-05、BR-08" in flat):
        dump_table(d2, i, "D2 FR-mapping candidate")
    if "cancel" in flat or "PERM-023" in flat:
        dump_table(d2, i, "D2 cancel/Perm table")
    if "≥4" in flat or "bad_review_penalty" in flat:
        dump_table(d2, i, "D2 review table")
    if "Main-Class" in flat or "javafx" in flat or "启动类" in flat:
        dump_table(d2, i, "D2 main-class table")

# --- D2 paragraphs with code blocks / key strings ---
def dump_paras(doc, keys, label, ctx=3):
    ps = [p.text for p in doc.paragraphs]
    w("=" * 15, label)
    seen = set()
    for i, t in enumerate(ps):
        if any(k in t for k in keys):
            for j in range(max(0, i - 1), min(len(ps), i + ctx)):
                if j in seen:
                    continue
                seen.add(j)
                w(f"   [{j}] {ps[j][:260]}")

dump_paras(d2, ["beginTransaction", "commit(", "executeInTransaction"], "D2 transaction text", 4)
dump_paras(d2, ["内存", ":memory:", "@BeforeEach"], "D2 test db text", 4)
dump_paras(d2, ["setUserDao", "FakeUserDao"], "D2 injection text", 3)
dump_paras(d2, ["AbstractJdbcDao"], "D2 abstract dao text", 3)
dump_paras(d2, ["findById(int)"], "D2 findById text", 3)
dump_paras(d2, ["carbon.factor"], "D2 carbon keys", 2)
dump_paras(d6, ["SecurityUtil", "edu.campus.recycle.App", "MainApp", "service.impl", "启动类"], "D6 misc text", 2)

# --- schema / seed / code facts ---
sp = os.path.join(BASE, "db", "schema.sql")
sql = open(sp, encoding="utf-8").read()
for n, line in enumerate(sql.splitlines(), 1):
    if re.search(r"(status TEXT|content TEXT|price REAL|trade_type TEXT|CHECK\s*\(\s*trade_type|DEFAULT 'ON_SALE'|300)", line):
        w(f"  schema:{n}: {line.strip()[:220]}")
w("schema DRAFT lines:")
for n, line in enumerate(sql.splitlines(), 1):
    if "DRAFT" in line:
        w(f"  schema:{n}: {line.strip()[:220]}")

sd = open(os.path.join(BASE, "db", "seed-data.sql"), encoding="utf-8").read()
w("=" * 15, "seed carbon/system_config keys")
for n, line in enumerate(sd.splitlines(), 1):
    if "carbon" in line or "factor" in line:
        w(f"  seed:{n}: {line.strip()[:200]}")

code = os.path.join(BASE, "code", "green-campus", "src", "main", "java")
w("=" * 15, "code: BR codes / Main class / cancel / status default")
for p in glob.glob(os.path.join(code, "**", "*.java"), recursive=True):
    txt = open(p, encoding="utf-8").read()
    rel = os.path.relpath(p, code)
    if re.search(r'"BR-\d', txt):
        for m in re.finditer(r'"[A-Z]{2,4}-\d{2,3}[^"]*"', txt):
            w(f"  {rel}: {m.group(0)[:80]}")
    if rel.endswith("Main.java"):
        w("  MAIN FILE:", rel)
        for n, line in enumerate(txt.splitlines(), 1):
            if "class Main" in line or "package " in line:
                w(f"    {n}: {line.strip()[:120]}")
    if rel.endswith("ItemServiceImpl.java"):
        for n, line in enumerate(txt.splitlines(), 1):
            if 100 <= n <= 120:
                w(f"    IS:{n}: {line.strip()[:150]}")
    if rel.endswith("TradeServiceImpl.java"):
        for n, line in enumerate(txt.splitlines(), 1):
            if 130 <= n <= 150:
                w(f"    TS:{n}: {line.strip()[:150]}")

open(OUT, "w", encoding="utf-8").write("\n".join(buf))
print("written", OUT, len(buf), "lines")
