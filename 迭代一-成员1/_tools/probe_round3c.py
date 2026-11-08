# -*- coding: utf-8 -*-
"""第 3 轮收尾核查（Lead）：错误码口径、D2 关键项、类图/时序图口径。"""
import re, sys, io
from docx import Document

BASE = r"C:\Users\wanhe\Desktop\软件构造\迭代一-成员1"
sys.stdout.reconfigure(encoding="utf-8", errors="replace")


def doc_text(path):
    d = Document(path)
    parts = [p.text for p in d.paragraphs]
    for t in d.tables:
        for row in t.rows:
            for c in row.cells:
                parts.append(c.text)
    return "\n".join(parts)


d1 = doc_text(BASE + r"\docs\01-需求规格说明书.docx")
d2 = doc_text(BASE + r"\docs\02-模块化设计与接口规范.docx")
d6 = doc_text(BASE + r"\docs\06-小组分工与两周迭代计划.docx")

print("== 1. 错误码 ==")
pat = re.compile(r"\b(VAL|DUP|NF|PERM|DB|TX|AUTH|LOCK)-\d{2,3}\b")
c1 = set(m.group(0) for m in pat.finditer(d1))
c2 = set(m.group(0) for m in pat.finditer(d2))
print("D1 码数=%d  D2 码数=%d" % (len(c1), len(c2)))
print("仅 D1 有:", sorted(c1 - c2)[:12])
print("仅 D2 有:", sorted(c2 - c1)[:12])
print("两位语义码残留(D1 中 VAL-0xx 之外):", sorted(x for x in c1 if re.match(r"(VAL|DUP|NF|PERM|DB|TX)-\d{3}$", x))[:15])
print("D2 分段码样例:", sorted(x for x in c2 if re.match(r"(DB|NF|PERM)-[1-9]\d\d$", x))[:8])
print("D1 三位 BR:", sorted(set(re.findall(r"\bBR-\d{3}\b", d1))))
print("D2 三位 BR:", sorted(set(re.findall(r"\bBR-\d{3}\b", d2))))
print("D1 BR 两位:", sorted(set(re.findall(r"\bBR-(0[1-9]|1[0-2])\b", d1))))
print("D1 表 7- 标题数:", len(re.findall(r"7\.2\.2", d1)), " 错误码总表出现:", d1.count("错误码总表"))

print("\n== 2. D2 关键项 ==")
for kw in ["historyDetail", "countUnread", "getCredit", "CreditFirstItemSortStrategy",
           "ItemService.audit", "AdminService.audit", "ControllerSupport",
           "UserController", "ItemController", "TradeController", "ReviewController",
           "StatisticController", "AdminController", "AppController",
           "executeInTransaction", "beginTransaction", "setXxx", "cache=shared",
           "records", "totalPages", "TC-33", "33 条", "92 方法", "22 接口",
           "PasswordUtil", "SecurityUtil", "DUP-003", "DUP-041", "BR-03", "BR-031", "200 字"]:
    print("  %-28s D2=%d" % (kw, d2.count(kw)))

print("\n== 3. D1 关键项 ==")
for kw in ["DUP-003", "DUP-004", "DUP-041", "DUP-051", "records", "totalPages",
           "updateCredit(userId", "carbon.factor.sports", "SecurityUtil",
           "PasswordUtil", "DRAFT", "FR-16", "FR-17", "验收标准"]:
    print("  %-28s D1=%d" % (kw, d1.count(kw)))

print("\n== 4. D6 关键项 ==")
for kw in ["D2", "D3", "D4", "类图", "时序图", "ER", "MainApp", "edu.campus.recycle.Main",
           "SecurityUtil", "PasswordUtil", "controller", "33 条", "示意", "FR-03"]:
    print("  %-28s D6=%d" % (kw, d6.count(kw)))

print("\n== 5. 时序号口径（D1 vs D2 vs 文件）==")
for name, txt in (("D1", d1), ("D2", d2)):
    print("  %s: 6 张时序图=%d  4 张=%d  5 张=%d" % (name, txt.count("6 张时序图"), txt.count("4 张时序图"), txt.count("5 张时序图")))

print("\n== 6. 明文残留检查 ==")
for kw in ["FR-02（发布", "TODO", "占位符", "待补"]:
    print("  %-12s D1=%d D6=%d" % (kw, d1.count(kw), d6.count(kw)))
