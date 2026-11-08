package edu.campus.recycle.controller;

import edu.campus.recycle.dto.StatisticsDTO;
import edu.campus.recycle.service.StatisticService;
import edu.campus.recycle.util.ServiceFactory;

import java.io.IOException;
import java.nio.file.Path;
import java.time.LocalDateTime;
import java.util.List;

/**
 * 统计控制器（薄壳，第 3 轮裁决 v1.1 §13-15）：分类统计、碳减排与 CSV 导出。
 *
 * <p>只做参数校验、调用 {@link StatisticService}，把 IO/业务异常转成用户文案。</p>
 */
public class StatisticController {

    private final StatisticService statisticService;

    public StatisticController() {
        this(ServiceFactory.getInstance().getStatisticService());
    }

    /**
     * 构造控制器（允许注入自定义服务实现）。
     *
     * @param statisticService 统计服务
     */
    public StatisticController(StatisticService statisticService) {
        ControllerSupport.require(statisticService != null, "statisticService 不能为空");
        this.statisticService = statisticService;
    }

    /**
     * 按一级分类统计完成流转的笔数、成交金额与碳减排量。
     */
    public List<StatisticsDTO> statisticsByCategory(LocalDateTime from, LocalDateTime to) {
        requireRange(from, to);
        return statisticService.statisticsByCategory(from, to);
    }

    /**
     * 碳减排总量（kgCO2e）。
     */
    public double carbonReduction(LocalDateTime from, LocalDateTime to) {
        requireRange(from, to);
        return statisticService.carbonReduction(from, to);
    }

    /**
     * 导出统计 CSV（UTF-8 BOM）。
     *
     * @return 导出文件绝对路径，失败时返回用户可读文案
     */
    public String exportCsv(Path target, LocalDateTime from, LocalDateTime to) {
        ControllerSupport.require(target != null, "导出路径不能为空");
        requireRange(from, to);
        try {
            return statisticService.exportCsv(target, from, to);
        } catch (IOException e) {
            return "导出失败：" + e.getMessage();
        } catch (RuntimeException e) {
            return "导出失败：" + e.getMessage();
        }
    }

    private void requireRange(LocalDateTime from, LocalDateTime to) {
        ControllerSupport.require(from != null, "统计起始时间不能为空");
        ControllerSupport.require(to != null, "统计结束时间不能为空");
        ControllerSupport.require(!from.isAfter(to), "统计起始时间不能晚于结束时间");
    }
}
