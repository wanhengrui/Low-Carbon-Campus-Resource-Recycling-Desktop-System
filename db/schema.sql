-- =============================================================================
-- 低碳校园资源循环流转桌面系统（GreenCampus Recycle）
-- 数据库初始化脚本：schema.sql
-- -----------------------------------------------------------------------------
-- 项目   ：《软件构造》8 周分组实验 · 迭代一（第 1-2 周：需求与设计）
-- 版本   ：v1.0.0
-- 作者   ：成员1（系统设计与数据层负责人）
-- 日期   ：2026-11-02
-- 目标库 ：SQLite 3（本机实测 sqlite3 3.53.1，JDBC 驱动 org.xerial:sqlite-jdbc:3.46.1.0）
-- 执行方式：
--   方式一（命令行）：sqlite3.exe greencampus.db ".read schema.sql"
--   方式二（Python）：
--       import sqlite3
--       con = sqlite3.connect('greencampus.db')
--       con.executescript(open('schema.sql', encoding='utf-8').read())
--   方式三（程序内）：DbUtil 初始化时读取本文件并 executescript
-- -----------------------------------------------------------------------------
-- 设计约定（与《_共享契约-实体与接口基线.md》第 2、3 节逐字一致）：
--   * 表名/字段名：小写 + 下划线；主键 INTEGER PRIMARY KEY AUTOINCREMENT
--   * 时间字段：TEXT，格式 'yyyy-MM-dd HH:mm:ss'
--   * 金额字段：REAL（单位：元）
--   * 布尔字段：INTEGER(0/1)，CHECK 限定 0/1
--   * 枚举字段：TEXT 存 Java 枚举 name()，CHECK 限定取值集合
--   * 表名 user / category / item 等若与 SQL 关键字冲突，统一使用双引号包裹
--
-- 可重复执行策略（二选一，本脚本采用"反序 DROP + 正序 CREATE"）：
--   本脚本显式按外键依赖的反序执行 DROP TABLE IF EXISTS，然后按依赖正序建表，
--   因此每次执行都会得到一个"结构全新、数据清空"的干净库；适用于本迭代的
--   初始化与回归验证。生产环境如需保留数据，应改用 CREATE TABLE IF NOT EXISTS
--   或版本化迁移脚本（本项目在 D5 第 8 节说明该取舍）。
--   建表顺序（外键依赖正序）：
--     user -> category -> item -> item_image -> favorite -> trade_message
--          -> trade_flow -> review -> credit_log -> operation_log -> system_config
-- =============================================================================

-- 每个连接都必须显式开启外键约束（SQLite 默认关闭，且该 PRAGMA 是连接级设置），
-- 程序侧 DbUtil#getConnection() 亦在获取连接后执行同一条 PRAGMA。
PRAGMA foreign_keys = ON;

-- 单机桌面场景下并发读写极少：WAL 允许"读不阻塞写、写不阻塞读"，
-- 降低统计报表导出（长查询）与业务写入相互等待的概率。该 PRAGMA 持久化在库文件中。
PRAGMA journal_mode = WAL;

-- -----------------------------------------------------------------------------
-- 0. 反序清理（保证脚本可重复执行；顺序与建表顺序严格相反）
--    category.parent_id 为自引用外键（ON DELETE RESTRICT），库中已有分类数据时直接
--    DROP TABLE 会因父行被隐式删除而触发外键约束（SQLITE_CONSTRAINT_TRIGGER）。
--    故重建阶段临时关闭外键强制，全部建表完成后于文末恢复（见第 12 节）。
-- -----------------------------------------------------------------------------
PRAGMA foreign_keys = OFF;

DROP TABLE IF EXISTS system_config;
DROP TABLE IF EXISTS operation_log;
DROP TABLE IF EXISTS credit_log;
DROP TABLE IF EXISTS review;
DROP TABLE IF EXISTS trade_flow;
DROP TABLE IF EXISTS trade_message;
DROP TABLE IF EXISTS favorite;
DROP TABLE IF EXISTS item_image;
DROP TABLE IF EXISTS item;
DROP TABLE IF EXISTS category;
DROP TABLE IF EXISTS "user";

-- -----------------------------------------------------------------------------
-- 1. user 用户表
--    职责：账号、认证、角色、信用分、登录失败锁定状态
-- -----------------------------------------------------------------------------
CREATE TABLE "user" (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,                          -- 用户ID
    username      TEXT    NOT NULL UNIQUE,                                    -- 登录名，4-20 位字母数字下划线（BR-01）
    password_hash TEXT    NOT NULL,                                           -- PBKDF2WithHmacSHA256 Base64 摘要（BR-02）
    salt          TEXT    NOT NULL,                                           -- 16 字节随机盐 Base64（BR-02）
    real_name     TEXT    NOT NULL,                                           -- 真实姓名
    student_no    TEXT    UNIQUE,                                             -- 学号/工号，8-12 位数字（BR-01）
    role          TEXT    NOT NULL DEFAULT 'STUDENT'
                          CHECK (role IN ('STUDENT','TEACHER','ADMIN')),      -- 角色
    college       TEXT,                                                       -- 学院
    contact       TEXT,                                                       -- 联系方式（手机/邮箱）
    credit_score  INTEGER NOT NULL DEFAULT 100
                          CHECK (credit_score BETWEEN 0 AND 150),             -- 信用分，初始 100（BR-04）
    status        TEXT    NOT NULL DEFAULT 'ACTIVE'
                          CHECK (status IN ('ACTIVE','FROZEN','CANCELLED')),  -- 账号状态
    fail_count    INTEGER NOT NULL DEFAULT 0,                                 -- 连续登录失败次数（BR-03）
    locked_until  TEXT,                                                       -- 锁定截止时间，失败 5 次锁 15 分钟（BR-03）
    created_at    TEXT    NOT NULL,                                           -- 注册时间
    updated_at    TEXT    NOT NULL,                                           -- 更新时间
    last_login_at TEXT                                                        -- 最近登录时间
);

-- -----------------------------------------------------------------------------
-- 2. category 分类表（两级：parent_id IS NULL 为一级分类）
-- -----------------------------------------------------------------------------
CREATE TABLE category (
    id         INTEGER PRIMARY KEY AUTOINCREMENT,                             -- 分类ID
    name       TEXT    NOT NULL,                                              -- 分类名
    parent_id  INTEGER,                                                       -- 父分类，NULL=一级分类
    sort_order INTEGER NOT NULL DEFAULT 0,                                    -- 排序号（升序展示）
    enabled    INTEGER NOT NULL DEFAULT 1
                       CHECK (enabled IN (0,1)),                             -- 是否启用：下架分类不可选
    created_at TEXT    NOT NULL,                                              -- 创建时间
    UNIQUE (parent_id, name),                                                 -- 同一父分类下分类名唯一
    CONSTRAINT fk_category_parent FOREIGN KEY (parent_id)
        REFERENCES category(id) ON DELETE RESTRICT ON UPDATE CASCADE
);
-- 说明：SQLite 的 UNIQUE 约束将 NULL 视为互不相等，因此 UNIQUE(parent_id, name)
--       无法阻止"多个同名一级分类"。此处补充部分唯一索引堵住该漏洞（NULL 分组）。
CREATE UNIQUE INDEX uq_category_root_name ON category(name) WHERE parent_id IS NULL;

-- -----------------------------------------------------------------------------
-- 3. item 闲置物品表
-- -----------------------------------------------------------------------------
CREATE TABLE item (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,                        -- 物品ID
    owner_id        INTEGER NOT NULL,                                         -- 发布者 user.id
    category_id     INTEGER NOT NULL,                                         -- 分类 category.id
    title           TEXT    NOT NULL,                                         -- 标题 2-50 字
    description     TEXT    NOT NULL,                                         -- 描述 <=500 字
    trade_type      TEXT    NOT NULL
                            CHECK (trade_type IN ('SELL','EXCHANGE','FREE')), -- 售卖/交换/赠送
    price           REAL    NOT NULL DEFAULT 0
                            CHECK (price >= 0),                               -- 期望价格（元，EXCHANGE/FREE 为 0）
    original_price  REAL    CHECK (original_price IS NULL OR original_price >= 0), -- 原价（减排估算）
    condition_level INTEGER NOT NULL DEFAULT 9
                            CHECK (condition_level BETWEEN 1 AND 10),          -- 成色 1-10 成新
    tags            TEXT,                                                     -- 标签，逗号分隔（反范式，见 D5 第 7 节）
    status          TEXT    NOT NULL DEFAULT 'PENDING'
                            CHECK (status IN ('DRAFT','PENDING','ON_SALE','LOCKED',
                                              'SOLD','OFF_SHELF','REJECTED')), -- 物品状态（默认待审核 PENDING；DRAFT 为草稿）
    view_count      INTEGER NOT NULL DEFAULT 0,                               -- 浏览数
    favorite_count  INTEGER NOT NULL DEFAULT 0,                               -- 收藏数（冗余计数）
    audit_remark    TEXT,                                                     -- 管理员审核/下架原因
    created_at      TEXT    NOT NULL,                                         -- 创建时间
    updated_at      TEXT    NOT NULL,                                         -- 更新时间
    published_at    TEXT,                                                     -- 上架时间（审核通过/显式上架时写入）
    -- 表级兜底约束（第 3 轮裁决 v1.1 §13-9）：FREE 赠送必须价格为 0，
    -- 与 Service 层校验构成"Service + DB 双层"防线，防止绕过 Service 直接写库。
    CONSTRAINT ck_item_free_price CHECK (NOT (trade_type = 'FREE' AND price <> 0)),
    CONSTRAINT fk_item_owner FOREIGN KEY (owner_id)
        REFERENCES "user"(id) ON DELETE CASCADE ON UPDATE CASCADE,
    CONSTRAINT fk_item_category FOREIGN KEY (category_id)
        REFERENCES category(id) ON DELETE RESTRICT ON UPDATE CASCADE
);

CREATE INDEX idx_item_status_category ON item(status, category_id);           -- 检索主路径
CREATE INDEX idx_item_owner           ON item(owner_id);                      -- "我的发布"
CREATE INDEX idx_item_title           ON item(title);                         -- 关键词前缀/排序辅助

-- -----------------------------------------------------------------------------
-- 4. item_image 物品图片表（只存相对路径，二进制不入库，BR-12）
-- -----------------------------------------------------------------------------
CREATE TABLE item_image (
    id         INTEGER PRIMARY KEY AUTOINCREMENT,                             -- 图片ID
    item_id    INTEGER NOT NULL,                                              -- 所属物品
    file_path  TEXT    NOT NULL,                                              -- 相对路径 data/images/{itemId}/{uuid}.jpg
    sort_order INTEGER NOT NULL DEFAULT 0,                                    -- 首图 sort_order=0
    created_at TEXT    NOT NULL,                                              -- 上传时间
    CONSTRAINT fk_image_item FOREIGN KEY (item_id)
        REFERENCES item(id) ON DELETE CASCADE ON UPDATE CASCADE
);

CREATE INDEX idx_item_image_item ON item_image(item_id, sort_order);         -- 按物品取有序图片

-- -----------------------------------------------------------------------------
-- 5. favorite 收藏表
-- -----------------------------------------------------------------------------
CREATE TABLE favorite (
    id         INTEGER PRIMARY KEY AUTOINCREMENT,                             -- 收藏ID
    user_id    INTEGER NOT NULL,                                              -- 收藏人
    item_id    INTEGER NOT NULL,                                              -- 被收藏物品
    created_at TEXT    NOT NULL,                                              -- 收藏时间
    UNIQUE (user_id, item_id),                                                -- 收藏唯一（BR-09 toggle 语义）
    CONSTRAINT fk_favorite_user FOREIGN KEY (user_id)
        REFERENCES "user"(id) ON DELETE CASCADE ON UPDATE CASCADE,
    CONSTRAINT fk_favorite_item FOREIGN KEY (item_id)
        REFERENCES item(id) ON DELETE CASCADE ON UPDATE CASCADE
);

CREATE INDEX idx_favorite_user ON favorite(user_id);                         -- "我的收藏"列表

-- -----------------------------------------------------------------------------
-- 6. trade_message 流转沟通消息表
-- -----------------------------------------------------------------------------
CREATE TABLE trade_message (
    id           INTEGER PRIMARY KEY AUTOINCREMENT,                           -- 消息ID
    item_id      INTEGER NOT NULL,                                            -- 关联物品
    from_user_id INTEGER NOT NULL,                                            -- 发送者
    to_user_id   INTEGER NOT NULL,                                            -- 接收者
    content      TEXT    NOT NULL,                                            -- 内容 <=200 字（VAL-006）
    is_read      INTEGER NOT NULL DEFAULT 0
                         CHECK (is_read IN (0,1)),                            -- 是否已读
    created_at   TEXT    NOT NULL,                                            -- 发送时间
    CONSTRAINT fk_msg_item FOREIGN KEY (item_id)
        REFERENCES item(id) ON DELETE CASCADE ON UPDATE CASCADE,
    CONSTRAINT fk_msg_from FOREIGN KEY (from_user_id)
        REFERENCES "user"(id) ON DELETE CASCADE ON UPDATE CASCADE,
    CONSTRAINT fk_msg_to FOREIGN KEY (to_user_id)
        REFERENCES "user"(id) ON DELETE CASCADE ON UPDATE CASCADE
);

CREATE INDEX idx_msg_pair ON trade_message(from_user_id, to_user_id, item_id); -- 会话查询

-- -----------------------------------------------------------------------------
-- 7. trade_flow 流转记录表（核心表）
--    业务约束 BR-05：同一物品同时最多一条进行中流转（部分唯一索引兜底）
-- -----------------------------------------------------------------------------
CREATE TABLE trade_flow (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,                          -- 流转ID
    item_id       INTEGER NOT NULL,                                           -- 物品
    seller_id     INTEGER NOT NULL,                                           -- 出让方
    buyer_id      INTEGER NOT NULL,                                           -- 受让方
    flow_type     TEXT    NOT NULL
                          CHECK (flow_type IN ('SELL','EXCHANGE','FREE')),    -- 流转方式（冗余自 item，留历史快照）
    amount        REAL    NOT NULL DEFAULT 0
                          CHECK (amount >= 0),                                -- 成交金额（元）
    status        TEXT    NOT NULL DEFAULT 'APPLYING'
                          CHECK (status IN ('APPLYING','AGREED','DONE','CANCELLED')), -- 流转状态
    apply_remark  TEXT,                                                       -- 申请留言
    cancel_reason TEXT,                                                       -- 取消原因
    created_at    TEXT    NOT NULL,                                           -- 发起时间
    finished_at   TEXT,                                                       -- 完成时间
    CONSTRAINT fk_flow_item FOREIGN KEY (item_id)
        REFERENCES item(id) ON DELETE RESTRICT ON UPDATE CASCADE,
    CONSTRAINT fk_flow_seller FOREIGN KEY (seller_id)
        REFERENCES "user"(id) ON DELETE RESTRICT ON UPDATE CASCADE,
    CONSTRAINT fk_flow_buyer FOREIGN KEY (buyer_id)
        REFERENCES "user"(id) ON DELETE RESTRICT ON UPDATE CASCADE
);

-- 部分唯一索引：仅对"进行中"的流转生效，保证同一物品最多一条 APPLYING/AGREED；
-- 已 DONE/CANCELLED 的历史记录不受限制，可保留多次流转历史。SQLite 3.8.0+ 支持。
CREATE UNIQUE INDEX uq_flow_item_active ON trade_flow(item_id)
    WHERE status IN ('APPLYING','AGREED');

CREATE INDEX idx_flow_seller ON trade_flow(seller_id);                       -- "我卖出的"
CREATE INDEX idx_flow_buyer  ON trade_flow(buyer_id);                        -- "我买到的"

-- -----------------------------------------------------------------------------
-- 8. review 评价表（BR-08：同一流转同一人只能评一次）
-- -----------------------------------------------------------------------------
CREATE TABLE review (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,                            -- 评价ID
    flow_id     INTEGER NOT NULL,                                             -- 关联流转
    reviewer_id INTEGER NOT NULL,                                             -- 评价人
    reviewee_id INTEGER NOT NULL,                                             -- 被评价人
    score       INTEGER NOT NULL CHECK (score BETWEEN 1 AND 5),               -- 评分 1-5 星
    content     TEXT,                                                         -- 评价内容 <=200 字
    created_at  TEXT    NOT NULL,                                             -- 评价时间
    UNIQUE (flow_id, reviewer_id),                                            -- 同一流转每人只能评价一次
    CONSTRAINT fk_review_flow FOREIGN KEY (flow_id)
        REFERENCES trade_flow(id) ON DELETE CASCADE ON UPDATE CASCADE,
    CONSTRAINT fk_review_reviewer FOREIGN KEY (reviewer_id)
        REFERENCES "user"(id) ON DELETE CASCADE ON UPDATE CASCADE,
    CONSTRAINT fk_review_reviewee FOREIGN KEY (reviewee_id)
        REFERENCES "user"(id) ON DELETE CASCADE ON UPDATE CASCADE
);

CREATE INDEX idx_review_reviewee ON review(reviewee_id);                     -- 信誉页/平均分

-- -----------------------------------------------------------------------------
-- 9. credit_log 信用分变更流水表（BR-04：每次变更留快照）
-- -----------------------------------------------------------------------------
CREATE TABLE credit_log (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,                            -- 流水ID
    user_id     INTEGER NOT NULL,                                             -- 用户
    flow_id     INTEGER,                                                      -- 关联流转，可为 NULL
    delta       INTEGER NOT NULL,                                             -- 变化量（+2/-5...）
    score_after INTEGER NOT NULL CHECK (score_after BETWEEN 0 AND 150),       -- 变更后分数（快照）
    reason      TEXT    NOT NULL,                                             -- 变更原因
    created_at  TEXT    NOT NULL,                                             -- 时间
    CONSTRAINT fk_credit_user FOREIGN KEY (user_id)
        REFERENCES "user"(id) ON DELETE CASCADE ON UPDATE CASCADE,
    CONSTRAINT fk_credit_flow FOREIGN KEY (flow_id)
        REFERENCES trade_flow(id) ON DELETE SET NULL ON UPDATE CASCADE
);

CREATE INDEX idx_credit_user ON credit_log(user_id, created_at);             -- 信用分历史

-- -----------------------------------------------------------------------------
-- 10. operation_log 关键操作日志表（BR-11：仅追加，不修改）
-- -----------------------------------------------------------------------------
CREATE TABLE operation_log (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,                            -- 日志ID
    operator_id INTEGER,                                                      -- 操作人，NULL=系统
    operation   TEXT    NOT NULL,                                             -- 操作类型 LOGIN/PUBLISH_ITEM/CONFIRM_FLOW/OFF_SHELF...
    target_type TEXT,                                                         -- 对象类型 ITEM/USER/FLOW/CATEGORY
    target_id   INTEGER,                                                      -- 对象ID
    detail      TEXT,                                                         -- 详情（JSON 或文本）
    ip          TEXT,                                                         -- 来源（桌面端记录 hostname）
    created_at  TEXT    NOT NULL,                                             -- 时间
    CONSTRAINT fk_oplog_operator FOREIGN KEY (operator_id)
        REFERENCES "user"(id) ON DELETE SET NULL ON UPDATE CASCADE
);

CREATE INDEX idx_oplog_operator ON operation_log(operator_id, created_at);   -- 审计查询

-- -----------------------------------------------------------------------------
-- 11. system_config 系统配置表（预置键见 seed-data.sql；键唯一）
-- -----------------------------------------------------------------------------
CREATE TABLE system_config (
    id           INTEGER PRIMARY KEY AUTOINCREMENT,                           -- 配置ID
    config_key   TEXT    NOT NULL UNIQUE,                                     -- 键
    config_value TEXT    NOT NULL,                                            -- 值
    description  TEXT,                                                        -- 说明
    updated_at   TEXT    NOT NULL                                             -- 更新时间
);

-- -----------------------------------------------------------------------------
-- 12. 恢复外键强制（第 0 节为支持可重复执行而临时关闭）
-- -----------------------------------------------------------------------------
PRAGMA foreign_keys = ON;
