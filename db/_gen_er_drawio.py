# -*- coding: utf-8 -*-
"""
生成 design/05-ER图.drawio（drawio 原生 XML，非图片）的脚本。

用途：依据《_共享契约-实体与接口基线.md》第 3 节 11 张表字段，程序化生成
      字段级 ER 图：swimlane 实体框 + 字段列（PK 加粗、FK 标注 FK→表.字段），
      关系线连到具体字段并标注 1 / N 基数。避免手工拼 XML 的错漏。

运行：
    python _gen_er_drawio.py
输出：
    ../design/05-ER图.drawio
"""
import os
import sys
from xml.sax.saxutils import escape

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
OUT_FILE = os.path.normpath(os.path.join(BASE_DIR, '..', 'design', '05-ER图.drawio'))

# ---------------------------------------------------------------------------
# 实体定义：(实体名, 中文名, 字段列表[(字段名, 类型, [约束标记...])], x, y, 宽)
# 约束标记：PK / NOT NULL / UQ / FK→表.字段 / DEFAULT 值 / CHECK ...（只标关键项，保证框内可读）
# ---------------------------------------------------------------------------
ENTITIES = [
    ('user', '用户', [
        ('id', 'INTEGER', ['PK']),
        ('username', 'TEXT', ['NOT NULL', 'UQ']),
        ('password_hash', 'TEXT', ['NOT NULL']),
        ('salt', 'TEXT', ['NOT NULL']),
        ('real_name', 'TEXT', ['NOT NULL']),
        ('student_no', 'TEXT', ['UQ']),
        ('role', 'TEXT', ['NOT NULL', 'DEFAULT STUDENT']),
        ('college', 'TEXT', []),
        ('contact', 'TEXT', []),
        ('credit_score', 'INTEGER', ['NOT NULL', 'DEFAULT 100']),
        ('status', 'TEXT', ['NOT NULL', 'DEFAULT ACTIVE']),
        ('fail_count', 'INTEGER', ['NOT NULL', 'DEFAULT 0']),
        ('locked_until', 'TEXT', []),
        ('created_at', 'TEXT', ['NOT NULL']),
        ('updated_at', 'TEXT', ['NOT NULL']),
        ('last_login_at', 'TEXT', []),
    ], 700, 60, 340),
    ('category', '分类', [
        ('id', 'INTEGER', ['PK']),
        ('name', 'TEXT', ['NOT NULL']),
        ('parent_id', 'INTEGER', ['FK→category.id']),
        ('sort_order', 'INTEGER', ['NOT NULL', 'DEFAULT 0']),
        ('enabled', 'INTEGER', ['NOT NULL', 'DEFAULT 1']),
        ('created_at', 'TEXT', ['NOT NULL']),
    ], 300, 60, 330),
    ('item', '闲置物品', [
        ('id', 'INTEGER', ['PK']),
        ('owner_id', 'INTEGER', ['NOT NULL', 'FK→user.id']),
        ('category_id', 'INTEGER', ['NOT NULL', 'FK→category.id']),
        ('title', 'TEXT', ['NOT NULL']),
        ('description', 'TEXT', ['NOT NULL']),
        ('trade_type', 'TEXT', ['NOT NULL']),
        ('price', 'REAL', ['NOT NULL', 'DEFAULT 0']),
        ('original_price', 'REAL', []),
        ('condition_level', 'INTEGER', ['NOT NULL', 'DEFAULT 9']),
        ('tags', 'TEXT', []),
        ('status', 'TEXT', ['NOT NULL', 'DEFAULT PENDING']),
        ('view_count', 'INTEGER', ['NOT NULL', 'DEFAULT 0']),
        ('favorite_count', 'INTEGER', ['NOT NULL', 'DEFAULT 0']),
        ('audit_remark', 'TEXT', []),
        ('created_at', 'TEXT', ['NOT NULL']),
        ('updated_at', 'TEXT', ['NOT NULL']),
        ('published_at', 'TEXT', []),
    ], 700, 580, 340),
    ('item_image', '物品图片', [
        ('id', 'INTEGER', ['PK']),
        ('item_id', 'INTEGER', ['NOT NULL', 'FK→item.id']),
        ('file_path', 'TEXT', ['NOT NULL']),
        ('sort_order', 'INTEGER', ['NOT NULL', 'DEFAULT 0']),
        ('created_at', 'TEXT', ['NOT NULL']),
    ], 300, 300, 330),
    ('favorite', '收藏', [
        ('id', 'INTEGER', ['PK']),
        ('user_id', 'INTEGER', ['NOT NULL', 'FK→user.id']),
        ('item_id', 'INTEGER', ['NOT NULL', 'FK→item.id']),
        ('created_at', 'TEXT', ['NOT NULL']),
    ], 1120, 330, 330),
    ('trade_message', '流转沟通消息', [
        ('id', 'INTEGER', ['PK']),
        ('item_id', 'INTEGER', ['NOT NULL', 'FK→item.id']),
        ('from_user_id', 'INTEGER', ['NOT NULL', 'FK→user.id']),
        ('to_user_id', 'INTEGER', ['NOT NULL', 'FK→user.id']),
        ('content', 'TEXT', ['NOT NULL']),
        ('is_read', 'INTEGER', ['NOT NULL', 'DEFAULT 0']),
        ('created_at', 'TEXT', ['NOT NULL']),
    ], 1120, 60, 340),
    ('trade_flow', '流转记录', [
        ('id', 'INTEGER', ['PK']),
        ('item_id', 'INTEGER', ['NOT NULL', 'FK→item.id']),
        ('seller_id', 'INTEGER', ['NOT NULL', 'FK→user.id']),
        ('buyer_id', 'INTEGER', ['NOT NULL', 'FK→user.id']),
        ('flow_type', 'TEXT', ['NOT NULL']),
        ('amount', 'REAL', ['NOT NULL', 'DEFAULT 0']),
        ('status', 'TEXT', ['NOT NULL', 'DEFAULT APPLYING']),
        ('apply_remark', 'TEXT', []),
        ('cancel_reason', 'TEXT', []),
        ('created_at', 'TEXT', ['NOT NULL']),
        ('finished_at', 'TEXT', []),
    ], 1120, 520, 340),
    ('review', '评价', [
        ('id', 'INTEGER', ['PK']),
        ('flow_id', 'INTEGER', ['NOT NULL', 'FK→trade_flow.id']),
        ('reviewer_id', 'INTEGER', ['NOT NULL', 'FK→user.id']),
        ('reviewee_id', 'INTEGER', ['NOT NULL', 'FK→user.id']),
        ('score', 'INTEGER', ['NOT NULL', 'CHECK 1-5']),
        ('content', 'TEXT', []),
        ('created_at', 'TEXT', ['NOT NULL']),
    ], 1120, 920, 340),
    ('credit_log', '信用分流水', [
        ('id', 'INTEGER', ['PK']),
        ('user_id', 'INTEGER', ['NOT NULL', 'FK→user.id']),
        ('flow_id', 'INTEGER', ['FK→trade_flow.id']),
        ('delta', 'INTEGER', ['NOT NULL']),
        ('score_after', 'INTEGER', ['NOT NULL']),
        ('reason', 'TEXT', ['NOT NULL']),
        ('created_at', 'TEXT', ['NOT NULL']),
    ], 1530, 300, 340),
    ('operation_log', '关键操作日志', [
        ('id', 'INTEGER', ['PK']),
        ('operator_id', 'INTEGER', ['FK→user.id']),
        ('operation', 'TEXT', ['NOT NULL']),
        ('target_type', 'TEXT', []),
        ('target_id', 'INTEGER', []),
        ('detail', 'TEXT', []),
        ('ip', 'TEXT', []),
        ('created_at', 'TEXT', ['NOT NULL']),
    ], 300, 700, 330),
    ('system_config', '系统配置', [
        ('id', 'INTEGER', ['PK']),
        ('config_key', 'TEXT', ['NOT NULL', 'UQ']),
        ('config_value', 'TEXT', ['NOT NULL']),
        ('description', 'TEXT', []),
        ('updated_at', 'TEXT', ['NOT NULL']),
    ], 700, 1180, 330),
]

# 关系：(id, 源字段, 目标字段, 关系动词, 源端基数, 目标端基数, 覆盖样式dict)
# 源端/目标端写 "实体.字段"，生成时自动解析为字段 cell id
RELATIONS = [
    ('r_user_item',        'user.id',        'item.owner_id',          '发布', '1', 'N', None),
    ('r_category_item',    'category.id',    'item.category_id',       '归属', '1', 'N', None),
    ('r_category_self',    'category.id',    'category.parent_id',     '父分类(自关联)', '1', 'N',
     {'self_loop': True}),
    ('r_item_image',       'item.id',        'item_image.item_id',     '附图', '1', 'N',
     {'exit': (0, 0.5), 'entry': (1, 0.5)}),
    ('r_user_favorite',    'user.id',        'favorite.user_id',       '收藏', '1', 'N', None),
    ('r_item_favorite',    'item.id',        'favorite.item_id',       '被收藏', '1', 'N', None),
    ('r_item_message',     'item.id',        'trade_message.item_id',  '关联物品', '1', 'N', None),
    ('r_user_msg_from',    'user.id',        'trade_message.from_user_id', '发送', '1', 'N', None),
    ('r_user_msg_to',      'user.id',        'trade_message.to_user_id',   '接收', '1', 'N', None),
    ('r_item_flow',        'item.id',        'trade_flow.item_id',     '流转物品', '1', 'N', None),
    ('r_user_flow_seller', 'user.id',        'trade_flow.seller_id',   '出让', '1', 'N', None),
    ('r_user_flow_buyer',  'user.id',        'trade_flow.buyer_id',    '受让', '1', 'N', None),
    ('r_flow_review',      'trade_flow.id',  'review.flow_id',         '产生评价', '1', 'N',
     {'exit': (0.5, 1), 'entry': (0.5, 0)}),
    ('r_user_reviewer',    'user.id',        'review.reviewer_id',     '评价人', '1', 'N', None),
    ('r_user_reviewee',    'user.id',        'review.reviewee_id',     '被评价人', '1', 'N', None),
    ('r_user_credit',      'user.id',        'credit_log.user_id',     '信用流水', '1', 'N', None),
    ('r_flow_credit',      'trade_flow.id',  'credit_log.flow_id',     '关联流转', '1', '0..N',
     {'exit': (1, 0.5), 'entry': (0, 0.5)}),
    ('r_user_oplog',       'user.id',        'operation_log.operator_id', '操作记录', '1', '0..N',
     {'exit': (0, 0.5), 'entry': (1, 0.5)}),
]

FIELD_ROW_H = 24
HEADER_H = 30
SWIMLANE_STYLE = (
    'swimlane;fontStyle=1;align=center;verticalAlign=top;childLayout=stackLayout;horizontal=1;'
    'startSize=30;horizontalStack=0;resizeParent=1;resizeParentMax=0;resizeLast=0;collapsible=1;'
    'marginBottom=0;html=1;fontSize=13;fillColor=#dae8fc;strokeColor=#6c8ebf;swimlaneFillColor=#ffffff;'
    'fontColor=#1f3864;'
)
FIELD_STYLE = (
    'text;strokeColor=none;fillColor=none;align=left;verticalAlign=middle;spacingLeft=8;'
    'spacingRight=4;overflow=hidden;rotatable=0;points=[[0,0.5],[1,0.5]];portConstraint=eastwest;'
    'html=1;fontSize=11;fontColor=#333333;'
)
FIELD_STYLE_PK = FIELD_STYLE + 'fontStyle=1;fontColor=#933333;'
FIELD_STYLE_FK = FIELD_STYLE + 'fontColor=#0b5394;'
EDGE_STYLE_BASE = (
    'edgeStyle=orthogonalEdgeStyle;rounded=1;orthogonalLoop=1;jettySize=auto;html=1;'
    'endArrow=ERmany;startArrow=ERone;startFill=0;endFill=0;strokeColor=#666666;strokeWidth=1;'
    'fontSize=10;labelBackgroundColor=#ffffff;'
)


def field_cell_id(entity, field):
    return 'f_%s_%s' % (entity, field)


def build_field_text(name, ftype, flags):
    parts = ['%s : %s' % (name, ftype)]
    if flags:
        parts.append('[' + ' '.join(flags) + ']')
    return '  '.join(parts)


def build_xml():
    lines = []
    add = lines.append
    add('<mxfile host="app.diagrams.net" modified="2026-11-02T15:00:00.000Z" agent="data-layer" '
        'version="24.7.17" type="device">')
    add('  <diagram id="er" name="ER图">')
    add('    <mxGraphModel dx="1600" dy="1000" grid="1" gridSize="10" guides="1" tooltips="1" '
        'connect="1" arrows="1" fold="1" page="1" pageScale="1" pageWidth="2000" pageHeight="1450" '
        'math="0" shadow="0">')
    add('      <root>')
    add('        <mxCell id="0" />')
    add('        <mxCell id="1" parent="0" />')

    # 标题与图例
    add('        <mxCell id="title" value="低碳校园资源循环流转系统（GreenCampus Recycle）—— '
        '实体关系图（ER 图）· 11 个实体 / 18 条关系" '
        'style="text;html=1;align=left;verticalAlign=middle;fontSize=20;fontStyle=1;fontColor=#1f3864;" '
        'vertex="1" parent="1">')
    add('          <mxGeometry x="40" y="-20" width="1200" height="40" as="geometry" />')
    add('        </mxCell>')
    add('        <mxCell id="legend" value="图例：字段行格式为“字段名 : 类型 [约束]”；'
        '[PK] 为主键；[FK→表.字段] 为外键；[UQ] 为唯一约束。关系线为鸦爪（crow\'s foot）表示法：'
        '源端 1（ERone）、目标端 N/0..N（ERmany），连线两端锚定具体字段。'
        'trade_flow.item_id 上的部分唯一索引 uq_flow_item_active 保证同一物品最多一条进行中流转；'
        '第 3 轮（契约 v1.1）起 item.status 默认 PENDING，且 item 表级约束 ck_item_free_price '
        '要求 trade_type=FREE 时 price 必须为 0（Service + DB 双层校验）。" '
        'style="text;html=1;align=left;verticalAlign=top;fontSize=11;fontColor=#444444;'
        'whiteSpace=wrap;fillColor=#fff2cc;strokeColor=#d6b656;spacingLeft=8;spacingTop=6;" '
        'vertex="1" parent="1">')
    add('          <mxGeometry x="40" y="1260" width="1560" height="120" as="geometry" />')
    add('        </mxCell>')

    # 实体框与字段行
    for ent, cn, fields, x, y, w in ENTITIES:
        height = HEADER_H + FIELD_ROW_H * len(fields) + 6
        add('        <mxCell id="e_%s" value="%s %s" style="%s" vertex="1" parent="1">'
            % (ent, ent, cn, SWIMLANE_STYLE))
        add('          <mxGeometry x="%d" y="%d" width="%d" height="%d" as="geometry" />'
            % (x, y, w, height))
        add('        </mxCell>')
        for i, (fname, ftype, flags) in enumerate(fields):
            text = build_field_text(fname, ftype, flags)
            style = FIELD_STYLE_PK if 'PK' in flags else (
                FIELD_STYLE_FK if any(f.startswith('FK') for f in flags) else FIELD_STYLE)
            add('        <mxCell id="%s" value="%s" style="%s" vertex="1" parent="e_%s">'
                % (field_cell_id(ent, fname), escape(text), style, ent))
            add('          <mxGeometry x="0" y="%d" width="%d" height="%d" as="geometry" />'
                % (HEADER_H + i * FIELD_ROW_H, w, FIELD_ROW_H))
            add('        </mxCell>')

    # 关系线（连到具体字段，两端标基数）
    for rid, src, tgt, verb, src_mult, tgt_mult, override in RELATIONS:
        s_ent, s_field = src.split('.')
        t_ent, t_field = tgt.split('.')
        style = EDGE_STYLE_BASE
        geometry = '          <mxGeometry relative="1" as="geometry" />'
        if override and override.get('self_loop'):
            style += 'exitX=0;exitY=0.2;entryX=0;entryY=0.8;'
            geometry = ('          <mxGeometry relative="1" as="geometry">\n'
                        '            <Array as="points">\n'
                        '              <mxPoint x="250" y="120" />\n'
                        '              <mxPoint x="250" y="250" />\n'
                        '            </Array>\n'
                        '          </mxGeometry>')
        elif override:
            ex, ey = override['exit']
            nx, ny = override['entry']
            style += 'exitX=%s;exitY=%s;entryX=%s;entryY=%s;' % (ex, ey, nx, ny)
        add('        <mxCell id="%s" value="%s" style="%s" edge="1" parent="1" '
            'source="%s" target="%s">'
            % (rid, escape(verb), style, field_cell_id(s_ent, s_field), field_cell_id(t_ent, t_field)))
        add(geometry)
        add('        </mxCell>')
        # 源端基数标签（1）
        add('        <mxCell id="%s_s" value="%s" style="edgeLabel;html=1;align=center;'
            'verticalAlign=middle;resizable=0;points=[];fontSize=11;fontStyle=1;'
            'labelBackgroundColor=#ffffff;" connectable="0" vertex="1" parent="%s">'
            % (rid, escape(src_mult), rid))
        add('          <mxGeometry x="-0.85" relative="1" as="geometry">')
        add('            <mxPoint x="-8" y="0" as="offset" />')
        add('          </mxGeometry>')
        add('        </mxCell>')
        # 目标端基数标签（N / 0..N）
        add('        <mxCell id="%s_t" value="%s" style="edgeLabel;html=1;align=center;'
            'verticalAlign=middle;resizable=0;points=[];fontSize=11;fontStyle=1;'
            'labelBackgroundColor=#ffffff;" connectable="0" vertex="1" parent="%s">'
            % (rid, escape(tgt_mult), rid))
        add('          <mxGeometry x="0.85" relative="1" as="geometry">')
        add('            <mxPoint x="8" y="0" as="offset" />')
        add('          </mxGeometry>')
        add('        </mxCell>')

    add('      </root>')
    add('    </mxGraphModel>')
    add('  </diagram>')
    add('</mxfile>')
    return '\n'.join(lines) + '\n'


def main():
    xml = build_xml()
    os.makedirs(os.path.dirname(OUT_FILE), exist_ok=True)
    with open(OUT_FILE, 'w', encoding='utf-8', newline='\n') as f:
        f.write(xml)
    cells = xml.count('<mxCell ')
    print('已生成：%s' % OUT_FILE)
    print('文件大小：%d 字节（>15KB 要求：%s）' % (len(xml.encode('utf-8')),
                                                 'OK' if len(xml.encode('utf-8')) > 15 * 1024 else 'FAIL'))
    print('mxCell 数量：%d（>=80 要求：%s）' % (cells, 'OK' if cells >= 80 else 'FAIL'))


if __name__ == '__main__':
    sys.exit(main())
