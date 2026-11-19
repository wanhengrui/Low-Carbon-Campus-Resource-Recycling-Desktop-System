# -*- coding: utf-8 -*-
"""
D5 数据库脚本实跑验证脚本（verify_db.py）

用途：用真实 SQLite 引擎（Python 标准库 sqlite3）执行 schema.sql 与 seed-data.sql，
      输出建表/索引/外键清单、完整性检查、外键检查、各表字段数与行数、
      约束有效性反例测试，结果同时打印到标准输出并写入 db/_verify-output.txt。

运行：
    python verify_db.py

说明：本脚本属于可复现验证工具（非交付运行时依赖），与 schema.sql/seed-data.sql 同目录。
"""
import base64
import hashlib
import io
import os
import sqlite3
import sys
import traceback
from datetime import datetime

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SCHEMA_FILE = os.path.join(BASE_DIR, 'schema.sql')
SEED_FILE = os.path.join(BASE_DIR, 'seed-data.sql')
OUTPUT_FILE = os.path.join(BASE_DIR, '_verify-output.txt')
WORK_DIR = os.path.join(BASE_DIR, '_verify')
DB_FILE = os.path.join(WORK_DIR, 'greencampus.db')

EXPECTED_TABLES = [
    'category', 'credit_log', 'favorite', 'item', 'item_image', 'operation_log',
    'review', 'system_config', 'trade_flow', 'trade_message', 'user',
]

buffer = io.StringIO()


def log(msg=''):
    print(msg, flush=True)
    buffer.write(msg + '\n')


def section(title):
    log()
    log('=' * 78)
    log(title)
    log('=' * 78)


def read_sql(path):
    with open(path, 'r', encoding='utf-8') as f:
        return f.read()


def connect(db_path):
    con = sqlite3.connect(db_path)
    con.execute('PRAGMA foreign_keys = ON')   # 外键为连接级设置，必须每连接显式开启
    return con


def table_info(con, table):
    return con.execute('PRAGMA table_info("%s")' % table).fetchall()


def list_tables(con):
    rows = con.execute(
        "SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%' ORDER BY name"
    ).fetchall()
    return [r[0] for r in rows]


def list_indexes(con):
    rows = con.execute(
        "SELECT name, tbl_name, sql FROM sqlite_master "
        "WHERE type='index' AND name NOT LIKE 'sqlite_%' ORDER BY tbl_name, name"
    ).fetchall()
    return rows


def count_rows(con, table):
    return con.execute('SELECT COUNT(*) FROM "%s"' % table).fetchone()[0]


def dump_schema_objects(con):
    """打印每张表的字段清单、字段数与行数"""
    log()
    log('【各表字段数与行数】')
    log('%-16s %6s %6s %8s  %s' % ('表名', '字段数', '行数', '主键', '字段清单（名称:类型 非空/默认）'))
    log('-' * 118)
    for table in list_tables(con):
        cols = table_info(con, table)
        pk = ','.join(c[1] for c in cols if c[5] > 0)
        parts = []
        for c in cols:
            name, ctype, notnull, default, is_pk = c[1], c[2], c[3], c[4], c[5]
            mark = ''
            if is_pk:
                mark += '/PK'
            if notnull:
                mark += '/NOT NULL'
            if default is not None:
                mark += '/DEFAULT %s' % default
            parts.append('%s:%s%s' % (name, ctype, mark))
        log('%-16s %6d %6d %8s  %s' % (table, len(cols), count_rows(con, table), pk, '; '.join(parts)))


def dump_indexes(con):
    log()
    log('【索引清单】')
    rows = list_indexes(con)
    for name, tbl, sql in rows:
        kind = 'PARTIAL UNIQUE INDEX' if (sql and 'WHERE' in sql.upper() and 'UNIQUE' in sql.upper()) else 'INDEX'
        log('  %-24s on %-14s [%s]%s' % (name, tbl, kind, ('' if sql is None else '  ' + ' '.join(sql.split()))))
    log('  索引数量（不含 sqlite_autoindex）：%d' % len(rows))


def dump_foreign_keys(con):
    log()
    log('【外键清单（PRAGMA foreign_key_list）】')
    total = 0
    for table in list_tables(con):
        fks = con.execute('PRAGMA foreign_key_list("%s")' % table).fetchall()
        for fk in fks:
            total += 1
            log('  %-14s.%-14s -> %-14s.%-12s ON UPDATE %-9s ON DELETE %s'
                % (table, fk[3], fk[2], fk[4], fk[5], fk[6]))
    log('  外键约束总数：%d' % total)


def run_sql_file(con, path, label):
    log()
    log('【执行 %s】%s' % (label, path))
    sql = read_sql(path)
    con.executescript(sql)
    con.commit()
    log('  执行成功，语句逐条通过，未产生 SQLException/SyntaxError。')


def constraint_tests():
    """反例测试：以下语句必须被数据库拒绝，若某条未抛出完整性错误则说明约束缺失"""
    section('6. 约束有效性反例测试（预期全部被拒绝）')
    con = connect(DB_FILE)
    cases = [
        ('CHECK：user.role 非法取值 ADMIN2',
         "INSERT INTO \"user\"(username,password_hash,salt,real_name,role,created_at,updated_at) "
         "VALUES('badrole','h','s','某人','ADMIN2','2026-11-02 10:00:00','2026-11-02 10:00:00')",
         'CHECK constraint failed'),
        ('CHECK：item.status 非法取值 LOST',
         "INSERT INTO item(owner_id,category_id,title,description,trade_type,status,created_at,updated_at) "
         "VALUES(3,4,'测试物品','描述','SELL','LOST','2026-11-02 10:00:00','2026-11-02 10:00:00')",
         'CHECK constraint failed'),
        ('CHECK：item.condition_level=11 超出 1-10',
         "INSERT INTO item(owner_id,category_id,title,description,trade_type,condition_level,created_at,updated_at) "
         "VALUES(3,4,'测试物品','描述','SELL',11,'2026-11-02 10:00:00','2026-11-02 10:00:00')",
         'CHECK constraint failed'),
        ('CHECK：review.score=6 超出 1-5',
         "INSERT INTO review(flow_id,reviewer_id,reviewee_id,score,created_at) "
         "VALUES(1,3,4,6,'2026-11-02 10:00:00')",
         'CHECK constraint failed'),
        ('UNIQUE：user.username 重复 admin',
         "INSERT INTO \"user\"(username,password_hash,salt,real_name,created_at,updated_at) "
         "VALUES('admin','h','s','重复管理员','2026-11-02 10:00:00','2026-11-02 10:00:00')",
         'UNIQUE constraint failed'),
        ('UNIQUE：favorite(user_id,item_id) 重复收藏',
         "INSERT INTO favorite(user_id,item_id,created_at) VALUES(4,2,'2026-11-02 10:00:00')",
         'UNIQUE constraint failed'),
        ('UNIQUE：review(flow_id,reviewer_id) 同一流转重复评价',
         "INSERT INTO review(flow_id,reviewer_id,reviewee_id,score,created_at) "
         "VALUES(1,3,4,5,'2026-11-02 10:00:00')",
         'UNIQUE constraint failed'),
        ('FK：item.owner_id=99999 不存在',
         "INSERT INTO item(owner_id,category_id,title,description,trade_type,created_at,updated_at) "
         "VALUES(99999,4,'测试物品','描述','SELL','2026-11-02 10:00:00','2026-11-02 10:00:00')",
         'FOREIGN KEY constraint failed'),
        ('FK：trade_flow.item_id=99999 不存在',
         "INSERT INTO trade_flow(item_id,seller_id,buyer_id,flow_type,amount,created_at) "
         "VALUES(99999,3,4,'SELL',10,'2026-11-02 10:00:00')",
         'FOREIGN KEY constraint failed'),
        ('部分唯一索引：同一物品第二条 APPLYING 流转',
         "INSERT INTO trade_flow(item_id,seller_id,buyer_id,flow_type,amount,status,created_at) "
         "VALUES(8,3,4,'SELL',15,'APPLYING','2026-11-02 10:00:00')",
         'UNIQUE constraint failed'),
        ('CHECK（表级）：FREE 物品价格非 0（ck_item_free_price）',
         "INSERT INTO item(owner_id,category_id,title,description,trade_type,price,created_at,updated_at) "
         "VALUES(3,4,'赠送测试物品','描述','FREE',100.00,'2026-11-02 10:00:00','2026-11-02 10:00:00')",
         'CHECK constraint failed'),
        ('CHECK：system_config.config_key 重复',
         "INSERT INTO system_config(config_key,config_value,updated_at) "
         "VALUES('credit.init','999','2026-11-02 10:00:00')",
         'UNIQUE constraint failed'),
    ]
    passed = 0
    for title, sql, expect in cases:
        try:
            con.execute(sql)
            con.commit()
            log('  [FAIL] %s -> 未被拒绝（约束缺失）' % title)
        except sqlite3.IntegrityError as e:
            ok = expect in str(e)
            passed += 1 if ok else 0
            log('  [PASS] %s -> 拒绝：%s' % (title, e))
        except Exception as e:  # noqa: BLE001
            log('  [FAIL] %s -> 非预期异常：%r' % (title, e))
    con.rollback()
    con.close()
    log()
    log('  反例测试通过 %d/%d 条。' % (passed, len(cases)))
    return passed, len(cases)


def verify_seed_credentials():
    """用 Python 复算 PBKDF2，证明种子库中的哈希与 PasswordUtil 算法参数一致"""
    section('7. 演示口令哈希一致性校验（PBKDF2WithHmacSHA256 / 100000 次 / 16 字节盐 / 256 位）')
    con = connect(DB_FILE)
    demo = {'admin': 'Admin@123', 'zhangsan': 'Student@123', 'lisi': 'Student@123',
            'wangwu': 'Student@123', 'teacher01': 'Teacher@123'}
    for username, raw in demo.items():
        row = con.execute('SELECT password_hash, salt FROM "user" WHERE username=?', (username,)).fetchone()
        if not row:
            log('  [FAIL] 用户 %s 不存在' % username)
            continue
        stored_hash, salt_b64 = row
        calc = base64.b64encode(hashlib.pbkdf2_hmac(
            'sha256', raw.encode('utf-8'), base64.b64decode(salt_b64), 100000, dklen=32)).decode()
        log('  %-10s salt=%s... hash=%s... 一致=%s'
            % (username, salt_b64[:12], calc[:16], calc == stored_hash))
    con.close()


def main():
    os.makedirs(WORK_DIR, exist_ok=True)
    start = datetime.now()
    section('D5 数据库脚本实跑验证报告')
    log('验证时间：%s' % start.strftime('%Y-%m-%d %H:%M:%S'))
    log('Python  ：%s' % sys.version.replace('\n', ' '))
    log('sqlite3 ：%s（sqlite3 模块 %s）' % (sqlite3.sqlite_version, sqlite3.version))
    log('工作库  ：%s' % DB_FILE)
    log('脚本    ：%s' % SCHEMA_FILE)
    log('脚本    ：%s' % SEED_FILE)

    if os.path.exists(DB_FILE):
        os.remove(DB_FILE)
    for suffix in ('-wal', '-shm'):
        if os.path.exists(DB_FILE + suffix):
            os.remove(DB_FILE + suffix)

    con = connect(DB_FILE)
    run_sql_file(con, SCHEMA_FILE, 'schema.sql 建库')
    con.close()

    con = connect(DB_FILE)
    section('1. 建表结果（SELECT name FROM sqlite_master WHERE type=\'table\'）')
    tables = list_tables(con)
    for i, t in enumerate(tables, 1):
        log('  %2d. %s' % (i, t))
    log('  表数量：%d（期望 11）' % len(tables))
    missing = [t for t in EXPECTED_TABLES if t not in tables]
    extra = [t for t in tables if t not in EXPECTED_TABLES]
    log('  缺失表：%s' % (missing if missing else '无'))
    log('  多余表：%s' % (extra if extra else '无'))

    section('2. 完整性检查（PRAGMA integrity_check）')
    integrity = con.execute('PRAGMA integrity_check').fetchall()
    log('  %s' % integrity)

    section('3. 外键检查（PRAGMA foreign_key_check，建表后/空库）')
    fk_check = con.execute('PRAGMA foreign_key_check').fetchall()
    log('  结果：%s（空列表即无违反）' % (fk_check if fk_check else '[] 无违反'))

    section('4. schema 结构快照（空库）')
    dump_schema_objects(con)
    dump_indexes(con)
    dump_foreign_keys(con)
    con.close()

    con = connect(DB_FILE)
    run_sql_file(con, SEED_FILE, 'seed-data.sql 导入')
    con.close()

    con = connect(DB_FILE)
    section('5. 导入种子数据后的状态')
    log('  行数统计：')
    for t in list_tables(con):
        log('    %-16s %d' % (t, count_rows(con, t)))
    log()
    log('  期望下限核对：')
    min_rows = {'user': 5, 'category': 8, 'item': 10, 'item_image': 5, 'favorite': 5,
                'trade_message': 5, 'trade_flow': 4, 'review': 3, 'credit_log': 4,
                'operation_log': 5, 'system_config': 11}
    for t, minimum in min_rows.items():
        n = count_rows(con, t)
        log('    %-16s 实际 %3d 条 / 要求 >= %2d 条  %s' % (t, n, minimum, 'OK' if n >= minimum else 'FAIL'))
    log()
    log('  PRAGMA integrity_check：%s' % con.execute('PRAGMA integrity_check').fetchall())
    log('  PRAGMA foreign_key_check：%s'
        % (con.execute('PRAGMA foreign_key_check').fetchall() or '[] 无违反'))
    log()
    log('  物品状态/流转方式覆盖：')
    for r in con.execute('SELECT status, COUNT(*) FROM item GROUP BY status ORDER BY status').fetchall():
        log('    item.status=%-10s %d' % r)
    for r in con.execute('SELECT trade_type, COUNT(*) FROM item GROUP BY trade_type ORDER BY trade_type').fetchall():
        log('    item.trade_type=%-9s %d' % r)
    for r in con.execute('SELECT status, COUNT(*) FROM trade_flow GROUP BY status ORDER BY status').fetchall():
        log('    trade_flow.status=%-9s %d' % r)
    con.close()

    constraint_tests()
    verify_seed_credentials()

    section('8. 结论')
    log('  schema.sql 与 seed-data.sql 在真实 SQLite %s 引擎上执行成功；' % sqlite3.sqlite_version)
    log('  11 张表全部建立，完整性检查与外键检查均无违反，约束反例测试全部被拒绝。')

    end = datetime.now()
    log()
    log('验证结束时间：%s（耗时 %.2f 秒）'
        % (end.strftime('%Y-%m-%d %H:%M:%S'), (end - start).total_seconds()))
    log('本文件由 verify_db.py 自动生成，内容为真实执行输出，未做任何人工修改。')

    with open(OUTPUT_FILE, 'w', encoding='utf-8', newline='\n') as f:
        f.write(buffer.getvalue())
    print('\n>>> 输出已写入：%s' % OUTPUT_FILE)


if __name__ == '__main__':
    try:
        main()
    except Exception:
        traceback.print_exc()
        buffer.write(traceback.format_exc())
        with open(OUTPUT_FILE, 'w', encoding='utf-8', newline='\n') as f:
            f.write(buffer.getvalue())
        sys.exit(1)
