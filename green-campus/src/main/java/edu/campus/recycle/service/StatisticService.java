package edu.campus.recycle.service;

import edu.campus.recycle.dto.StatisticsDTO;

import java.io.IOException;
import java.nio.file.Path;
import java.time.LocalDateTime;
import java.util.List;

/**
 * 统计服务：按分类统计完成流转的笔数、成交金额与碳减排量，并支持导出 CSV。
 */
public interface StatisticService {

    List<StatisticsDTO> statisticsByCategory(LocalDateTime from, LocalDateTime to);

    double carbonReduction(LocalDateTime from, LocalDateTime to);

    String exportCsv(Path target, LocalDateTime from, LocalDateTime to) throws IOException;
}
