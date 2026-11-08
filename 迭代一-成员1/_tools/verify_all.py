#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""迭代一交付物自动验收脚本（Lead 质检用，不随交付提交）。

用法:
    python verify_all.py            # 全量验收
    python verify_all.py docx       # 只查 Word
    python verify_all.py drawio     # 只查 drawio
    python verify_all.py db         # 只查 SQL 脚本（新建临时库实跑）
    python verify_all.py code       # 只查 Maven 骨架结构
"""
import os
import sys
import glob
import sqlite3
import tempfile
import xml.etree.ElementTree as ET

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DOCS = os.path.join(BASE, "docs")
DESIGN = os.path.join(BASE, "design")
DB = os.path.join(BASE, "db")
CODE = os.path.join(BASE, "code", "green-campus")

results = []


def rec(item, ok, detail):
    results.append((item, "PASS" if ok else "FAIL", detail))
    return ok


def check_docx():
    from docx import Document
    from docx.oxml.ns import qn

    expect = {
        "00-能力自检与编排方案.docx": (2, 3),
        "01-需求规格说明书.docx": (30, 5),
        "02-模块化设计与接口规范.docx": (40, 6),
        "05-数据库设计说明书.docx": (40, 6),
        "06-小组分工与两周迭代计划.docx": (20, 4),
    }
    files = sorted(glob.glob(os.path.join(DOCS, "*.docx")))
    if not files:
        return rec("docx 存在性", False, "docs/ 下没有 .docx")
    for f in files:
        name = os.path.basename(f)
        try:
            d = Document(f)
        except Exception as e:  # noqa: BLE001
            rec(f"docx {name}", False, f"打不开: {e}")
            continue
        paras = [p for p in d.paragraphs if p.text.strip()]
        heads = [p for p in d.paragraphs if p.style.name.startswith("Heading")]
        tables = len(d.tables)
        # 页脚页码：footer 中是否存在 PAGE 域
        page_field = False
        for sec in d.sections:
            xml = sec.footer._element.xml
            if "PAGE" in xml or "w:fldSimple" in xml:
                page_field = True
        # 文末生成注记
        tail = "\n".join(p.text for p in d.paragraphs[-6:])
        has_note = "【生成：" in tail
        min_paras, min_tables = expect.get(name, (10, 1))
        ok = len(paras) >= min_paras and tables >= min_tables and len(heads) >= 5
        rec(
            f"docx {name}",
            ok,
            f"段落{len(paras)} 标题{len(heads)} 表格{tables} 页码域{'有' if page_field else '无'} 生成注记{'有' if has_note else '无'}",
        )
    return True


def check_drawio():
    files = sorted(glob.glob(os.path.join(DESIGN, "*.drawio")))
    if not files:
        return rec("drawio 存在性", False, "design/ 下没有 .drawio")
    for f in files:
        name = os.path.basename(f)
        size = os.path.getsize(f)
        try:
            tree = ET.parse(f)
        except Exception as e:  # noqa: BLE001
            rec(f"drawio {name}", False, f"XML 解析失败: {e}")
            continue
        root = tree.getroot()
        diagrams = root.findall(".//diagram")
        cells = root.findall(".//mxCell")
        edges = [c for c in cells if c.get("edge") == "1"]
        vertices = [c for c in cells if c.get("vertex") == "1"]
        ok = size > 8000 and len(cells) >= 40 and len(diagrams) >= 1
        rec(
            f"drawio {name}",
            ok,
            f"大小{size//1024}KB 分页{len(diagrams)} mxCell{len(cells)} 顶点{len(vertices)} 边{len(edges)}",
        )
    return True


def check_db():
    schema = os.path.join(DB, "schema.sql")
    seed = os.path.join(DB, "seed-data.sql")
    if not os.path.exists(schema):
        return rec("schema.sql", False, "文件不存在")
    sql = open(schema, encoding="utf-8").read()
    fd, path = tempfile.mkstemp(suffix=".db")
    os.close(fd)
    os.remove(path)
    con = sqlite3.connect(path)
    try:
        con.executescript(sql)
        con.commit()
        tables = [r[0] for r in con.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%' ORDER BY name")]
        idx = [r[0] for r in con.execute(
            "SELECT name FROM sqlite_master WHERE type='index' AND name NOT LIKE 'sqlite_%'")]
        integ = con.execute("PRAGMA integrity_check").fetchone()[0]
        fk = con.execute("PRAGMA foreign_key_check").fetchall()
        want = {"user", "category", "item", "item_image", "favorite", "trade_message",
                "trade_flow", "review", "credit_log", "operation_log", "system_config"}
        missing = want - set(tables)
        ok = (not missing) and integ == "ok" and len(fk) == 0
        rec("schema.sql 实跑", ok,
            f"表{len(tables)}张 缺{','.join(sorted(missing)) or '无'} 索引{len(idx)}个 integrity={integ} fk_violation={len(fk)}")
        seed_ok = False
        seed_detail = "seed-data.sql 不存在"
        if os.path.exists(seed):
            try:
                con.executescript(open(seed, encoding="utf-8").read())
                con.commit()
                counts = {t: con.execute(f"SELECT COUNT(*) FROM {t}").fetchone()[0] for t in sorted(table for table in tables if table != "sqlite_sequence")}
                empty = [t for t, c in counts.items() if c == 0]
                seed_ok = "user" not in empty and "item" not in empty and "category" not in empty
                seed_detail = "行数: " + " ".join(f"{k}={v}" for k, v in counts.items())
            except Exception as e:  # noqa: BLE001
                seed_detail = f"导入失败: {e}"
        rec("seed-data.sql 导入", seed_ok, seed_detail)
    except Exception as e:  # noqa: BLE001
        rec("schema.sql 实跑", False, f"执行失败: {e}")
    finally:
        con.close()
        try:
            os.remove(path)
        except OSError:
            pass
    return True


def check_code():
    if not os.path.isdir(CODE):
        return rec("code/green-campus", False, "目录不存在")
    pom = os.path.join(CODE, "pom.xml")
    java_files = glob.glob(os.path.join(CODE, "**", "*.java"), recursive=True)
    pkgs = {os.path.relpath(os.path.dirname(f), os.path.join(CODE, "src", "main", "java")).replace(os.sep, ".")
            for f in java_files if os.path.join("src", "main", "java") in f}
    ok = os.path.exists(pom) and len(java_files) >= 40
    rec("code 结构", ok, f"pom.xml{'有' if os.path.exists(pom) else '无'} java文件{len(java_files)}个 包{len(pkgs)}个")
    for layer in ["entity", "dao", "service", "util", "exception", "config", "dto", "ui", "controller"]:
        hit = any(f"edu.campus.recycle.{layer}" in p for p in pkgs)
        rec(f"  包 {layer}", hit, "存在" if hit else "缺失")
    return True


def main():
    which = sys.argv[1] if len(sys.argv) > 1 else "all"
    print(f"=== 迭代一交付物验收 @ {BASE} ===\n")
    if which in ("all", "docx"):
        print("[1] Word 文档")
        check_docx()
        print()
    if which in ("all", "drawio"):
        print("[2] drawio 图")
        check_drawio()
        print()
    if which in ("all", "db"):
        print("[3] SQL 脚本实跑")
        check_db()
        print()
    if which in ("all", "code"):
        print("[4] Maven 骨架")
        check_code()
        print()

    fails = [r for r in results if r[1] == "FAIL"]
    for item, status, detail in results:
        print(f"  [{status}] {item} — {detail}")
    print()
    print(f"合计 {len(results)} 项：PASS {len(results)-len(fails)} / FAIL {len(fails)}")
    return 0 if not fails else 1


if __name__ == "__main__":
    sys.exit(main())
