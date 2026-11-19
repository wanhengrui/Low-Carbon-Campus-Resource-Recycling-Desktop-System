package edu.campus.recycle.util;

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
