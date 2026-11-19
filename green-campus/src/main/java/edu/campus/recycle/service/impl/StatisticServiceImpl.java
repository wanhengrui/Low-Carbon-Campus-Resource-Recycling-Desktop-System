package edu.campus.recycle.service.impl;

import edu.campus.recycle.dao.CategoryDao;
import edu.campus.recycle.dao.SystemConfigDao;
import edu.campus.recycle.dao.TradeFlowDao;
import edu.campus.recycle.dto.StatisticsDTO;
import edu.campus.recycle.entity.Category;
import edu.campus.recycle.service.StatisticService;
import edu.campus.recycle.util.CarbonFactorStrategy;
import edu.campus.recycle.util.CsvExporter;

import java.io.IOException;
import java.math.BigDecimal;
import java.math.RoundingMode;
import java.nio.file.Path;
import java.time.LocalDateTime;
import java.util.ArrayList;
import java.util.Comparator;
import java.util.HashMap;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;
import java.util.Objects;

/**
 * 统计服务实现：按一级分类聚合完成流转的笔数/金额，并按 system_config 中的
 * carbon.factor.* 系数折算碳减排量；策略模式 {@link CarbonFactorStrategy} 提供缺省系数回退。
 */
public class StatisticServiceImpl implements StatisticService {

    /** 一级分类名称 → system_config 中碳减排系数键。 */
    private static final Map<String, String> FACTOR_KEYS = Map.of(
            "教材书籍", "carbon.factor.book",
            "数码配件", "carbon.factor.electronics",
            "文体用品", "carbon.factor.sports",
            "生活物资", "carbon.factor.daily");

    private final TradeFlowDao tradeFlowDao;
    private final CategoryDao categoryDao;
    private final SystemConfigDao systemConfigDao;
    private final CarbonFactorStrategy carbonFactorStrategy;
    private final CsvExporter csvExporter = new CsvExporter();

    public StatisticServiceImpl(TradeFlowDao tradeFlowDao, CategoryDao categoryDao,
                                SystemConfigDao systemConfigDao, CarbonFactorStrategy carbonFactorStrategy) {
        this.tradeFlowDao = Objects.requireNonNull(tradeFlowDao, "tradeFlowDao");
        this.categoryDao = Objects.requireNonNull(categoryDao, "categoryDao");
        this.systemConfigDao = Objects.requireNonNull(systemConfigDao, "systemConfigDao");
        this.carbonFactorStrategy = Objects.requireNonNull(carbonFactorStrategy, "carbonFactorStrategy");
    }

    @Override
    public List<StatisticsDTO> statisticsByCategory(LocalDateTime from, LocalDateTime to) {
        List<StatisticsDTO> raw = tradeFlowDao.countByCategoryForPeriod(from, to);
        Map<Integer, Category> categories = new HashMap<>();
        Map<String, Integer> nameToId = new HashMap<>();
        for (Category category : categoryDao.findAll()) {
            categories.put(category.getId(), category);
            if (category.getName() != null) {
                nameToId.putIfAbsent(category.getName(), category.getId());
            }
        }
        Map<String, long[]> counts = new LinkedHashMap<>();
        Map<String, BigDecimal> amounts = new HashMap<>();
        for (StatisticsDTO row : raw) {
            Integer categoryId = nameToId.get(row.getCategoryName());
            String rootName = rootCategoryName(categoryId, categories);
            counts.computeIfAbsent(rootName, key -> new long[1])[0] += row.getFlowCount();
            BigDecimal amount = row.getTotalAmount() == null ? BigDecimal.ZERO : row.getTotalAmount();
            amounts.merge(rootName, amount, BigDecimal::add);
        }
        List<StatisticsDTO> result = new ArrayList<>(counts.size());
        for (Map.Entry<String, long[]> entry : counts.entrySet()) {
            String name = entry.getKey();
            long flowCount = entry.getValue()[0];
            BigDecimal totalAmount = amounts.getOrDefault(name, BigDecimal.ZERO)
                    .setScale(2, RoundingMode.HALF_UP);
            double carbon = factorOf(name) * flowCount;
            result.add(new StatisticsDTO(name, flowCount, totalAmount, carbon));
        }
        result.sort(Comparator.comparingLong(StatisticsDTO::getFlowCount).reversed());
        return result;
    }

    @Override
    public double carbonReduction(LocalDateTime from, LocalDateTime to) {
        double total = 0.0D;
        for (StatisticsDTO dto : statisticsByCategory(from, to)) {
            total += dto.getCarbonReduction();
        }
        return BigDecimal.valueOf(total).setScale(2, RoundingMode.HALF_UP).doubleValue();
    }

    @Override
    public String exportCsv(Path target, LocalDateTime from, LocalDateTime to) throws IOException {
        return csvExporter.exportStatistics(target, statisticsByCategory(from, to), from, to);
    }

    /**
     * 取分类的一级祖先名称（分类仅两级）。
     */
    private String rootCategoryName(Integer categoryId, Map<Integer, Category> categories) {
        if (categoryId == null) {
            return "未分类";
        }
        Category current = categories.get(categoryId);
        int guard = 0;
        while (current != null && current.getParentId() != null && guard++ < 5) {
            Category parent = categories.get(current.getParentId());
            if (parent == null) {
                break;
            }
            current = parent;
        }
        return current == null ? "未分类" : current.getName();
    }

    /**
     * 碳减排系数：优先读 system_config，读不到时回退到策略实现。
     */
    private double factorOf(String rootName) {
        String key = FACTOR_KEYS.get(rootName);
        if (key == null) {
            return carbonFactorStrategy.factorOf(rootName);
        }
        return systemConfigDao.getDouble(key, carbonFactorStrategy.factorOf(rootName));
    }
}
