package edu.campus.recycle.dao;

import edu.campus.recycle.dto.StatisticsDTO;
import edu.campus.recycle.entity.TradeFlow;

import java.time.LocalDateTime;
import java.util.List;
import java.util.Optional;

/**
 * 流转记录 DAO（契约第 5 节）。核心表，配合部分唯一索引
 * {@code uq_flow_item_active} 保证同一物品同时只有一条进行中流转（BR-05）。
 */
public interface TradeFlowDao extends BaseDao<TradeFlow, Integer> {

    /**
     * 插入流转记录并回填自增主键。
     *
     * @param f 流转记录
     * @return 受影响行数
     */
    @Override
    int insert(TradeFlow f);

    /**
     * 查询某物品当前进行中的流转（APPLYING/AGREED）。
     *
     * @param itemId 物品ID
     * @return 进行中的流转
     */
    Optional<TradeFlow> findActiveByItemId(int itemId);

    /**
     * 按主键查询流转。
     *
     * @param id 流转ID
     * @return 流转记录
     */
    Optional<TradeFlow> findById(int id);

    /**
     * 更新流转状态、取消原因与完成时间。
     *
     * @param flowId       流转ID
     * @param status       目标状态
     * @param cancelReason 取消原因，可为 null
     * @param finishedAt   完成时间，可为 null
     * @return 受影响行数
     */
    int updateStatus(int flowId, String status, String cancelReason, LocalDateTime finishedAt);

    /**
     * 分页查询某用户相关的流转（作为出让方或受让方）。
     *
     * @param userId   用户ID
     * @param status   状态过滤，可为 null
     * @param pageNo   页码
     * @param pageSize 每页条数
     * @return 流转列表
     */
    List<TradeFlow> findByUserId(int userId, String status, int pageNo, int pageSize);

    /**
     * 统计某用户相关流转总数。
     *
     * @param userId 用户ID
     * @param status 状态过滤，可为 null
     * @return 总条数
     */
    int countByUserId(int userId, String status);

    /**
     * 按分类统计指定时间区间内已完成流转的笔数与金额。
     *
     * @param from 起始时间（含）
     * @param to   结束时间（含）
     * @return 分类统计列表
     */
    List<StatisticsDTO> countByCategoryForPeriod(LocalDateTime from, LocalDateTime to);
}
