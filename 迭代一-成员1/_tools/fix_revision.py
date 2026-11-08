# -*- coding: utf-8 -*-
"""fix_revision.py —— 统一修订记录与文末轮次注记（可重复执行，幂等）。

背景：各文档由队友脚本生成，生成器写入的历史日期为示意值，或轮次注记停留在第 1 轮。
本脚本把 5 份 docx 的「修订记录」表改为真实记录（全部 2026-11-02，成员1 主笔/质检），
并把文末 `【生成：…】` 注记统一为第 3 轮。

用法： python _tools/fix_revision.py
"""
import os
from docx import Document

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DOCS = os.path.join(BASE, "docs")

ROWS = {
    "01-需求规格说明书.docx": [
        ["V0.1", "2026-11-02", "成员1", "初稿：项目概述、范围边界、目标用户与角色、功能需求 FR-01…FR-17 框架", "草稿"],
        ["V0.2", "2026-11-02", "成员1", "补全非功能需求 NFR-01…NFR-10、业务规则 BR-01…BR-12、角色权限矩阵", "草稿"],
        ["V0.3", "2026-11-02", "成员1", "补齐用例 UC-01…UC-08（含异常流与后置条件）、需求追踪矩阵", "草稿"],
        ["V1.0", "2026-11-02", "成员1", "与《共享契约》逐字对齐：需求编号、字段名、验收标准；补充项统一标注【建议补充】", "定稿"],
        ["V1.1", "2026-11-02", "成员1", "第 3 轮评审修正：错误码总表、BR 两位编号、PageResult/updateCredit 口径、FR-14 统计口径", "定稿"],
    ],
    "02-模块化设计与接口规范.docx": [
        ["V0.1", "2026-11-02", "成员1", "初稿：分层架构、包结构、模块划分、接口签名清单、异常体系、设计模式落点"],
        ["V0.5", "2026-11-02", "成员1", "第 2 轮：补 5.7 节 util 回调接口；与 code 实际签名逐字核对（22 接口 89 方法）"],
        ["V1.0", "2026-11-02", "成员1", "第 3 轮评审修正：FR 追踪编号、事务模板方法口径、测试注入与内存库方案、评价与取消规则、新增 3 个 Service 方法与 6 个 Controller"],
    ],
    "05-数据库设计说明书.docx": [
        ["v0.9", "2026-11-02", "成员1", "搭建章节框架，确定 11 张表字段草案"],
        ["v1.0.0", "2026-11-02", "成员1", "按《共享契约》第 3 节定稿 11 张表字段/约束/索引/事务边界；追加附录 B（脚本清单与 javac、JUnit、Main 实测记录）"],
        ["v1.1.0", "2026-11-02", "成员1", "第 3 轮：item.status 默认值改 PENDING、新增 FREE 价格库层 CHECK、消息长度 ≤200 字，并重跑全部数据库验证"],
    ],
    "06-小组分工与两周迭代计划.docx": [
        ["V0.1", "2026-11-02", "成员1", "分工框架：角色边界、迭代一任务分解、里程碑", "草稿"],
        ["V0.2", "2026-11-02", "成员1", "补迭代一 14 天排期表（D1–D14）、迭代二接口交接清单、Git 协作约定", "草稿"],
        ["V1.0", "2026-11-02", "成员1", "补风险与应对（含砍功能顺序）、质量门禁；成员2/3 任务标注为建议分工供组内确认", "定稿"],
        ["V1.1", "2026-11-02", "成员1", "第 3 轮：交付物编号纠偏（D1–D7 与文件一一对应）、工具类命名统一为 PasswordUtil、主类口径、Service 归属与门禁用例数", "定稿"],
    ],
}

NOTE = {
    "01-需求规格说明书.docx": "【生成：deepseek-flash / doc-writer / 第 3 轮】",
    "02-模块化设计与接口规范.docx": "【生成：deepseek-flash / arch-modeler / 第 3 轮】",
    "05-数据库设计说明书.docx": "【生成：deepseek-flash / data-layer / 第 3 轮】",
    "06-小组分工与两周迭代计划.docx": "【生成：deepseek-flash / doc-writer / 第 3 轮】",
}


def set_cell(cell, text):
    p = cell.paragraphs[0]
    runs = p.runs
    if runs:
        runs[0].text = text
        for r in runs[1:]:
            r.text = ""
    else:
        p.add_run(text)


def set_para(p, text):
    runs = p.runs
    if runs:
        runs[0].text = text
        for r in runs[1:]:
            r.text = ""
    else:
        p.add_run(text)


def rewrite_table_rows(table, rows):
    """按 rows 重写数据行；行数不足时复制最后一行 XML 追加，多余行删除。"""
    import copy
    data_rows = list(table.rows[1:])
    while len(data_rows) < len(rows):
        new_tr = copy.deepcopy(data_rows[-1]._tr)
        data_rows[-1]._tr.addnext(new_tr)
        data_rows = list(table.rows[1:])
    while len(data_rows) > len(rows):
        tr = data_rows[-1]._tr
        tr.getparent().remove(tr)
        data_rows = list(table.rows[1:])
    for r, values in zip(data_rows, rows):
        cells = r.cells
        for j, v in enumerate(values[:len(cells)]):
            set_cell(cells[j], v)


def main():
    for name, rows in ROWS.items():
        path = os.path.join(DOCS, name)
        if not os.path.exists(path):
            print("[skip] missing", name)
            continue
        doc = Document(path)
        if len(doc.tables) < 2:
            print("[warn] no revision table", name)
            continue
        rewrite_table_rows(doc.tables[1], rows)
        note_done = False
        for para in reversed(doc.paragraphs):
            if "【生成：" in para.text:
                set_para(para, NOTE[name])
                note_done = True
                break
        doc.save(path)
        print(f"[ok] {name}: revision rows={len(rows)}, note={note_done}")


if __name__ == "__main__":
    main()

