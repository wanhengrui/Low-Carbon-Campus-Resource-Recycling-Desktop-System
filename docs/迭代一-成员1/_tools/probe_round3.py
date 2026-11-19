# -*- coding: utf-8 -*-
"""Round-3 fix probe: dump facts needed for consistency rulings."""
import re, os, glob

BASE = r"C:\Users\wanhe\Desktop\软件构造\迭代一-成员1"
DOCS = os.path.join(BASE, "docs")
OUT = os.path.join(BASE, "_tools", "round3_facts.txt")

from docx import Document

buf = []
def w(*a):
    buf.append(" ".join(str(x) for x in a))

def table_texts(doc):
    for i, t in enumerate(doc.tables):
        rows = [[c.text.strip() for c in r.cells] for r in t.rows]
        yield i, rows

d1 = Document(os.path.join(DOCS, "01-需求规格说明书.docx"))
d2 = Document(os.path.join(DOCS, "02-模块化设计与接口规范.docx"))
d6 = Document(os.path.join(DOCS, "06-小组分工与两周迭代计划.docx"))

# --- 1. D1 error-code table ---
w("=" * 30, "D1 tables containing 错误码 / VAL- / DUP-")
for i, rows in table_texts(d1):
    flat = " ".join(" ".join(r) for r in rows)
    if "错误码" in flat or "VAL-" in flat or "DUP-" in flat:
        w("-- D1 table", i, "rows", len(rows))
        for r in rows[:40]:
            w("   ", " | ".join(x[:70] for x in r))

# --- 2. D2 tables containing codes ---
w("=" * 30, "D2 tables containing VAL-/DUP-/NF-/PERM-/DB-/TX-")
for i, rows in table_texts(d2):
    flat = " ".join(" ".join(r) for r in rows)
    if re.search(r"(VAL-|DUP-|PERM-|TX-|DB-\d)", flat):
        codes = sorted(set(re.findall(r"\b(?:VAL|DUP|NF|PERM|BR|DB|TX|LOCK|AUTH)-\d{2,3}\b", flat)))
        w("-- D2 table", i, "rows", len(rows), "codes:", ",".join(codes)[:400])

# --- 3. D2 table 11 (FR mapping) ---
w("=" * 30, "D2 table 11 raw")
rows = list(table_texts(d2))
if len(rows) > 11:
    i, r = rows[11]
    for x in r:
        w("   ", " | ".join(y[:80] for y in x))

# --- 4. D2 tables mentioning PageResult / sortBy / updateCredit ---
for i, rows in table_texts(d2):
    flat = " ".join(" ".join(r) for r in rows)
    for k in ("PageResult", "sortType", "updateCredit", "beginTransaction", "≤300", "300 字", "≥4"):
        if k in flat:
            w("== D2 table", i, "hits", k)
            for r in rows:
                line = " | ".join(r)
                if k in line:
                    w("    ", line[:220])

# --- 5. D1 text hits ---
t1 = "\n".join(p.text for p in d1.paragraphs) + "\n" + "\n".join(" | ".join(c.text for c in r.cells) for t in d1.tables for r in t.rows)
for k in ("rows", "records", "sortType", "sortBy", "updateCredit", "BR-005", "BR-004", "300 字", "200 字", "FR-03", "成员1"):
    w("D1 count", k, t1.count(k))

# --- 6. D6 text hits ---
t6 = "\n".join(p.text for p in d6.paragraphs) + "\n" + "\n".join(" | ".join(c.text for c in r.cells) for t in d6.tables for r in t.rows)
for k in ("D2", "D3", "D4", "SecurityUtil", "PasswordUtil", "MainApp", "edu.campus.recycle.App", "service.impl"):
    w("D6 count", k, t6.count(k))
w("=" * 30, "D6 tables 2,3,4,8 (分工/交付物)")
for idx in (2, 3, 4, 8):
    if idx < len(d6.tables):
        w("-- D6 table", idx)
        for r in d6.tables[idx].rows:
            w("   ", " | ".join(c.text.strip()[:60] for c in r.cells))

# --- 7. schema facts ---
sp = os.path.join(BASE, "db", "schema.sql")
sql = open(sp, encoding="utf-8").read()
for k in ("DEFAULT 'ON_SALE'", "DRAFT", "300", "content", "carbon.factor", "trade_type", "CHECK (price"):
    w("schema count", k, sql.count(k))
for line in sql.splitlines():
    if re.search(r"(status TEXT NOT NULL DEFAULT|content TEXT|price REAL|trade_type TEXT)", line):
        w("  schema:", line.strip()[:200])
    if "carbon.factor" in line:
        w("  carbon:", line.strip()[:160])

# --- 8. code facts: publish status, cancel perms, sort strategies, service methods ---
code = os.path.join(BASE, "code", "green-campus", "src", "main", "java")
def grep(path_pattern, pattern, label, limit=12):
    hits = 0
    for p in glob.glob(os.path.join(code, "**", path_pattern), recursive=True):
        for n, line in enumerate(open(p, encoding="utf-8"), 1):
            if re.search(pattern, line):
                w(f"  {label}: {os.path.basename(p)}:{n}: {line.strip()[:150]}")
                hits += 1
                if hits >= limit:
                    return
grep("ItemServiceImpl.java", r"status|PENDING|ON_SALE", "publish")
grep("TradeServiceImpl.java", r"participant|isAdmin|sellerId|buyerId|trade_bonus", "confirm/cancel")
grep("ItemStatus.java", r"[A-Z_]{3,}", "enum")
grep("ItemQuery.java", r"sortBy|String sort", "itemquery")
grep("TradeService.java", r"history|detail", "tradesvc")
grep("UserService.java", r"getCredit|Credit", "usersvc")

open(OUT, "w", encoding="utf-8").write("\n".join(buf))
print("written", OUT, len(buf), "lines")
