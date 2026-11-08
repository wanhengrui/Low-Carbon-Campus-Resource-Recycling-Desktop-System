# -*- coding: utf-8 -*-
"""
schema.sql 解析器（供 D5-4 docx 构建脚本复用）。

从 db/schema.sql 中解析出：
  * 11 张表的列定义（列名、类型、约束、默认值、说明、所属实体类属性）；
  * 表级约束（外键、唯一、CHECK）；
  * 索引清单（含部分唯一索引的 WHERE 子句）。

只做静态文本解析，不连接数据库；用于生成"数据字典""约束清单""索引清单"章节，
保证 docx 内容与 schema.sql 单一来源一致。

作者：成员1（数据层）  日期：2026-11-02
"""
import pathlib
import re

SCHEMA_PATH = pathlib.Path(
    r"C:\Users\wanhe\Desktop\软件构造\迭代一-成员1\db\schema.sql"
)

# 表名 → (中文名, 所属实体类, 职责说明)
TABLE_META = {
    "user": ("用户表", "User", "账号、认证、角色、信用分与登录失败锁定状态"),
    "category": ("分类表", "Category", "两级物品分类（parent_id 为空表示一级分类）"),
    "item": ("闲置物品表", "Item", "物品主体信息、交易方式、状态与浏览/收藏计数"),
    "item_image": ("物品图片表", "ItemImage", "物品图片相对路径（二进制不入库）与展示顺序"),
    "favorite": ("收藏表", "Favorite", "用户与物品的收藏关系（toggle 语义）"),
    "trade_message": ("流转消息表", "TradeMessage", "买卖双方围绕某物品的沟通消息与已读状态"),
    "trade_flow": ("交易流转表", "TradeFlow", "一次流转的全生命周期：申请→同意→成交/取消"),
    "review": ("评价表", "Review", "成交后买卖双方互评（1-5 分）"),
    "credit_log": ("信用分流水表", "CreditLog", "信用分变化的审计流水（变动值、变动后分值、原因）"),
    "operation_log": ("操作日志表", "OperationLog", "关键操作审计日志，只追加不修改"),
    "system_config": ("系统配置表", "SystemConfig", "业务参数键值对（信用分、锁定、减排系数等）"),
}

# 列 → 实体类属性名的特殊映射（其余按 snake_case → camelCase）
ATTR_OVERRIDE = {
    "trade_message.is_read": "isRead",
}

# 外键列的删除行为业务理由（用于"约束清单"章节）
FK_REASON = {
    "item.owner_id": "发布者注销时物品一并删除，避免孤儿数据（业务上注销需先下架，DDL 兜底）",
    "item.category_id": "分类被物品引用时禁止删除，保证检索维度完整",
    "item_image.item_id": "物品删除时图片记录级联清理",
    "favorite.user_id": "用户删除时收藏级联清理",
    "favorite.item_id": "物品删除时收藏级联清理",
    "trade_message.item_id": "物品删除时消息级联清理",
    "trade_message.from_user_id": "发送者删除时消息级联清理",
    "trade_message.to_user_id": "接收者删除时消息级联清理",
    "trade_flow.item_id": "存在流转记录时禁止删除物品，保护交易历史（BR-05）",
    "trade_flow.seller_id": "存在流转记录时禁止删除卖家，保护交易历史",
    "trade_flow.buyer_id": "存在流转记录时禁止删除买家，保护交易历史",
    "review.flow_id": "流转删除时评价级联清理",
    "review.reviewer_id": "评价人删除时评价级联清理",
    "review.reviewee_id": "被评价人删除时评价级联清理",
    "credit_log.user_id": "用户删除时信用流水级联清理",
    "credit_log.flow_id": "流转删除时信用流水保留（flow_id 置空），仅保留分值与原因",
    "operation_log.operator_id": "操作人删除后日志保留（operator_id 置空），满足审计留痕（BR-11）",
    "category.parent_id": "自引用：父分类仍被子分类引用时禁止删除；NULL 表示一级分类",
}

# 索引 → (用途, 建立理由)
INDEX_REASON = {
    "idx_item_status_category": (
        "检索主路径：WHERE status=? AND category_id IN (...)",
        "组合列顺序按\"等值列在前、范围/IN 列在后\"设计；支撑首页列表与分类筛选，避免全表扫描",
    ),
    "idx_item_owner": (
        "“我的发布” WHERE owner_id=? ORDER BY created_at DESC",
        "单列等值 + 排序，覆盖用户中心列表",
    ),
    "idx_item_title": (
        "关键词检索 WHERE title LIKE '%关键词%'",
        "LIKE 前置通配符无法用索引定位，但可减小扫描范围；迭代二可换 FTS5 全文索引",
    ),
    "idx_item_image_item": (
        "按物品取图 WHERE item_id=? ORDER BY sort_order",
        "覆盖查询与排序，首图取 sort_order=0",
    ),
    "idx_favorite_user": (
        "“我的收藏” WHERE user_id=? ORDER BY created_at DESC",
        "等值 + 排序",
    ),
    "idx_msg_pair": (
        "会话查询 WHERE (from_user_id=? AND to_user_id=?) AND item_id=?",
        "三列等值；双向会话拆成两个等值查询后复用该索引",
    ),
    "idx_flow_seller": (
        "卖家侧“我收到的申请” WHERE seller_id=? AND status=?",
        "等值 + 状态过滤",
    ),
    "idx_flow_buyer": (
        "买家侧“我发起的申请” WHERE buyer_id=? AND status=?",
        "等值 + 状态过滤",
    ),
    "idx_review_reviewee": (
        "信用评价页 WHERE reviewee_id=?",
        "等值查询 + 后续聚合平均分",
    ),
    "idx_credit_user": (
        "信用分历史 WHERE user_id=? ORDER BY created_at DESC",
        "等值 + 排序，支撑个人信用页",
    ),
    "idx_oplog_operator": (
        "审计查询 WHERE operator_id=? ORDER BY created_at DESC",
        "等值 + 排序，支撑后台日志页",
    ),
    "uq_flow_item_active": (
        "同一物品同时只允许一条 APPLYING/AGREED 流转（BR-05/BR-06）",
        "部分唯一索引只约束“活动态”行；DONE/CANCELLED 历史行不参与唯一性，既防止重复成交又保留历史",
    ),
    "uq_category_root_name": (
        "一级分类重名（parent_id IS NULL）",
        "SQLite 的 UNIQUE(parent_id,name) 视 NULL 互不相等，普通唯一约束挡不住多个同名一级分类；"
        "用部分唯一索引补洞（【建议补充】，契约未列，已落 DDL 并在验证中确认）",
    ),
}

_CHECK_REASON = {
    ("user", "role"): "角色只允许学生/教师/管理员，防止越权值写入",
    ("user", "credit_score"): "信用分区间 [0,150]（BR-04）",
    ("user", "status"): "账号状态枚举",
    ("category", "enabled"): "启用标志只允许 0/1",
    ("item", "trade_type"): "交易方式枚举 SELL/EXCHANGE/FREE",
    ("item", "price"): "价格非负；EXCHANGE/FREE 传 0",
    ("item", "original_price"): "原价可空，非空时非负",
    ("item", "condition_level"): "成色 1-10 成新",
    ("item", "status"): "物品状态七态枚举",
    ("trade_flow", "flow_type"): "流转类型枚举（与物品交易方式一致）",
    ("trade_flow", "amount"): "成交金额非负",
    ("trade_flow", "status"): "流转状态四态枚举",
    ("review", "score"): "评分 1-5（BR-08）",
    ("credit_log", "score_after"): "变动后分值仍落在 [0,150]",
}


def _camel(name: str) -> str:
    parts = name.split("_")
    return parts[0] + "".join(p[:1].upper() + p[1:] for p in parts[1:])


def _default_of(text: str):
    m = re.search(r"DEFAULT\s+('(?:[^']|'')*'|[-+]?\d+(?:\.\d+)?)", text)
    if not m:
        return ""
    return m.group(1).strip("'")


def _check_of(text: str):
    idx = text.find("CHECK")
    if idx < 0:
        return ""
    expr = text[idx + len("CHECK"):].strip()
    # 去掉末尾逗号与残留换行空白
    expr = expr.rstrip().rstrip(",").strip()
    return "CHECK " + " ".join(expr.split())


def parse_schema(path: pathlib.Path = SCHEMA_PATH):
    """返回 (tables, indexes, foreign_keys)。

    tables: list[dict]，按建表顺序，含 name/comment/columns/table_constraints
    indexes: list[dict]，含 name/table/unique/columns/where/reason
    foreign_keys: list[dict]，含 table/columns/ref_table/ref_columns/on_delete/on_update
    """
    text = path.read_text(encoding="utf-8")
    lines = text.splitlines()

    tables = []
    i = 0
    current = None
    while i < len(lines):
        line = lines[i]
        m = re.match(r'\s*CREATE TABLE\s+"?(\w+)"?\s*\($', line)
        if m:
            current = {"name": m.group(1), "columns": [], "table_constraints": [],
                       "comment": "", "raw": []}
            # 向上收集紧邻的 -- 注释块作为表说明
            j = i - 1
            comment_lines = []
            while j >= 0 and lines[j].strip().startswith("--"):
                comment_lines.insert(0, lines[j].strip()[2:].strip())
                j -= 1
            current["comment"] = " ".join([c for c in comment_lines if c and not set(c) <= set("-=")])
            i += 1
            # 解析表体
            buf = []           # 当前元素的多行缓冲（含初始行）
            while i < len(lines) and not re.match(r"\s*\);", lines[i]):
                raw = lines[i]
                body, comment = raw, ""
                if "--" in raw:
                    pos = raw.find("--")
                    body, comment = raw[:pos], raw[pos + 2:].strip()
                current["raw"].append((body, comment))
                if body.strip():
                    stripped = body.strip()
                    starts_new = bool(re.match(
                        r'^(CONSTRAINT\b|UNIQUE\s*\(|PRIMARY\s+KEY\b|FOREIGN\s+KEY\b)',
                        stripped)) or bool(re.match(r'^"?\w+"?\s+[A-Z]', body.lstrip()))
                    if starts_new:
                        if buf:
                            _consume(current, buf)
                        buf = [(body, comment)]
                    else:
                        if buf:
                            buf.append((body, comment))
                i += 1
            if buf:
                _consume(current, buf)
            current.pop("_pending", None)
            tables.append(current)
            i += 1
            continue
        i += 1

    # 解析索引（支持跨行书写；先按分号把 CREATE INDEX 语句拼成一行）
    indexes = []
    idx_buf = None
    for line in lines:
        raw = line.split("--")[0].rstrip() if "--" in line else line.rstrip()
        stripped = raw.strip()
        if idx_buf is None:
            if re.match(r'^CREATE\s+(UNIQUE\s+)?INDEX\b', stripped):
                idx_buf = stripped
        else:
            idx_buf = idx_buf + " " + stripped
        if idx_buf is not None and idx_buf.rstrip().endswith(";"):
            stmt = " ".join(idx_buf.split())
            m = re.match(r'CREATE\s+(UNIQUE\s+)?INDEX\s+(\w+)\s+ON\s+"?(\w+)"?\s*\(([^)]*)\)\s*(?:WHERE\s+(.+?))?;?\s*$', stmt)
            if m:
                indexes.append({
                    "name": m.group(2),
                    "unique": bool(m.group(1)),
                    "table": m.group(3),
                    "columns": [c.strip() for c in m.group(4).split(",")],
                    "where": (m.group(5) or "").strip().rstrip(";").strip(),
                    "reason": INDEX_REASON.get(m.group(2)),
                })
            idx_buf = None

    foreign_keys = _collect_fks(tables)
    # 把 FK 信息回填到列
    for t in tables:
        for c in t["columns"]:
            fk = next((f for f in foreign_keys if f["table"] == t["name"]
                       and c["name"] in f["columns"]), None)
            if fk:
                c["fk"] = fk
    return tables, indexes, foreign_keys


def _column_starts(body: str) -> bool:
    stripped = body.strip()
    return bool(re.match(r'^"?\w+"?\s+(INTEGER|TEXT|REAL|NUMERIC|BLOB|VARCHAR|BOOLEAN)\b', stripped, re.I))


def _consume(table, buf):
    """把一段（可能多行的）DDL 片段归类为列或表级约束。"""
    body = " ".join(b[0].strip() for b in buf if b[0].strip())
    comments = [b[1] for b in buf if b[1]]
    comment = comments[-1] if comments else ""
    body = body.strip().rstrip(",").strip()

    m = re.match(r'^CONSTRAINT\s+(\w+)\s+FOREIGN\s+KEY\s*\(([^)]*)\)\s*REFERENCES\s+"?(\w+)"?\s*\(([^)]*)\)(.*)$',
                 body, re.I)
    if m:
        tail = m.group(5)
        on_delete = _opt(tail, r"ON DELETE\s+(CASCADE|RESTRICT|SET NULL|SET DEFAULT|NO ACTION)")
        on_update = _opt(tail, r"ON UPDATE\s+(CASCADE|RESTRICT|SET NULL|SET DEFAULT|NO ACTION)")
        table["table_constraints"].append({
            "type": "FK", "name": m.group(1),
            "columns": [c.strip() for c in m.group(2).split(",")],
            "ref_table": m.group(3),
            "ref_columns": [c.strip() for c in m.group(4).split(",")],
            "on_delete": on_delete, "on_update": on_update,
            "raw": body,
        })
        return
    m = re.match(r"^UNIQUE\s*\(([^)]*)\)$", body, re.I)
    if m:
        table["table_constraints"].append({
            "type": "UNIQUE",
            "columns": [c.strip() for c in m.group(1).split(",")],
            "raw": body,
        })
        return
    m = re.match(r"^(?:CONSTRAINT\s+\w+\s+)?CHECK\s*\((.*)\)$", body, re.I)
    if m:
        table["table_constraints"].append({"type": "CHECK", "expr": m.group(1).strip(), "raw": body})
        return
    m = re.match(r'^"?(\w+)"?\s+([A-Za-z]+(?:\([^)]*\))?)\s*(.*)$', body)
    if not m:
        return
    name, col_type, tail = m.group(1), m.group(2), m.group(3)
    constraints = []
    if re.search(r"PRIMARY\s+KEY", tail, re.I):
        constraints.append("PK")
    if re.search(r"AUTOINCREMENT", tail, re.I):
        constraints.append("AUTOINCREMENT")
    if re.search(r"NOT\s+NULL", tail, re.I):
        constraints.append("NOT NULL")
    if re.search(r"\bUNIQUE\b", tail, re.I):
        constraints.append("UNIQUE")
    check = _check_of(tail)
    if check:
        constraints.append(check)
    table["columns"].append({
        "name": name,
        "type": col_type.upper(),
        "not_null": "NOT NULL" in constraints,
        "pk": "PK" in constraints,
        "unique": "UNIQUE" in constraints,
        "check": check,
        "default": _default_of(tail),
        "constraints": constraints,
        "comment": comment,
        "attr": ATTR_OVERRIDE.get(table["name"] + "." + name) or _camel(name),
        "raw": body,
    })


def _opt(text, pattern):
    m = re.search(pattern, text, re.I)
    return m.group(1).upper() if m else ""


def _collect_fks(tables):
    fks = []
    for t in tables:
        for c in t["table_constraints"]:
            if c["type"] == "FK":
                fks.append({
                    "table": t["name"], "columns": c["columns"],
                    "ref_table": c["ref_table"], "ref_columns": c["ref_columns"],
                    "on_delete": c["on_delete"], "on_update": c["on_update"],
                    "reason": FK_REASON.get(t["name"] + "." + c["columns"][0], ""),
                })
    return fks


if __name__ == "__main__":
    tables, indexes, fks = parse_schema()
    print("表数量:", len(tables), "| 列总数:", sum(len(t["columns"]) for t in tables),
          "| 索引:", len(indexes), "| 外键:", len(fks))
    for t in tables:
        print("  %-14s 列=%-2d 表级约束=%d  %s" % (t["name"], len(t["columns"]),
                                                 len(t["table_constraints"]), t["comment"][:40]))
    print("--- 列样例（user）")
    for c in tables[0]["columns"]:
        print("   ", c["name"], c["type"], c["constraints"], "default=%r" % c["default"], "说明=%s" % c["comment"][:30])
    print("--- 索引")
    for x in indexes:
        print("   ", x["name"], x["table"], x["columns"], "unique=", x["unique"], "where=", x["where"])
