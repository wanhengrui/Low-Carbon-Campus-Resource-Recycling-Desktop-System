# -*- coding: utf-8 -*-
"""第 3 轮 ER 生成器的小修补：item.status 默认值改 PENDING、图例补 ck_item_free_price 说明。"""
import pathlib

BASE = pathlib.Path(r"C:\Users\wanhe\Desktop\软件构造\迭代一-成员1")
GEN = BASE / "db" / "_gen_er_drawio.py"

text = GEN.read_text(encoding="utf-8")
pairs = [
    ("('status', 'TEXT', ['NOT NULL', 'DEFAULT ON_SALE']),",
     "('status', 'TEXT', ['NOT NULL', 'DEFAULT PENDING']),"),
    ("'trade_flow.item_id 上的部分唯一索引 uq_flow_item_active 保证同一物品最多一条进行中流转。\" '",
     "'trade_flow.item_id 上的部分唯一索引 uq_flow_item_active 保证同一物品最多一条进行中流转；'\n"
     "        '第 3 轮（契约 v1.1）起 item.status 默认 PENDING，且 item 表级约束 ck_item_free_price '\n"
     "        '要求 trade_type=FREE 时 price 必须为 0（Service + DB 双层校验）。\" '"),
    ("<mxGeometry x=\"40\" y=\"1260\" width=\"1560\" height=\"90\" as=\"geometry\" />",
     "<mxGeometry x=\"40\" y=\"1260\" width=\"1560\" height=\"120\" as=\"geometry\" />"),
]
for old, new in pairs:
    if old not in text:
        raise SystemExit("PATTERN NOT FOUND: %r" % old[:60])
    text = text.replace(old, new, 1)

GEN.write_text(text, encoding="utf-8")
print("PATCHED_BYTES=", GEN.stat().st_size)
