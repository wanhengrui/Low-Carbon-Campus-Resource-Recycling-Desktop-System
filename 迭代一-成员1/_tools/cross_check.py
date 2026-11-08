#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""D8 交叉一致性核对（Lead 质检用，不随交付提交）。

核对四条链：
  db/schema.sql 列  <->  code 实体类字段  <->  design/03-UML类图.drawio 属性
  docs/02 接口清单  <->  code 中的 interface 声明
用法: python cross_check.py   -> 生成 _tools/cross_check.txt
"""
import os
import re
import glob
import xml.etree.ElementTree as ET

BASE = r"C:\Users\wanhe\Desktop\软件构造\迭代一-成员1"
OUT = os.path.join(BASE, "_tools", "cross_check.txt")
L = []


def p(s=""):
    L.append(s)


def camel2snake(n):
    return re.sub(r"(?<!^)(?=[A-Z])", "_", n).lower()


def strip_comments(sql):
    sql = re.sub(r"--[^\n]*", "", sql)
    sql = re.sub(r"/\*.*?\*/", "", sql, flags=re.S)
    return sql


def parse_schema():
    path = os.path.join(BASE, "db", "schema.sql")
    sql = strip_comments(open(path, encoding="utf-8").read())
    tables = {}
    for m in re.finditer(r"CREATE\s+TABLE\s+(?:IF\s+NOT\s+EXISTS\s+)?[\"`\[]?(\w+)[\"`\]]?\s*\(",
                         sql, flags=re.I):
        name = m.group(1)
        i, depth, buf = m.end(), 1, []
        while i < len(sql) and depth:
            c = sql[i]
            if c == "(":
                depth += 1
            elif c == ")":
                depth -= 1
            if depth:
                buf.append(c)
            i += 1
        body = "".join(buf)
        cols, depth, cur = [], 0, []
        for c in body + ",":
            if c == "(":
                depth += 1
            elif c == ")":
                depth -= 1
            if c == "," and depth == 0:
                seg = "".join(cur).strip()
                cur = []
                if not seg:
                    continue
                head = seg.split()[0].strip('"`[]')
                if head.upper() in ("PRIMARY", "FOREIGN", "UNIQUE", "CHECK", "CONSTRAINT"):
                    continue
                cols.append(head)
            else:
                cur.append(c)
        tables[name] = cols
    indexes = re.findall(r"CREATE\s+(?:UNIQUE\s+)?INDEX\s+(?:IF\s+NOT\s+EXISTS\s+)?(\w+)\s+ON\s+(\w+)",
                         sql, flags=re.I)
    return tables, indexes


def parse_entities():
    d = os.path.join(BASE, "code", "green-campus", "src", "main", "java", "edu", "campus", "recycle", "entity")
    out = {}
    for f in sorted(glob.glob(os.path.join(d, "*.java"))):
        name = os.path.splitext(os.path.basename(f))[0]
        txt = open(f, encoding="utf-8").read()
        if re.search(r"\benum\s+" + name + r"\b", txt):
            out[name] = {"kind": "enum"}
            continue
        fields = re.findall(r"^\s*private\s+(?!static)(?:final\s+)?[\w<>,\[\]\. ]+?\s+(\w+)\s*;",
                            txt, flags=re.M)
        out[name] = {"kind": "class", "fields": fields}
    return out


def class2table(name):
    return camel2snake(name)


def parse_drawio():
    path = os.path.join(BASE, "design", "03-UML类图.drawio")
    root = ET.parse(path).getroot()
    cells = root.findall(".//mxCell")
    by_id = {c.get("id"): c.get("value", "") or "" for c in cells}
    classes = {}
    for cid, val in by_id.items():
        if cid.endswith("_a") or cid.endswith("_m") or cid.endswith("_t"):
            continue
        if re.fullmatch(r"«(?:enumeration|interface)»\s*\w+|\w+", (val or "").strip()):
            classes[cid] = re.sub(r"«[^»]*»\s*", "", val).strip()
    attrs = {}
    for cid, val in by_id.items():
        if not cid.endswith("_a"):
            continue
        base = cid[:-2]
        cname = classes.get(base)
        if not cname:
            continue
        flds = re.findall(r"(?:^|<br>)\s*[-+]\s*(\w+)\s*[:(]", val)
        attrs[cname] = flds
    return classes, attrs, len(cells)


def parse_code_ifaces():
    root = os.path.join(BASE, "code", "green-campus", "src", "main", "java")
    found = {}
    for f in glob.glob(os.path.join(root, "**", "*.java"), recursive=True):
        txt = open(f, encoding="utf-8").read()
        for m in re.finditer(r"public\s+(?:abstract\s+)?interface\s+(\w+)", txt):
            found[m.group(1)] = os.path.relpath(f, root).replace(os.sep, "/")
    return found


def tag_list(xs, n=6):
    xs = sorted(xs)
    return "、".join(xs) if len(xs) <= n else "、".join(xs[:n]) + f" …共{len(xs)}"


def parse_dtos():
    d = os.path.join(BASE, "code", "green-campus", "src", "main", "java", "edu", "campus", "recycle", "dto")
    out = {}
    for f in sorted(glob.glob(os.path.join(d, "*.java"))):
        name = os.path.splitext(os.path.basename(f))[0]
        txt = open(f, encoding="utf-8").read()
        flds = re.findall(r"^\s*private\s+(?!static)(?:final\s+)?[\w<>,\[\]\. ]+?\s+(\w+)\s*(?:=|;)", txt, flags=re.M)
        out[name] = flds
    return out


def main():
    tables, indexes = parse_schema()
    ents = parse_entities()
    classes, attrs, ncells = parse_drawio()
    ifaces = parse_code_ifaces()

    p("D8 交叉一致性核对报告")
    p("=" * 78)
    p(f"schema.sql: {len(tables)} 表 / {len(indexes)} 索引")
    p(f"entity 目录: {len(ents)} 个类（其中枚举 {sum(1 for v in ents.values() if v['kind']=='enum')} 个）")
    p(f"03-UML类图.drawio: mxCell {ncells} 个，识别类 {len(classes)} 个，含属性组 {len(attrs)} 个")
    p(f"code 中 interface 声明: {len(ifaces)} 个")
    p()

    p("【1】表 <-> 实体类")
    ent_classes = {k for k, v in ents.items() if v["kind"] == "class"}
    tbl2ent = {class2table(e): e for e in ent_classes}
    miss_ent = sorted(set(tables) - set(tbl2ent))
    extra_ent = sorted(set(tbl2ent) - set(tables))
    p(f"  表↔类 缺失: {tag_list(miss_ent) if miss_ent else '无'}")
    p(f"  类↔表 多余: {tag_list(extra_ent) if extra_ent else '无'}")
    p()

    p("【2】字段三方对齐（schema 列 / 实体字段 / 类图属性）")
    bad = 0
    for tbl in sorted(tables):
        ent = tbl2ent.get(tbl)
        if not ent:
            p(f"  [{tbl}] 无对应实体类，跳过")
            bad += 1
            continue
        cols = set(tables[tbl])
        flds = set(ents[ent]["fields"])
        exp = {camel2snake(x) for x in flds}
        only_schema = sorted(cols - exp)
        only_entity = sorted({camel2snake(x) for x in flds} - cols)
        dia = set(attrs.get(ent, []))
        dia_schema = {camel2snake(x) for x in dia} - {"__none__"}
        miss_dia = sorted(cols - dia_schema) if dia else []
        status = "OK" if not only_schema and not only_entity and not miss_dia else "DIFF"
        if status == "DIFF":
            bad += 1
        p(f"  [{status}] {tbl} ← {ent}: 列{len(cols)} / 字段{len(flds)} / 类图{len(dia)}")
        if only_schema:
            p(f"        schema 有、实体无: {tag_list(only_schema)}")
        if only_entity:
            p(f"        实体有、schema 无: {tag_list(only_entity)}")
        if miss_dia:
            p(f"        类图属性缺失: {tag_list(miss_dia)}")
    p(f"  小结: {len(tables)-bad} 张表三方一致 / {bad} 张存在差异")
    p()

    p("【3】枚举一致性")
    cls_names = set(classes.values())
    for e in sorted(k for k, v in ents.items() if v["kind"] == "enum"):
        p(f"  {e}: 类图{'有' if e in cls_names else '无'}")
    p()

    p("【4】接口声明 <-> D2 文档 / 契约")
    docx02 = os.path.join(BASE, "docs", "02-模块化设计与接口规范.docx")
    txt = ""
    if os.path.exists(docx02):
        from docx import Document
        d = Document(docx02)
        txt = "\n".join(x.text for x in d.paragraphs)
        for t in d.tables:
            for r in t.rows:
                txt += "\n" + " | ".join(c.text for c in r.cells)
    # 正向：code 里声明的每个接口名，在 D2 全文（段落+表格）里按整词出现即视为已覆盖
    miss_doc = sorted(n for n in ifaces if not re.search(rf"\b{re.escape(n)}\b", txt))
    # 反向：D2 里提到、但 code 未声明为 interface 的名字。
    # 排除三类合法提及：抽象类 AbstractJdbcDao、JUnit 测试桩 FakeUserDao、作为反例被否定的 SystemService。
    MENTION_ONLY = {"AbstractJdbcDao", "FakeUserDao", "SystemService"}
    doc_names = set(re.findall(r"\b([A-Z][A-Za-z]{2,}(?:Service|Dao|Factory|Strategy|EventBus|Exporter|Util))\b", txt))
    miss_code = sorted({n for n in doc_names if n.endswith(("Service", "Dao"))} - set(ifaces) - MENTION_ONLY)
    p(f"  code 有接口、D2 未出现: {tag_list(miss_doc) if miss_doc else '无'}")
    p(f"  D2 有接口、code 未声明: {tag_list(miss_code) if miss_code else '无'}")
    p(f"  （已排除的合法提及：{tag_list(sorted(MENTION_ONLY))}；判定口径=名在 D2 全文出现即算覆盖）")
    p()
    p("【4b】DTO 字段对齐（code DTO / 类图）")
    dtos = parse_dtos()
    for name in sorted(dtos):
        dia = set(attrs.get(name, []))
        code = set(dtos[name])
        miss = sorted(code - dia) if dia else []
        extra = sorted(dia - code) if dia else []
        st = "OK" if dia and not miss and not extra else ("类图无" if not dia else "DIFF")
        p(f"  [{st}] {name}: code {len(code)} 字段 / 类图 {len(dia)}")
        if miss:
            p(f"        类图缺: {tag_list(miss)}")
        if extra:
            p(f"        类图多: {tag_list(extra)}")
    p()

    p("【5】接口清单（code）")
    for k in sorted(ifaces):
        p(f"  {k:28s} {ifaces[k]}")

    open(OUT, "w", encoding="utf-8").write("\n".join(L))
    print("written:", OUT, "lines:", len(L))


if __name__ == "__main__":
    main()
