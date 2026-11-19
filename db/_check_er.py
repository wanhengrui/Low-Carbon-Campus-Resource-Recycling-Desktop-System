# -*- coding: utf-8 -*-
"""
D5-3 ER 图自检脚本：解析 design/05-ER图.drawio 并核对结构。

校验项：
  1) XML 可被 xml.etree.ElementTree 解析（格式合法）
  2) 根节点/图页结构符合 drawio 规范（mxfile → diagram id=er → mxGraphModel → root）
  3) mxCell 数量 >= 80，文件体积 > 15KB
  4) 11 个实体框齐全，字段数逐表核对（与契约第 3 节一致）
  5) 18 条关系线的 source/target 均为具体字段 cell（f_*），且两端带 1 / N 基数标签
运行：python _check_er.py
结果同时追加写入 db/_verify-output.txt。
"""
import os
import sys
import xml.etree.ElementTree as ET
from datetime import datetime

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DRAWIO = os.path.normpath(os.path.join(BASE_DIR, '..', 'design', '05-ER图.drawio'))
OUTPUT = os.path.join(BASE_DIR, '_verify-output.txt')

EXPECTED_FIELDS = {
    'user': 16, 'category': 6, 'item': 17, 'item_image': 5, 'favorite': 4,
    'trade_message': 7, 'trade_flow': 11, 'review': 7, 'credit_log': 7,
    'operation_log': 8, 'system_config': 5,
}
EXPECTED_EDGES = 18

report = []


def log(msg=''):
    print(msg)
    report.append(msg)


def main():
    log()
    log('=' * 78)
    log('D5-3  ER 图文件自检（design/05-ER图.drawio）')
    log('=' * 78)
    log('检查时间：%s' % datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
    log('检查文件：%s' % DRAWIO)

    size = os.path.getsize(DRAWIO)
    with open(DRAWIO, 'r', encoding='utf-8') as f:
        text = f.read()
    log('文件大小：%d 字节（要求 > 15360 字节：%s）' % (size, 'PASS' if size > 15 * 1024 else 'FAIL'))

    # 1) XML 解析
    tree = ET.parse(DRAWIO)
    root = tree.getroot()
    log('XML 解析：xml.etree.ElementTree 解析通过（根节点 <%s>）' % root.tag)

    # 2) 结构
    diagram = root.find('diagram')
    model = diagram.find('mxGraphModel')
    cells_parent = model.find('root')
    log('结构校验：mxfile → diagram(id=%s, name=%s) → mxGraphModel → root（%s）'
        % (diagram.get('id'), diagram.get('name'),
           'PASS' if diagram.get('id') == 'er' and diagram.get('name') == 'ER图' else 'FAIL'))

    cells = cells_parent.findall('mxCell')
    log('mxCell 总数：%d（要求 >=80：%s）' % (len(cells), 'PASS' if len(cells) >= 80 else 'FAIL'))

    # 3) 实体与字段
    by_id = {c.get('id'): c for c in cells}
    log()
    log('实体框与字段数核对（swimlane 框 + 子字段行）：')
    ok_entities = 0
    for ent, expected in EXPECTED_FIELDS.items():
        eid = 'e_%s' % ent
        present = eid in by_id and by_id[eid].get('style', '').startswith('swimlane')
        children = [c for c in cells if c.get('parent') == eid]
        ok = present and len(children) == expected
        ok_entities += 1 if ok else 0
        log('  %-14s 实体框=%-5s 字段行=%2d（期望 %2d）%s'
            % (ent, present, len(children), expected, 'PASS' if ok else 'FAIL'))
    log('  实体核对：%d/%d 通过' % (ok_entities, len(EXPECTED_FIELDS)))

    # 4) 关系线
    edges = [c for c in cells if c.get('edge') == '1']
    field_cells = {cid for cid in by_id if cid.startswith('f_')}
    log()
    log('关系线核对（source/target 必须锚定具体字段 cell，两端带基数标签）：')
    ok_edges = 0
    for e in edges:
        src, tgt = e.get('source'), e.get('target')
        labels = [c for c in cells if c.get('parent') == e.get('id')]
        anchor_ok = src in field_cells and tgt in field_cells
        mult_ok = len(labels) == 2 and {l.get('value') for l in labels} >= {'1'}
        ok = anchor_ok and mult_ok and e.get('style', '').find('ERone') >= 0
        ok_edges += 1 if ok else 0
        log('  %-18s %-24s → %-24s 基数标签=%-12s %s'
            % (e.get('id'), src, tgt, '/'.join(sorted(l.get('value') for l in labels)),
               'PASS' if ok else 'FAIL'))
    log('  关系线核对：%d/%d 条通过（期望 %d 条）' % (ok_edges, len(edges), EXPECTED_EDGES))

    # 5) 结论
    all_ok = (size > 15 * 1024 and len(cells) >= 80 and ok_entities == len(EXPECTED_FIELDS)
              and ok_edges == len(edges) == EXPECTED_EDGES)
    log()
    log('自检结论：%s' % ('全部通过：XML 合法、11 实体 93 字段、18 条字段级关系、节点数 %d、体积 %d 字节'
                          % (len(cells), size) if all_ok else '存在未通过项，需修正'))
    log('说明：该文件为 drawio 原生 XML 工程文件（非位图），可被 diagrams.net / VS Code Draw.io '
        'Integration 直接打开与编辑。')

    # 追加写入验证输出
    with open(OUTPUT, 'a', encoding='utf-8', newline='\n') as f:
        f.write('\n'.join(report) + '\n')
    print('\n>>> 自检报告已追加写入：%s' % OUTPUT)
    return 0 if all_ok else 1


if __name__ == '__main__':
    sys.exit(main())
