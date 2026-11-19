# -*- coding: utf-8 -*-
"""D7 生成器 part1：pom.xml、logback.xml、11 个实体、5 个枚举、6 个 DTO。"""
import os

BASE = r'C:\Users\wanhe\Desktop\软件构造\迭代一-成员1\code\green-campus'
JAVA = os.path.join(BASE, 'src', 'main', 'java', 'edu', 'campus', 'recycle')
RES = os.path.join(BASE, 'src', 'main', 'resources')


def write(rel, content):
    path = os.path.join(BASE, rel)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'w', encoding='utf-8', newline='\n') as f:
        f.write(content)
    print('  + %-70s %5d B' % (rel, len(content.encode('utf-8'))))


# --------------------------------------------------------------------------
# pom.xml
# --------------------------------------------------------------------------
POM = '''<?xml version="1.0" encoding="UTF-8"?>
<project xmlns="http://maven.apache.org/POM/4.0.0"
         xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
         xsi:schemaLocation="http://maven.apache.org/POM/4.0.0 http://maven.apache.org/xsd/maven-4.0.0.xsd">
    <modelVersion>4.0.0</modelVersion>

    <groupId>edu.campus</groupId>
    <artifactId>green-campus</artifactId>
    <version>1.0.0</version>
    <packaging>jar</packaging>

    <name>green-campus</name>
    <description>校园闲置物品循环流转平台（软件构造 迭代一）</description>

    <properties>
        <project.build.sourceEncoding>UTF-8</project.build.sourceEncoding>
        <project.reporting.outputEncoding>UTF-8</project.reporting.outputEncoding>
        <maven.compiler.release>17</maven.compiler.release>
        <sqlite-jdbc.version>3.46.1.0</sqlite-jdbc.version>
        <junit-jupiter.version>5.10.2</junit-jupiter.version>
        <logback.version>1.5.6</logback.version>
        <main.class>edu.campus.recycle.Main</main.class>
    </properties>

    <dependencies>
        <!-- SQLite JDBC 驱动（含各平台原生库） -->
        <dependency>
            <groupId>org.xerial</groupId>
            <artifactId>sqlite-jdbc</artifactId>
            <version>${sqlite-jdbc.version}</version>
        </dependency>

        <!-- 日志后端：logback-classic + slf4j-api -->
        <dependency>
            <groupId>ch.qos.logback</groupId>
            <artifactId>logback-classic</artifactId>
            <version>${logback.version}</version>
        </dependency>

        <!-- 单元测试 -->
        <dependency>
            <groupId>org.junit.jupiter</groupId>
            <artifactId>junit-jupiter</artifactId>
            <version>${junit-jupiter.version}</version>
            <scope>test</scope>
        </dependency>
    </dependencies>

    <build>
        <finalName>green-campus-${project.version}</finalName>
        <plugins>
            <plugin>
                <groupId>org.apache.maven.plugins</groupId>
                <artifactId>maven-compiler-plugin</artifactId>
                <version>3.13.0</version>
                <configuration>
                    <release>${maven.compiler.release}</release>
                    <encoding>UTF-8</encoding>
                </configuration>
            </plugin>

            <plugin>
                <groupId>org.apache.maven.plugins</groupId>
                <artifactId>maven-surefire-plugin</artifactId>
                <version>3.2.5</version>
                <configuration>
                    <argLine>-Dfile.encoding=UTF-8</argLine>
                </configuration>
            </plugin>

            <plugin>
                <groupId>org.apache.maven.plugins</groupId>
                <artifactId>maven-jar-plugin</artifactId>
                <version>3.4.1</version>
                <configuration>
                    <archive>
                        <manifest>
                            <mainClass>${main.class}</mainClass>
                        </manifest>
                    </archive>
                </configuration>
            </plugin>

            <!-- 可执行 fat jar：java -jar green-campus-1.0.0.jar -->
            <plugin>
                <groupId>org.apache.maven.plugins</groupId>
                <artifactId>maven-shade-plugin</artifactId>
                <version>3.5.2</version>
                <executions>
                    <execution>
                        <phase>package</phase>
                        <goals>
                            <goal>shade</goal>
                        </goals>
                        <configuration>
                            <createDependencyReducedPom>false</createDependencyReducedPom>
                            <filters>
                                <filter>
                                    <artifact>*:*</artifact>
                                    <excludes>
                                        <exclude>META-INF/*.SF</exclude>
                                        <exclude>META-INF/*.DSA</exclude>
                                        <exclude>META-INF/*.RSA</exclude>
                                    </excludes>
                                </filter>
                            </filters>
                            <transformers>
                                <transformer implementation="org.apache.maven.plugins.shade.resource.ManifestResourceTransformer">
                                    <mainClass>${main.class}</mainClass>
                                </transformer>
                            </transformers>
                        </configuration>
                    </execution>
                </executions>
            </plugin>
        </plugins>
    </build>
</project>
'''
write('pom.xml', POM)

# --------------------------------------------------------------------------
# logback.xml
# --------------------------------------------------------------------------
LOGBACK = '''<?xml version="1.0" encoding="UTF-8"?>
<configuration>
    <property name="LOG_PATTERN"
              value="%d{yyyy-MM-dd HH:mm:ss.SSS} [%thread] %-5level %logger{36} - %msg%n"/>
    <property name="LOG_DIR" value="logs"/>

    <appender name="CONSOLE" class="ch.qos.logback.core.ConsoleAppender">
        <encoder>
            <pattern>${LOG_PATTERN}</pattern>
            <charset>UTF-8</charset>
        </encoder>
    </appender>

    <appender name="FILE" class="ch.qos.logback.core.rolling.RollingFileAppender">
        <file>${LOG_DIR}/green-campus.log</file>
        <rollingPolicy class="ch.qos.logback.core.rolling.TimeBasedRollingPolicy">
            <fileNamePattern>${LOG_DIR}/green-campus.%d{yyyy-MM-dd}.log</fileNamePattern>
            <maxHistory>30</maxHistory>
        </rollingPolicy>
        <encoder>
            <pattern>${LOG_PATTERN}</pattern>
            <charset>UTF-8</charset>
        </encoder>
    </appender>

    <logger name="edu.campus.recycle" level="DEBUG"/>
    <logger name="edu.campus.recycle.dao" level="DEBUG"/>

    <root level="INFO">
        <appender-ref ref="CONSOLE"/>
        <appender-ref ref="FILE"/>
    </root>
</configuration>
'''
write('src/main/resources/logback.xml', LOGBACK)

# --------------------------------------------------------------------------
# 实体（11 个）
# 字段三元组：(Java 类型, 属性名, 注释)
# --------------------------------------------------------------------------
ENTITIES = [
    ('User', 'user', '3.1', '用户', [
        ('Integer', 'id', '用户ID（主键）'),
        ('String', 'username', '登录名，4–20 位字母数字下划线'),
        ('String', 'passwordHash', 'PBKDF2WithHmacSHA256 Base64 摘要'),
        ('String', 'salt', '16 字节随机盐 Base64'),
        ('String', 'realName', '真实姓名'),
        ('String', 'studentNo', '学号/工号，8–12 位数字'),
        ('String', 'role', '角色：STUDENT/TEACHER/ADMIN'),
        ('String', 'college', '学院'),
        ('String', 'contact', '联系方式（手机/邮箱）'),
        ('Integer', 'creditScore', '信用分，0–150，默认 100'),
        ('String', 'status', '账号状态：ACTIVE/FROZEN/CANCELLED'),
        ('Integer', 'failCount', '连续登录失败次数'),
        ('LocalDateTime', 'lockedUntil', '锁定截止时间（失败 5 次锁 15 分钟）'),
        ('LocalDateTime', 'createdAt', '注册时间'),
        ('LocalDateTime', 'updatedAt', '更新时间'),
        ('LocalDateTime', 'lastLoginAt', '最近登录时间'),
    ]),
    ('Category', 'category', '3.2', '分类', [
        ('Integer', 'id', '分类ID（主键）'),
        ('String', 'name', '分类名'),
        ('Integer', 'parentId', '父分类ID，NULL 表示一级分类（FK→category.id）'),
        ('Integer', 'sortOrder', '排序值，升序展示'),
        ('Boolean', 'enabled', '是否启用（下架分类不可选）'),
        ('LocalDateTime', 'createdAt', '创建时间'),
    ]),
    ('Item', 'item', '3.3', '闲置物品', [
        ('Integer', 'id', '物品ID（主键）'),
        ('Integer', 'ownerId', '发布者（FK→user.id）'),
        ('Integer', 'categoryId', '分类（FK→category.id）'),
        ('String', 'title', '标题，2–50 字'),
        ('String', 'description', '描述，≤500 字'),
        ('String', 'tradeType', '交易方式：SELL/EXCHANGE/FREE'),
        ('BigDecimal', 'price', '期望价格，EXCHANGE/FREE 为 0'),
        ('BigDecimal', 'originalPrice', '原价（用于减排估算）'),
        ('Integer', 'conditionLevel', '成色 1–10 成新'),
        ('String', 'tags', '标签，逗号分隔（反范式存储，见 D5 第 7 章）'),
        ('String', 'status', '物品状态：DRAFT/PENDING/ON_SALE/LOCKED/SOLD/OFF_SHELF/REJECTED'),
        ('Integer', 'viewCount', '浏览数'),
        ('Integer', 'favoriteCount', '收藏数'),
        ('String', 'auditRemark', '管理员审核/下架原因'),
        ('LocalDateTime', 'createdAt', '创建时间'),
        ('LocalDateTime', 'updatedAt', '更新时间'),
        ('LocalDateTime', 'publishedAt', '上架时间'),
    ]),
    ('ItemImage', 'item_image', '3.4', '物品图片', [
        ('Integer', 'id', '图片ID（主键）'),
        ('Integer', 'itemId', '所属物品（FK→item.id）'),
        ('String', 'filePath', '相对路径 data/images/{itemId}/{uuid}.jpg'),
        ('Integer', 'sortOrder', '排序，首图 sort_order=0'),
        ('LocalDateTime', 'createdAt', '上传时间'),
    ]),
    ('Favorite', 'favorite', '3.5', '收藏', [
        ('Integer', 'id', '收藏ID（主键）'),
        ('Integer', 'userId', '收藏人（FK→user.id）'),
        ('Integer', 'itemId', '物品（FK→item.id）'),
        ('LocalDateTime', 'createdAt', '收藏时间'),
    ]),
    ('TradeMessage', 'trade_message', '3.6', '流转沟通消息', [
        ('Integer', 'id', '消息ID（主键）'),
        ('Integer', 'itemId', '关联物品（FK→item.id）'),
        ('Integer', 'fromUserId', '发送者（FK→user.id）'),
        ('Integer', 'toUserId', '接收者（FK→user.id）'),
        ('String', 'content', '内容，≤300 字'),
        ('Boolean', 'isRead', '是否已读'),
        ('LocalDateTime', 'createdAt', '发送时间'),
    ]),
    ('TradeFlow', 'trade_flow', '3.7', '流转记录（核心表）', [
        ('Integer', 'id', '流转ID（主键）'),
        ('Integer', 'itemId', '物品（FK→item.id）'),
        ('Integer', 'sellerId', '出让方（FK→user.id）'),
        ('Integer', 'buyerId', '受让方（FK→user.id）'),
        ('String', 'flowType', '流转方式：SELL/EXCHANGE/FREE（冗余自 item，历史快照）'),
        ('BigDecimal', 'amount', '成交金额'),
        ('String', 'status', '流转状态：APPLYING/AGREED/DONE/CANCELLED'),
        ('String', 'applyRemark', '申请留言'),
        ('String', 'cancelReason', '取消原因'),
        ('LocalDateTime', 'createdAt', '发起时间'),
        ('LocalDateTime', 'finishedAt', '完成时间'),
    ]),
    ('Review', 'review', '3.8', '评价', [
        ('Integer', 'id', '评价ID（主键）'),
        ('Integer', 'flowId', '关联流转（FK→trade_flow.id）'),
        ('Integer', 'reviewerId', '评价人（FK→user.id）'),
        ('Integer', 'revieweeId', '被评价人（FK→user.id）'),
        ('Integer', 'score', '评分 1–5 星'),
        ('String', 'content', '评价内容，≤200 字'),
        ('LocalDateTime', 'createdAt', '评价时间'),
    ]),
    ('CreditLog', 'credit_log', '3.9', '信用分变更流水', [
        ('Integer', 'id', '流水ID（主键）'),
        ('Integer', 'userId', '用户（FK→user.id）'),
        ('Integer', 'flowId', '关联流转（FK→trade_flow.id，可空）'),
        ('Integer', 'delta', '变化量（+2/-5…）'),
        ('Integer', 'scoreAfter', '变更后分数快照，0–150'),
        ('String', 'reason', '变更原因'),
        ('LocalDateTime', 'createdAt', '变更时间'),
    ]),
    ('OperationLog', 'operation_log', '3.10', '关键操作日志', [
        ('Integer', 'id', '日志ID（主键）'),
        ('Integer', 'operatorId', '操作人（FK→user.id，NULL=系统）'),
        ('String', 'operation', '操作类型：LOGIN/PUBLISH_ITEM/CONFIRM_FLOW/OFF_SHELF…'),
        ('String', 'targetType', '对象类型：ITEM/USER/FLOW/CATEGORY'),
        ('Integer', 'targetId', '对象ID'),
        ('String', 'detail', '详情（JSON 或文本）'),
        ('String', 'ip', '来源（桌面端记录 hostname）'),
        ('LocalDateTime', 'createdAt', '操作时间'),
    ]),
    ('SystemConfig', 'system_config', '3.11', '系统配置', [
        ('Integer', 'id', '配置ID（主键）'),
        ('String', 'configKey', '配置键'),
        ('String', 'configValue', '配置值'),
        ('String', 'description', '配置说明'),
        ('LocalDateTime', 'updatedAt', '更新时间'),
    ]),
]

for cls, table, sec, cn, fields in ENTITIES:
    imports = []
    types = {t for t, _, _ in fields}
    if 'LocalDateTime' in types:
        imports.append('import java.time.LocalDateTime;')
    if 'BigDecimal' in types:
        imports.append('import java.math.BigDecimal;')
    imports.sort()

    lines = []
    lines.append('package edu.campus.recycle.entity;')
    lines.append('')
    if imports:
        lines.extend(imports)
        lines.append('')
    lines.append('/**')
    lines.append(' * %s实体，与数据库表 {@code %s} 一一对应（契约第 %s 节，字段不得增删）。' % (cn, table, sec))
    lines.append(' *')
    lines.append(' * <p>字段名由表字段下划线形式转驼峰，金额使用 {@link java.math.BigDecimal}，')
    lines.append(' * 时间使用 {@link java.time.LocalDateTime}，布尔语义字段使用 {@link Boolean}。</p>')
    lines.append(' */')
    lines.append('public class %s {' % cls)
    lines.append('')
    for t, n, c in fields:
        lines.append('    /** %s */' % c)
        lines.append('    private %s %s;' % (t, n))
        lines.append('')
    lines.append('    /** 无参构造器，供 DAO 与框架反射使用。 */')
    lines.append('    public %s() {' % cls)
    lines.append('    }')
    lines.append('')
    params = ', '.join('%s %s' % (t, n) for t, n, _ in fields)
    lines.append('    /** 全参构造器。 */')
    lines.append('    public %s(%s) {' % (cls, params))
    for t, n, _ in fields:
        lines.append('        this.%s = %s;' % (n, n))
    lines.append('    }')
    lines.append('')
    for t, n, c in fields:
        cap = n[0].upper() + n[1:]
        lines.append('    public %s get%s() {' % (t, cap))
        lines.append('        return %s;' % n)
        lines.append('    }')
        lines.append('')
        lines.append('    public void set%s(%s %s) {' % (cap, t, n))
        lines.append('        this.%s = %s;' % (n, n))
        lines.append('    }')
        lines.append('')
    # toString：排除敏感字段
    sensitive = {'passwordHash', 'salt'}
    parts = []
    for t, n, _ in fields:
        if n in sensitive:
            parts.append('"%s=<hidden>"' % n)
        elif t == 'String':
            parts.append('"%s=" + %s' % (n, n))
        else:
            parts.append('"%s=" + %s' % (n, n))
    joined = ' + ", " + '.join(parts)
    lines.append('    @Override')
    lines.append('    public String toString() {')
    lines.append('        return "%s{" + %s + \'}\';' % (cls, joined))
    lines.append('    }')
    lines.append('}')
    lines.append('')
    write(os.path.join('src', 'main', 'java', 'edu', 'campus', 'recycle', 'entity', cls + '.java'), '\n'.join(lines))

# --------------------------------------------------------------------------
# 枚举（5 个）
# --------------------------------------------------------------------------
ENUMS = [
    ('Role', '用户角色，对应 {@code user.role} 的 CHECK 取值。',
     [('STUDENT', '学生'), ('TEACHER', '教师'), ('ADMIN', '管理员')]),
    ('UserStatus', '账号状态，对应 {@code user.status} 的 CHECK 取值。',
     [('ACTIVE', '正常'), ('FROZEN', '已冻结'), ('CANCELLED', '已注销')]),
    ('TradeType', '交易方式，对应 {@code item.trade_type} / {@code trade_flow.flow_type}。',
     [('SELL', '售卖'), ('EXCHANGE', '交换'), ('FREE', '赠送')]),
    ('ItemStatus', '物品状态，对应 {@code item.status} 的 CHECK 取值（7 态）。',
     [('DRAFT', '草稿'), ('PENDING', '待审核'), ('ON_SALE', '在售'), ('LOCKED', '交易中'),
      ('SOLD', '已成交'), ('OFF_SHELF', '已下架'), ('REJECTED', '审核驳回')]),
    ('FlowStatus', '流转状态，对应 {@code trade_flow.status} 的 CHECK 取值。',
     [('APPLYING', '申请中'), ('AGREED', '已同意'), ('DONE', '已完成'), ('CANCELLED', '已取消')]),
]

for name, doc, values in ENUMS:
    lines = []
    lines.append('package edu.campus.recycle.entity;')
    lines.append('')
    lines.append('/**')
    lines.append(' * %s' % doc)
    lines.append(' *')
    lines.append(' * <p>枚举 {@code code()} 与数据库 TEXT 列取值逐字符一致，数据库写入统一使用')
    lines.append(' * {@link #getCode()}，读取统一使用 {@link #fromCode(String)} 转换。</p>')
    lines.append(' */')
    lines.append('public enum %s {' % name)
    lines.append('')
    body = []
    for code, label in values:
        body.append('    %s("%s")' % (code, label))
    lines.append(',\n'.join(body) + ';')
    lines.append('')
    lines.append('    private final String label;')
    lines.append('')
    lines.append('    %s(String label) {' % name)
    lines.append('        this.label = label;')
    lines.append('    }')
    lines.append('')
    lines.append('    /** 中文展示名。 */')
    lines.append('    public String getLabel() {')
    lines.append('        return label;')
    lines.append('    }')
    lines.append('')
    lines.append('    /** 数据库存储值（与枚举常量名一致）。 */')
    lines.append('    public String getCode() {')
    lines.append('        return name();')
    lines.append('    }')
    lines.append('')
    lines.append('    /**')
    lines.append('     * 按数据库取值解析枚举，无法匹配时抛出 {@link IllegalArgumentException}。')
    lines.append('     *')
    lines.append('     * @param code 数据库 TEXT 列取值')
    lines.append('     * @return 对应枚举常量')
    lines.append('     */')
    lines.append('    public static %s fromCode(String code) {' % name)
    lines.append('        if (code == null) {')
    lines.append('            throw new IllegalArgumentException("%s 取值不能为空");' % name)
    lines.append('        }')
    lines.append('        for (%s value : values()) {' % name)
    lines.append('            if (value.name().equalsIgnoreCase(code.trim())) {')
    lines.append('                return value;')
    lines.append('            }')
    lines.append('        }')
    lines.append('        throw new IllegalArgumentException("非法的 %s 取值: " + code);' % name)
    lines.append('    }')
    lines.append('')
    lines.append('    /** 解析失败时返回默认值，供历史脏数据容错使用。 */')
    lines.append('    public static %s fromCode(String code, %s defaultValue) {' % (name, name))
    lines.append('        try {')
    lines.append('            return fromCode(code);')
    lines.append('        } catch (IllegalArgumentException e) {')
    lines.append('            return defaultValue;')
    lines.append('        }')
    lines.append('    }')
    lines.append('}')
    lines.append('')
    write(os.path.join('src', 'main', 'java', 'edu', 'campus', 'recycle', 'entity', name + '.java'), '\n'.join(lines))

# --------------------------------------------------------------------------
# DTO（6 个）
# --------------------------------------------------------------------------
DTOS = {}

DTOS['ItemQuery'] = '''package edu.campus.recycle.dto;

import java.math.BigDecimal;

/**
 * 物品检索条件对象（契约第 4 节），承载 keyword/categoryId/价格区间/交易方式/状态/
 * 发布者/排序/分页共 10 个可选条件，避免超长参数表。
 */
public class ItemQuery {

    /** 关键字，匹配标题、描述与标签 */
    private String keyword;
    /** 分类ID（含二级分类时由 Service 展开） */
    private Integer categoryId;
    /** 价格下限（含） */
    private BigDecimal minPrice;
    /** 价格上限（含） */
    private BigDecimal maxPrice;
    /** 交易方式：SELL/EXCHANGE/FREE */
    private String tradeType;
    /** 物品状态，默认仅检索 ON_SALE */
    private String status;
    /** 发布者ID */
    private Integer ownerId;
    /** 排序方式：LATEST/PRICE_ASC/PRICE_DESC */
    private String sortBy;
    /** 页码，从 1 开始 */
    private int pageNo = 1;
    /** 每页条数 */
    private int pageSize = 10;

    public ItemQuery() {
    }

    public int getOffset() {
        return (Math.max(pageNo, 1) - 1) * getLimit();
    }

    public int getLimit() {
        return pageSize <= 0 ? 10 : pageSize;
    }

    /** 排序方式，未指定时按最新排序。 */
    public String getSortByOrDefault() {
        return sortBy == null || sortBy.isBlank() ? "LATEST" : sortBy;
    }

    public String getKeyword() {
        return keyword;
    }

    public void setKeyword(String keyword) {
        this.keyword = keyword;
    }

    public Integer getCategoryId() {
        return categoryId;
    }

    public void setCategoryId(Integer categoryId) {
        this.categoryId = categoryId;
    }

    public BigDecimal getMinPrice() {
        return minPrice;
    }

    public void setMinPrice(BigDecimal minPrice) {
        this.minPrice = minPrice;
    }

    public BigDecimal getMaxPrice() {
        return maxPrice;
    }

    public void setMaxPrice(BigDecimal maxPrice) {
        this.maxPrice = maxPrice;
    }

    public String getTradeType() {
        return tradeType;
    }

    public void setTradeType(String tradeType) {
        this.tradeType = tradeType;
    }

    public String getStatus() {
        return status;
    }

    public void setStatus(String status) {
        this.status = status;
    }

    public Integer getOwnerId() {
        return ownerId;
    }

    public void setOwnerId(Integer ownerId) {
        this.ownerId = ownerId;
    }

    public String getSortBy() {
        return sortBy;
    }

    public void setSortBy(String sortBy) {
        this.sortBy = sortBy;
    }

    public int getPageNo() {
        return pageNo;
    }

    public void setPageNo(int pageNo) {
        this.pageNo = pageNo;
    }

    public int getPageSize() {
        return pageSize;
    }

    public void setPageSize(int pageSize) {
        this.pageSize = pageSize;
    }

    @Override
    public String toString() {
        return "ItemQuery{keyword=" + keyword + ", categoryId=" + categoryId
                + ", minPrice=" + minPrice + ", maxPrice=" + maxPrice
                + ", tradeType=" + tradeType + ", status=" + status
                + ", ownerId=" + ownerId + ", sortBy=" + sortBy
                + ", pageNo=" + pageNo + ", pageSize=" + pageSize + '}';
    }
}
'''

DTOS['PageResult'] = '''package edu.campus.recycle.dto;

import java.util.ArrayList;
import java.util.List;

/**
 * 分页结果（契约第 4 节），同时携带记录、总数与页码信息，
 * 由 {@link #of(List, long, int, int)} 统一计算总页数。
 *
 * @param <T> 记录类型
 */
public class PageResult<T> {

    /** 当前页记录 */
    private List<T> records = new ArrayList<>();
    /** 满足条件的总记录数 */
    private long total;
    /** 当前页码（从 1 开始） */
    private int pageNo = 1;
    /** 每页条数 */
    private int pageSize = 10;
    /** 总页数 */
    private int totalPages;

    public PageResult() {
    }

    public PageResult(List<T> records, long total, int pageNo, int pageSize) {
        this.records = records == null ? new ArrayList<>() : records;
        this.total = total;
        this.pageNo = Math.max(pageNo, 1);
        this.pageSize = pageSize <= 0 ? 10 : pageSize;
        this.totalPages = (int) ((total + this.pageSize - 1) / this.pageSize);
    }

    /**
     * 构建分页结果。
     *
     * @param records  当前页记录
     * @param total    总记录数
     * @param pageNo   当前页码
     * @param pageSize 每页条数
     * @param <T>      记录类型
     * @return 分页结果
     */
    public static <T> PageResult<T> of(List<T> records, long total, int pageNo, int pageSize) {
        return new PageResult<>(records, total, pageNo, pageSize);
    }

    public boolean isEmpty() {
        return records == null || records.isEmpty();
    }

    public List<T> getRecords() {
        return records;
    }

    public void setRecords(List<T> records) {
        this.records = records;
    }

    public long getTotal() {
        return total;
    }

    public void setTotal(long total) {
        this.total = total;
    }

    public int getPageNo() {
        return pageNo;
    }

    public void setPageNo(int pageNo) {
        this.pageNo = pageNo;
    }

    public int getPageSize() {
        return pageSize;
    }

    public void setPageSize(int pageSize) {
        this.pageSize = pageSize;
    }

    public int getTotalPages() {
        return totalPages;
    }

    public void setTotalPages(int totalPages) {
        this.totalPages = totalPages;
    }

    @Override
    public String toString() {
        return "PageResult{total=" + total + ", pageNo=" + pageNo + ", pageSize=" + pageSize
                + ", totalPages=" + totalPages + ", records=" + (records == null ? 0 : records.size()) + '}';
    }
}
'''

DTOS['StatisticsDTO'] = '''package edu.campus.recycle.dto;

import java.math.BigDecimal;

/**
 * 分类统计结果（契约第 4 节）：完成流转笔数、成交总额与碳减排量。
 */
public class StatisticsDTO {

    /** 分类名 */
    private String categoryName;
    /** 已完成流转笔数 */
    private long flowCount;
    /** 成交总额（元） */
    private BigDecimal totalAmount = BigDecimal.ZERO;
    /** 碳减排量（kgCO₂e） */
    private double carbonReduction;

    public StatisticsDTO() {
    }

    public StatisticsDTO(String categoryName, long flowCount, BigDecimal totalAmount, double carbonReduction) {
        this.categoryName = categoryName;
        this.flowCount = flowCount;
        this.totalAmount = totalAmount == null ? BigDecimal.ZERO : totalAmount;
        this.carbonReduction = carbonReduction;
    }

    public String getCategoryName() {
        return categoryName;
    }

    public void setCategoryName(String categoryName) {
        this.categoryName = categoryName;
    }

    public long getFlowCount() {
        return flowCount;
    }

    public void setFlowCount(long flowCount) {
        this.flowCount = flowCount;
    }

    public BigDecimal getTotalAmount() {
        return totalAmount;
    }

    public void setTotalAmount(BigDecimal totalAmount) {
        this.totalAmount = totalAmount;
    }

    public double getCarbonReduction() {
        return carbonReduction;
    }

    public void setCarbonReduction(double carbonReduction) {
        this.carbonReduction = carbonReduction;
    }

    @Override
    public String toString() {
        return "StatisticsDTO{categoryName=" + categoryName + ", flowCount=" + flowCount
                + ", totalAmount=" + totalAmount + ", carbonReduction=" + carbonReduction + '}';
    }
}
'''

DTOS['UserCreditDTO'] = '''package edu.campus.recycle.dto;

/**
 * 用户信用视图对象（契约第 4 节），用于控制台/界面展示信用分与信用等级，
 * 不参与持久化，由 Service 依据 {@code user.credit_score} 实时组装。
 */
public class UserCreditDTO {

    /** 用户ID */
    private Integer userId;
    /** 登录名 */
    private String username;
    /** 真实姓名 */
    private String realName;
    /** 信用分 */
    private Integer creditScore;
    /** 信用等级：优秀/良好/正常/受限 */
    private String creditLevel;
    /** 信用分变更次数（来自 credit_log 统计） */
    private int changeCount;

    public UserCreditDTO() {
    }

    public UserCreditDTO(Integer userId, String username, String realName, Integer creditScore,
                         String creditLevel, int changeCount) {
        this.userId = userId;
        this.username = username;
        this.realName = realName;
        this.creditScore = creditScore;
        this.creditLevel = creditLevel;
        this.changeCount = changeCount;
    }

    /**
     * 按信用分区间推导信用等级：≥120 优秀、≥100 良好、≥60 正常、&lt;60 受限。
     *
     * @param score 信用分
     * @return 信用等级中文名
     */
    public static String levelOf(Integer score) {
        int value = score == null ? 0 : score;
        if (value >= 120) {
            return "优秀";
        }
        if (value >= 100) {
            return "良好";
        }
        if (value >= 60) {
            return "正常";
        }
        return "受限";
    }

    public Integer getUserId() {
        return userId;
    }

    public void setUserId(Integer userId) {
        this.userId = userId;
    }

    public String getUsername() {
        return username;
    }

    public void setUsername(String username) {
        this.username = username;
    }

    public String getRealName() {
        return realName;
    }

    public void setRealName(String realName) {
        this.realName = realName;
    }

    public Integer getCreditScore() {
        return creditScore;
    }

    public void setCreditScore(Integer creditScore) {
        this.creditScore = creditScore;
    }

    public String getCreditLevel() {
        return creditLevel;
    }

    public void setCreditLevel(String creditLevel) {
        this.creditLevel = creditLevel;
    }

    public int getChangeCount() {
        return changeCount;
    }

    public void setChangeCount(int changeCount) {
        this.changeCount = changeCount;
    }

    @Override
    public String toString() {
        return "UserCreditDTO{userId=" + userId + ", username=" + username + ", realName=" + realName
                + ", creditScore=" + creditScore + ", creditLevel=" + creditLevel
                + ", changeCount=" + changeCount + '}';
    }
}
'''

DTOS['LoginResult'] = '''package edu.campus.recycle.dto;

import edu.campus.recycle.entity.User;

import java.time.LocalDateTime;

/**
 * 登录结果（契约第 4 节）：登录成功后回填用户概要信息与最近登录时间，
 * 供控制台/界面提示与后续页面数据加载使用。
 */
public class LoginResult {

    /** 是否成功 */
    private boolean success;
    /** 用户ID */
    private Integer userId;
    /** 登录名 */
    private String username;
    /** 真实姓名 */
    private String realName;
    /** 角色：STUDENT/TEACHER/ADMIN */
    private String role;
    /** 信用分 */
    private Integer creditScore;
    /** 本次登录时间 */
    private LocalDateTime loginAt;
    /** 提示信息 */
    private String message;

    public LoginResult() {
    }

    public LoginResult(boolean success, Integer userId, String username, String realName,
                       String role, Integer creditScore, LocalDateTime loginAt, String message) {
        this.success = success;
        this.userId = userId;
        this.username = username;
        this.realName = realName;
        this.role = role;
        this.creditScore = creditScore;
        this.loginAt = loginAt;
        this.message = message;
    }

    /**
     * 由用户实体构建登录成功结果。
     *
     * @param user     登录成功的用户
     * @param loginAt  登录时间
     * @return 登录结果
     */
    public static LoginResult ofSuccess(User user, LocalDateTime loginAt) {
        return new LoginResult(true, user.getId(), user.getUsername(), user.getRealName(),
                user.getRole(), user.getCreditScore(), loginAt, "登录成功");
    }

    public boolean isSuccess() {
        return success;
    }

    public void setSuccess(boolean success) {
        this.success = success;
    }

    public Integer getUserId() {
        return userId;
    }

    public void setUserId(Integer userId) {
        this.userId = userId;
    }

    public String getUsername() {
        return username;
    }

    public void setUsername(String username) {
        this.username = username;
    }

    public String getRealName() {
        return realName;
    }

    public void setRealName(String realName) {
        this.realName = realName;
    }

    public String getRole() {
        return role;
    }

    public void setRole(String role) {
        this.role = role;
    }

    public Integer getCreditScore() {
        return creditScore;
    }

    public void setCreditScore(Integer creditScore) {
        this.creditScore = creditScore;
    }

    public LocalDateTime getLoginAt() {
        return loginAt;
    }

    public void setLoginAt(LocalDateTime loginAt) {
        this.loginAt = loginAt;
    }

    public String getMessage() {
        return message;
    }

    public void setMessage(String message) {
        this.message = message;
    }

    @Override
    public String toString() {
        return "LoginResult{success=" + success + ", userId=" + userId + ", username=" + username
                + ", role=" + role + ", creditScore=" + creditScore + ", message=" + message + '}';
    }
}
'''

DTOS['TradeDetailDTO'] = '''package edu.campus.recycle.dto;

import edu.campus.recycle.entity.Item;
import edu.campus.recycle.entity.Review;
import edu.campus.recycle.entity.TradeFlow;
import edu.campus.recycle.entity.TradeMessage;
import edu.campus.recycle.entity.User;

import java.util.ArrayList;
import java.util.List;

/**
 * 流转详情聚合对象（契约第 4 节）：一次查询装配流转、物品、买卖双方、沟通消息与评价，
 * 避免界面层逐表拼接产生的多次往返查询。
 */
public class TradeDetailDTO {

    /** 流转记录 */
    private TradeFlow flow;
    /** 关联物品 */
    private Item item;
    /** 出让方 */
    private User seller;
    /** 受让方 */
    private User buyer;
    /** 沟通消息 */
    private List<TradeMessage> messages = new ArrayList<>();
    /** 双方评价 */
    private List<Review> reviews = new ArrayList<>();

    public TradeDetailDTO() {
    }

    public TradeDetailDTO(TradeFlow flow, Item item, User seller, User buyer,
                          List<TradeMessage> messages, List<Review> reviews) {
        this.flow = flow;
        this.item = item;
        this.seller = seller;
        this.buyer = buyer;
        this.messages = messages == null ? new ArrayList<>() : messages;
        this.reviews = reviews == null ? new ArrayList<>() : reviews;
    }

    public TradeFlow getFlow() {
        return flow;
    }

    public void setFlow(TradeFlow flow) {
        this.flow = flow;
    }

    public Item getItem() {
        return item;
    }

    public void setItem(Item item) {
        this.item = item;
    }

    public User getSeller() {
        return seller;
    }

    public void setSeller(User seller) {
        this.seller = seller;
    }

    public User getBuyer() {
        return buyer;
    }

    public void setBuyer(User buyer) {
        this.buyer = buyer;
    }

    public List<TradeMessage> getMessages() {
        return messages;
    }

    public void setMessages(List<TradeMessage> messages) {
        this.messages = messages;
    }

    public List<Review> getReviews() {
        return reviews;
    }

    public void setReviews(List<Review> reviews) {
        this.reviews = reviews;
    }

    @Override
    public String toString() {
        return "TradeDetailDTO{flow=" + (flow == null ? null : flow.getId())
                + ", item=" + (item == null ? null : item.getId())
                + ", seller=" + (seller == null ? null : seller.getId())
                + ", buyer=" + (buyer == null ? null : buyer.getId())
                + ", messages=" + messages.size() + ", reviews=" + reviews.size() + '}';
    }
}
'''

for name, content in DTOS.items():
    write(os.path.join('src', 'main', 'java', 'edu', 'campus', 'recycle', 'dto', name + '.java'), content)

print('\npart1 完成。')
