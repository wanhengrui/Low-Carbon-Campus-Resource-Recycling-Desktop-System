# -*- coding: utf-8 -*-
"""D7 生成器 part4a：策略（排序/减排系数）、观察者（事件总线 + 3 监听器）、工厂、CSV 模板。"""
import os

BASE = r'C:\Users\wanhe\Desktop\软件构造\迭代一-成员1\code\green-campus'


def write(rel, content):
    path = os.path.join(BASE, rel)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'w', encoding='utf-8', newline='\n') as f:
        f.write(content)
    print('  + %-82s %5d B' % (rel, len(content.encode('utf-8'))))


def u(name):
    return os.path.join('src', 'main', 'java', 'edu', 'campus', 'recycle', 'util', name + '.java')


ITEM_SORT_STRATEGY = '''package edu.campus.recycle.util;

/**
 * 物品检索排序策略（策略模式，契约第 8 节）。
 *
 * <p>{@code ORDER BY} 片段由策略提供，而不是由前端字符串拼接，
 * 因而既满足"排序可插拔"，也避免 SQL 注入（排序字段不可参数化，只能白名单化）。</p>
 */
public interface ItemSortStrategy {

    /**
     * 策略编码，与 {@code ItemQuery.sortBy} 的取值一致。
     *
     * @return 编码
     */
    String getCode();

    /**
     * 展示名称。
     *
     * @return 中文名称
     */
    String getDisplayName();

    /**
     * 返回 ORDER BY 子句片段（不含 {@code ORDER BY} 关键字，仅白名单常量拼接）。
     *
     * @return 例如 {@code "i.price ASC, i.id DESC"}
     */
    String orderByClause();
}
'''
write(u('ItemSortStrategy'), ITEM_SORT_STRATEGY)

LATEST = '''package edu.campus.recycle.util;

/**
 * 排序策略：最新发布优先（默认策略）。
 */
public class LatestItemSortStrategy implements ItemSortStrategy {

    @Override
    public String getCode() {
        return "LATEST";
    }

    @Override
    public String getDisplayName() {
        return "最新发布";
    }

    @Override
    public String orderByClause() {
        return "i.created_at DESC, i.id DESC";
    }
}
'''
write(u('LatestItemSortStrategy'), LATEST)

PRICE_ASC = '''package edu.campus.recycle.util;

/**
 * 排序策略：价格从低到高。
 */
public class PriceAscItemSortStrategy implements ItemSortStrategy {

    @Override
    public String getCode() {
        return "PRICE_ASC";
    }

    @Override
    public String getDisplayName() {
        return "价格升序";
    }

    @Override
    public String orderByClause() {
        return "i.price ASC, i.id DESC";
    }
}
'''
write(u('PriceAscItemSortStrategy'), PRICE_ASC)

PRICE_DESC = '''package edu.campus.recycle.util;

/**
 * 排序策略：价格从高到低。
 */
public class PriceDescItemSortStrategy implements ItemSortStrategy {

    @Override
    public String getCode() {
        return "PRICE_DESC";
    }

    @Override
    public String getDisplayName() {
        return "价格降序";
    }

    @Override
    public String orderByClause() {
        return "i.price DESC, i.id DESC";
    }
}
'''
write(u('PriceDescItemSortStrategy'), PRICE_DESC)

CARBON_STRATEGY = '''package edu.campus.recycle.util;

/**
 * 碳减排系数策略（策略模式）：不同分类的物品"再使用一次"折算的减排量不同，
 * 由策略集中维护，便于后续接入更精确的碳排放因子表而不改统计服务。
 */
public interface CarbonFactorStrategy {

    /**
     * 按分类名称返回单次完成的减排系数（kgCO2e）。
     *
     * @param categoryName 分类名称，可为 null
     * @return 减排系数，未知分类返回缺省系数
     */
    double factorOf(String categoryName);

    /**
     * 策略名称。
     *
     * @return 名称
     */
    String getName();
}
'''
write(u('CarbonFactorStrategy'), CARBON_STRATEGY)

DEFAULT_CARBON = '''package edu.campus.recycle.util;

import java.util.HashMap;
import java.util.Map;

/**
 * 缺省碳减排系数策略：按一级分类给定经验系数（单位：kgCO2e/次），
 * 未登记分类使用 {@link #DEFAULT_FACTOR}。
 *
 * <p>系数取值说明（用于统计页展示与课程报告说明）：
 * 数码配件再流通减排最高（3.2），教材书籍最低（0.6），
 * 该值后续可替换为生态环境部门发布的因子表（实现类可替换，调用方不变）。</p>
 */
public class DefaultCarbonFactorStrategy implements CarbonFactorStrategy {

    /** 未登记分类的缺省系数（kgCO2e/次） */
    public static final double DEFAULT_FACTOR = 1.0D;

    private final Map<String, Double> factors = new HashMap<>();

    private final double defaultFactor;

    public DefaultCarbonFactorStrategy() {
        this(DEFAULT_FACTOR);
    }

    public DefaultCarbonFactorStrategy(double defaultFactor) {
        this.defaultFactor = defaultFactor;
        factors.put("教材书籍", 0.6D);
        factors.put("考研考证", 0.6D);
        factors.put("公共课教材", 0.6D);
        factors.put("数码配件", 3.2D);
        factors.put("手机配件", 2.4D);
        factors.put("电脑外设", 3.2D);
        factors.put("文体用品", 1.1D);
        factors.put("球类器材", 1.1D);
        factors.put("生活物资", 1.8D);
        factors.put("宿舍用品", 1.8D);
    }

    @Override
    public double factorOf(String categoryName) {
        if (categoryName == null || categoryName.isBlank()) {
            return defaultFactor;
        }
        Double factor = factors.get(categoryName.trim());
        return factor == null ? defaultFactor : factor;
    }

    @Override
    public String getName() {
        return "默认分类减排系数";
    }
}
'''
write(u('DefaultCarbonFactorStrategy'), DEFAULT_CARBON)

ITEM_EVENT = '''package edu.campus.recycle.util;

import edu.campus.recycle.entity.Item;
import edu.campus.recycle.entity.TradeFlow;

import java.time.LocalDateTime;
import java.util.Objects;

/**
 * 物品/流转领域事件（观察者模式被观察对象，契约第 8 节）。
 *
 * <p>事件在业务事务内部发布，监听器与主流程共用同一个 JDBC 连接，
 * 因此"改物品状态 / 记信用 / 写日志 / 统计"可以保持在同一事务内（BR-07）。</p>
 */
public final class ItemEvent {

    /** 事件类型 */
    public enum Type {
        /** 发布物品 */
        ITEM_PUBLISHED,
        /** 下架物品 */
        ITEM_OFF_SHELF,
        /** 审核物品 */
        ITEM_AUDITED,
        /** 发起流转申请 */
        FLOW_APPLIED,
        /** 出让方同意 */
        FLOW_AGREED,
        /** 流转完成 */
        FLOW_DONE,
        /** 取消流转 */
        FLOW_CANCELLED,
        /** 新增评价 */
        REVIEW_CREATED
    }

    private final Type type;

    private final Integer itemId;

    private final Integer flowId;

    private final Integer operatorId;

    private final String detail;

    private final LocalDateTime occurredAt;

    private ItemEvent(Type type, Integer itemId, Integer flowId, Integer operatorId,
                      String detail, LocalDateTime occurredAt) {
        this.type = Objects.requireNonNull(type, "type");
        this.itemId = itemId;
        this.flowId = flowId;
        this.operatorId = operatorId;
        this.detail = detail;
        this.occurredAt = occurredAt == null ? LocalDateTime.now() : occurredAt;
    }

    /**
     * 创建事件。
     *
     * @param type       类型
     * @param itemId     物品ID，可为 null
     * @param flowId     流转ID，可为 null
     * @param operatorId 操作人ID，可为 null（系统）
     * @param detail     详情描述
     * @return 事件
     */
    public static ItemEvent of(Type type, Integer itemId, Integer flowId, Integer operatorId, String detail) {
        return new ItemEvent(type, itemId, flowId, operatorId, detail, LocalDateTime.now());
    }

    /**
     * 便捷工厂：物品事件。
     *
     * @param type       类型
     * @param item       物品，可为 null
     * @param operatorId 操作人
     * @param detail     详情
     * @return 事件
     */
    public static ItemEvent item(Type type, Item item, Integer operatorId, String detail) {
        return new ItemEvent(type, item == null ? null : item.getId(), null, operatorId, detail,
                LocalDateTime.now());
    }

    /**
     * 便捷工厂：流转事件。
     *
     * @param type       类型
     * @param flow       流转
     * @param operatorId 操作人
     * @param detail     详情
     * @return 事件
     */
    public static ItemEvent flow(Type type, TradeFlow flow, Integer operatorId, String detail) {
        return new ItemEvent(type, flow == null ? null : flow.getItemId(),
                flow == null ? null : flow.getId(), operatorId, detail, LocalDateTime.now());
    }

    public Type getType() {
        return type;
    }

    public Integer getItemId() {
        return itemId;
    }

    public Integer getFlowId() {
        return flowId;
    }

    public Integer getOperatorId() {
        return operatorId;
    }

    public String getDetail() {
        return detail;
    }

    public LocalDateTime getOccurredAt() {
        return occurredAt;
    }

    @Override
    public String toString() {
        return "ItemEvent{" + type + ", itemId=" + itemId + ", flowId=" + flowId
                + ", operatorId=" + operatorId + ", detail=" + detail + "}";
    }
}
'''
write(u('ItemEvent'), ITEM_EVENT)

ITEM_EVENT_LISTENER = '''package edu.campus.recycle.util;

/**
 * 物品/流转事件监听器（观察者模式观察者接口）。
 */
@FunctionalInterface
public interface ItemEventListener {

    /**
     * 处理事件。
     *
     * @param event 事件
     */
    void onEvent(ItemEvent event);
}
'''
write(u('ItemEventListener'), ITEM_EVENT_LISTENER)

EVENT_BUS = '''package edu.campus.recycle.util;

import java.util.List;
import java.util.concurrent.CopyOnWriteArrayList;
import java.util.logging.Level;
import java.util.logging.Logger;

/**
 * 事件总线（观察者模式主题/被观察者，单例）。
 *
 * <p>流转完成的副作用（信用分、操作日志、统计）通过监听器解耦，
 * 主流程只发布事件。监听器抛出异常时向上传播，使外层事务整体回滚，
 * 保证 BR-07"完成 + 信用 + 日志同事务"。</p>
 */
public final class ItemEventBus {

    private static final Logger LOG = Logger.getLogger(ItemEventBus.class.getName());

    private static final ItemEventBus INSTANCE = new ItemEventBus();

    private final List<ItemEventListener> listeners = new CopyOnWriteArrayList<>();

    private ItemEventBus() {
        DaoFactory factory = DaoFactory.getInstance();
        register(new OperationLogListener(factory.getOperationLogDao()));
        register(new CreditChangeListener(factory.getUserDao(), factory.getCreditLogDao()));
        register(new StatisticListener());
    }

    /**
     * 全局单例。
     *
     * @return 事件总线
     */
    public static ItemEventBus getInstance() {
        return INSTANCE;
    }

    /**
     * 注册监听器。
     *
     * @param listener 监听器
     */
    public void register(ItemEventListener listener) {
        if (listener != null) {
            listeners.add(listener);
        }
    }

    /**
     * 注销监听器。
     *
     * @param listener 监听器
     * @return 是否注销成功
     */
    public boolean unregister(ItemEventListener listener) {
        return listeners.remove(listener);
    }

    /**
     * 当前监听器快照。
     *
     * @return 监听器列表
     */
    public List<ItemEventListener> getListeners() {
        return List.copyOf(listeners);
    }

    /**
     * 发布事件：依次同步通知所有监听器。
     *
     * @param event 事件
     */
    public void publish(ItemEvent event) {
        if (event == null) {
            return;
        }
        for (ItemEventListener listener : listeners) {
            try {
                listener.onEvent(event);
            } catch (RuntimeException e) {
                LOG.log(Level.SEVERE, "事件监听器执行失败：" + listener.getClass().getSimpleName()
                        + "，事件=" + event, e);
                throw e;
            }
        }
    }
}
'''
write(u('ItemEventBus'), EVENT_BUS)

OPLOG_LISTENER = '''package edu.campus.recycle.util;

import edu.campus.recycle.dao.OperationLogDao;
import edu.campus.recycle.entity.OperationLog;

/**
 * 操作日志监听器：把领域事件落库到 {@code operation_log}（BR-11 仅追加）。
 *
 * <p>与业务操作处于同一事务的连接上，事件发布成功即日志写入成功。</p>
 */
public class OperationLogListener implements ItemEventListener {

    private final OperationLogDao operationLogDao;

    public OperationLogListener(OperationLogDao operationLogDao) {
        this.operationLogDao = operationLogDao;
    }

    @Override
    public void onEvent(ItemEvent event) {
        OperationLog log = new OperationLog();
        log.setOperatorId(event.getOperatorId());
        log.setOperation(event.getType().name());
        if (event.getFlowId() != null) {
            log.setTargetType("FLOW");
            log.setTargetId(event.getFlowId());
        } else {
            log.setTargetType("ITEM");
            log.setTargetId(event.getItemId());
        }
        log.setDetail(event.getDetail());
        log.setIp("localhost");
        log.setCreatedAt(event.getOccurredAt());
        operationLogDao.insert(log);
    }
}
'''
write(u('OperationLogListener'), OPLOG_LISTENER)

CREDIT_LISTENER = '''package edu.campus.recycle.util;

import edu.campus.recycle.dao.CreditLogDao;
import edu.campus.recycle.dao.UserDao;

/**
 * 信用分监听器：流转完成后给双方增加信用分并写入 {@code credit_log} 快照（BR-04/BR-07）。
 *
 * <p>只在 {@link ItemEvent.Type#FLOW_DONE} 时生效，其它事件忽略。</p>
 */
public class CreditChangeListener implements ItemEventListener {

    /** 完成一次流转，出让方/受让方各加 2 分 */
    public static final int FLOW_DONE_DELTA = 2;

    private final UserDao userDao;

    private final CreditLogDao creditLogDao;

    public CreditChangeListener(UserDao userDao, CreditLogDao creditLogDao) {
        this.userDao = userDao;
        this.creditLogDao = creditLogDao;
    }

    @Override
    public void onEvent(ItemEvent event) {
        if (event.getType() != ItemEvent.Type.FLOW_DONE || event.getFlowId() == null) {
            return;
        }
        Integer sellerId = CreditRules.findParticipant(userDao, event.getFlowId(), true);
        Integer buyerId = CreditRules.findParticipant(userDao, event.getFlowId(), false);
        if (sellerId != null) {
            CreditRules.apply(userDao, creditLogDao, sellerId, FLOW_DONE_DELTA, event.getFlowId(),
                    "完成流转（出让方）");
        }
        if (buyerId != null) {
            CreditRules.apply(userDao, creditLogDao, buyerId, FLOW_DONE_DELTA, event.getFlowId(),
                    "完成流转（受让方）");
        }
    }
}
'''
write(u('CreditChangeListener'), CREDIT_LISTENER)

CREDIT_RULES = '''package edu.campus.recycle.util;

import edu.campus.recycle.dao.CreditLogDao;
import edu.campus.recycle.dao.TradeFlowDao;
import edu.campus.recycle.dao.UserDao;
import edu.campus.recycle.entity.CreditLog;
import edu.campus.recycle.entity.TradeFlow;
import edu.campus.recycle.entity.User;

import java.time.LocalDateTime;

/**
 * 信用分变更规则（公共逻辑，避免监听器与 UserService 重复实现）。
 *
 * <p>区间约束 [0,150] 在此统一裁剪，并保证"更新用户分数 + 写 credit_log 快照"
 * 在同一连接/事务中完成（BR-04）。</p>
 */
public final class CreditRules {

    /** 信用分下限 */
    public static final int MIN_SCORE = 0;

    /** 信用分上限 */
    public static final int MAX_SCORE = 150;

    private CreditRules() {
    }

    /**
     * 裁剪到合法区间。
     *
     * @param score 原始分数
     * @return [0,150] 内的分数
     */
    public static int clamp(int score) {
        return Math.max(MIN_SCORE, Math.min(MAX_SCORE, score));
    }

    /**
     * 变更信用分并写流水快照。
     *
     * @param userDao      用户 DAO
     * @param creditLogDao 流水 DAO
     * @param userId       用户ID
     * @param delta        变化量
     * @param flowId       关联流转，可为 null
     * @param reason       原因
     * @return 变更后分数
     */
    public static int apply(UserDao userDao, CreditLogDao creditLogDao, int userId, int delta,
                            Integer flowId, String reason) {
        User user = userDao.findById(userId).orElse(null);
        if (user == null) {
            return MIN_SCORE;
        }
        int before = user.getCreditScore() == null ? 100 : user.getCreditScore();
        int after = clamp(before + delta);
        userDao.updateCreditScore(userId, after);
        CreditLog log = new CreditLog();
        log.setUserId(userId);
        log.setFlowId(flowId);
        log.setDelta(after - before);
        log.setScoreAfter(after);
        log.setReason(reason);
        log.setCreatedAt(LocalDateTime.now());
        creditLogDao.insert(log);
        return after;
    }

    /**
     * 查询流转参与方（出让方/受让方）。
     *
     * @param userDao 用户 DAO
     * @param flowId  流转ID
     * @param seller  true 查出让方，false 查受让方
     * @return 用户ID，流转不存在时返回 null
     */
    public static Integer findParticipant(UserDao userDao, int flowId, boolean seller) {
        // 通过 TradeFlowDao 才能拿到 seller_id/buyer_id，这里用静态持有避免监听器多一个依赖
        TradeFlowDao flowDao = DaoFactory.getInstance().getTradeFlowDao();
        TradeFlow flow = flowDao.findById(flowId).orElse(null);
        if (flow == null) {
            return null;
        }
        return seller ? flow.getSellerId() : flow.getBuyerId();
    }
}
'''
write(u('CreditRules'), CREDIT_RULES)

STAT_LISTENER = '''package edu.campus.recycle.util;

import java.util.EnumMap;
import java.util.Map;
import java.util.concurrent.atomic.AtomicLong;

/**
 * 统计监听器：在内存中累计领域事件次数，供控制台/统计页快速展示，
 * 避免每次刷新都做 COUNT 聚合查询；持久化统计仍以 {@code trade_flow} 为准。
 */
public class StatisticListener implements ItemEventListener {

    private final Map<ItemEvent.Type, AtomicLong> counters = new EnumMap<>(ItemEvent.Type.class);

    public StatisticListener() {
        for (ItemEvent.Type type : ItemEvent.Type.values()) {
            counters.put(type, new AtomicLong());
        }
    }

    @Override
    public void onEvent(ItemEvent event) {
        AtomicLong counter = counters.get(event.getType());
        if (counter != null) {
            counter.incrementAndGet();
        }
    }

    /**
     * 某类事件累计次数。
     *
     * @param type 事件类型
     * @return 次数
     */
    public long count(ItemEvent.Type type) {
        AtomicLong counter = counters.get(type);
        return counter == null ? 0L : counter.get();
    }

    /**
     * 事件计数快照，形如 {@code ITEM_PUBLISHED=3, FLOW_DONE=1}。
     *
     * @return 快照文本
     */
    public String snapshot() {
        StringBuilder builder = new StringBuilder();
        for (Map.Entry<ItemEvent.Type, AtomicLong> entry : counters.entrySet()) {
            if (entry.getValue().get() > 0) {
                if (builder.length() > 0) {
                    builder.append(", ");
                }
                builder.append(entry.getKey()).append('=').append(entry.getValue().get());
            }
        }
        return builder.length() == 0 ? "(无事件)" : builder.toString();
    }
}
'''
write(u('StatisticListener'), STAT_LISTENER)

ABSTRACT_CSV = '''package edu.campus.recycle.util;

import java.io.BufferedWriter;
import java.io.IOException;
import java.io.OutputStreamWriter;
import java.io.Writer;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.List;

/**
 * CSV 导出模板方法（模板方法模式，契约第 8 节）。
 *
 * <p>固定流程：建目录 → 写 UTF-8 BOM → 表头 → 数据行 → 关闭资源；
 * 子类只负责组装表头与数据行，消除"打开文件/编码/资源释放"的重复代码。</p>
 */
public abstract class AbstractCsvExporter {

    /** UTF-8 BOM，保证 Excel 直接双击打开不乱码 */
    private static final String UTF8_BOM = "\\uFEFF";

    /**
     * 导出模板方法（final：流程不可被覆写）。
     *
     * @param target 目标文件
     * @param header 表头
     * @param rows   数据行
     * @return 目标文件路径的字符串形式
     * @throws IOException 写文件失败
     */
    public final String export(Path target, List<String> header, List<List<String>> rows) throws IOException {
        if (target == null) {
            throw new IllegalArgumentException("导出目标路径不能为空");
        }
        Path absolute = target.toAbsolutePath();
        if (absolute.getParent() != null) {
            Files.createDirectories(absolute.getParent());
        }
        try (Writer writer = new BufferedWriter(new OutputStreamWriter(
                Files.newOutputStream(absolute), StandardCharsets.UTF_8))) {
            writer.write(UTF8_BOM);
            writeLine(writer, header);
            if (rows != null) {
                for (List<String> row : rows) {
                    writeLine(writer, row);
                }
            }
            writer.flush();
        }
        return absolute.toString();
    }

    /**
     * 钩子：导出内容描述（子类可覆写用于日志）。
     *
     * @return 描述
     */
    protected String describe() {
        return "CSV";
    }

    private void writeLine(Writer writer, List<String> values) throws IOException {
        if (values == null) {
            writer.write("\\r\\n");
            return;
        }
        StringBuilder line = new StringBuilder();
        for (int i = 0; i < values.size(); i++) {
            if (i > 0) {
                line.append(',');
            }
            line.append(escape(values.get(i)));
        }
        writer.write(line.toString());
        writer.write("\\r\\n");
    }

    private String escape(String value) {
        if (value == null) {
            return "";
        }
        boolean needQuote = value.indexOf(',') >= 0 || value.indexOf('"') >= 0
                || value.indexOf('\\n') >= 0 || value.indexOf('\\r') >= 0;
        if (!needQuote) {
            return value;
        }
        return '"' + value.replace("\\"", "\\"\\"") + '"';
    }
}
'''
write(u('AbstractCsvExporter'), ABSTRACT_CSV)

CSV_EXPORTER = '''package edu.campus.recycle.util;

import edu.campus.recycle.dto.StatisticsDTO;

import java.math.BigDecimal;
import java.math.RoundingMode;
import java.time.LocalDateTime;
import java.util.ArrayList;
import java.util.List;

/**
 * 统计结果导出器：把 {@link StatisticsDTO} 列表按固定表头导出为 CSV。
 *
 * <p>表头：分类, 完成笔数, 成交金额（元）, 减排量（kgCO2e）</p>
 */
public class CsvExporter extends AbstractCsvExporter {

    /** 表头 */
    public static final List<String> HEADER = List.of("分类", "完成笔数", "成交金额（元）", "减排量（kgCO2e）");

    /**
     * 组装统计行。
     *
     * @param statistics 分类统计
     * @return 数据行
     */
    public List<List<String>> toRows(List<StatisticsDTO> statistics) {
        List<List<String>> rows = new ArrayList<>();
        if (statistics == null) {
            return rows;
        }
        for (StatisticsDTO dto : statistics) {
            List<String> row = new ArrayList<>();
            row.add(dto.getCategoryName());
            row.add(String.valueOf(dto.getFlowCount()));
            BigDecimal amount = dto.getTotalAmount() == null
                    ? BigDecimal.ZERO : dto.getTotalAmount().setScale(2, RoundingMode.HALF_UP);
            row.add(amount.toPlainString());
            row.add(String.format("%.2f", dto.getCarbonReduction()));
            rows.add(row);
        }
        return rows;
    }

    /**
     * 导出统计 CSV。
     *
     * @param target     目标文件
     * @param statistics 统计结果
     * @param from       起始时间（仅用于注释）
     * @param to         结束时间（仅用于注释）
     * @return 文件绝对路径
     * @throws java.io.IOException 写文件失败
     */
    public String exportStatistics(java.nio.file.Path target, List<StatisticsDTO> statistics,
                                   LocalDateTime from, LocalDateTime to) throws java.io.IOException {
        return export(target, HEADER, toRows(statistics));
    }

    @Override
    protected String describe() {
        return "分类统计 CSV";
    }
}
'''
write(u('CsvExporter'), CSV_EXPORTER)

DAO_FACTORY = '''package edu.campus.recycle.util;

import edu.campus.recycle.dao.CategoryDao;
import edu.campus.recycle.dao.CreditLogDao;
import edu.campus.recycle.dao.FavoriteDao;
import edu.campus.recycle.dao.ItemDao;
import edu.campus.recycle.dao.ItemImageDao;
import edu.campus.recycle.dao.OperationLogDao;
import edu.campus.recycle.dao.ReviewDao;
import edu.campus.recycle.dao.SystemConfigDao;
import edu.campus.recycle.dao.TradeFlowDao;
import edu.campus.recycle.dao.TradeMessageDao;
import edu.campus.recycle.dao.UserDao;
import edu.campus.recycle.dao.impl.CategoryDaoImpl;
import edu.campus.recycle.dao.impl.CreditLogDaoImpl;
import edu.campus.recycle.dao.impl.FavoriteDaoImpl;
import edu.campus.recycle.dao.impl.ItemDaoImpl;
import edu.campus.recycle.dao.impl.ItemImageDaoImpl;
import edu.campus.recycle.dao.impl.OperationLogDaoImpl;
import edu.campus.recycle.dao.impl.ReviewDaoImpl;
import edu.campus.recycle.dao.impl.SystemConfigDaoImpl;
import edu.campus.recycle.dao.impl.TradeFlowDaoImpl;
import edu.campus.recycle.dao.impl.TradeMessageDaoImpl;
import edu.campus.recycle.dao.impl.UserDaoImpl;

/**
 * DAO 工厂（工厂模式，单例，契约第 8 节）。
 *
 * <p>上层（Service/UI）只依赖接口，通过工厂拿到实现；替换实现（如内存 mock）
 * 或增加缓存代理时，调用方代码不需要修改。所有 DAO 无状态，可安全复用单例。</p>
 */
public final class DaoFactory {

    private static final DaoFactory INSTANCE = new DaoFactory();

    private final UserDao userDao = new UserDaoImpl();

    private final CategoryDao categoryDao = new CategoryDaoImpl();

    private final ItemDao itemDao = new ItemDaoImpl();

    private final ItemImageDao itemImageDao = new ItemImageDaoImpl();

    private final FavoriteDao favoriteDao = new FavoriteDaoImpl();

    private final TradeMessageDao tradeMessageDao = new TradeMessageDaoImpl();

    private final TradeFlowDao tradeFlowDao = new TradeFlowDaoImpl();

    private final ReviewDao reviewDao = new ReviewDaoImpl();

    private final CreditLogDao creditLogDao = new CreditLogDaoImpl();

    private final OperationLogDao operationLogDao = new OperationLogDaoImpl();

    private final SystemConfigDao systemConfigDao = new SystemConfigDaoImpl();

    private DaoFactory() {
    }

    /**
     * 全局单例。
     *
     * @return 工厂
     */
    public static DaoFactory getInstance() {
        return INSTANCE;
    }

    public UserDao getUserDao() {
        return userDao;
    }

    public CategoryDao getCategoryDao() {
        return categoryDao;
    }

    public ItemDao getItemDao() {
        return itemDao;
    }

    public ItemImageDao getItemImageDao() {
        return itemImageDao;
    }

    public FavoriteDao getFavoriteDao() {
        return favoriteDao;
    }

    public TradeMessageDao getTradeMessageDao() {
        return tradeMessageDao;
    }

    public TradeFlowDao getTradeFlowDao() {
        return tradeFlowDao;
    }

    public ReviewDao getReviewDao() {
        return reviewDao;
    }

    public CreditLogDao getCreditLogDao() {
        return creditLogDao;
    }

    public OperationLogDao getOperationLogDao() {
        return operationLogDao;
    }

    public SystemConfigDao getSystemConfigDao() {
        return systemConfigDao;
    }
}
'''
write(u('DaoFactory'), DAO_FACTORY)

print('\npart4a 完成（策略 + 观察者 + 模板 + DAO 工厂）。')
