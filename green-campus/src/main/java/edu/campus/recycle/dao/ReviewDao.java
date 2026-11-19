package edu.campus.recycle.dao;

import edu.campus.recycle.entity.Review;

import java.util.List;

/**
 * 评价 DAO（契约第 5 节）。{@code UNIQUE(flow_id, reviewer_id)} 保证同一流转每人只评一次（BR-08）。
 */
public interface ReviewDao extends BaseDao<Review, Integer> {

    /**
     * 新增评价。
     *
     * @param r 评价
     * @return 受影响行数
     */
    @Override
    int insert(Review r);

    /**
     * 查询某流转下的全部评价（出让方与受让方各至多一条，BR-08）。
     *
     * <p>为 {@code TradeService.historyDetail} 的详情聚合提供数据支撑（第 3 轮裁决 v1.1 §13-14），
     * 属契约第 5 节的增补方法，已在 D5 第 10 章一致性差异中登记。</p>
     *
     * @param flowId 流转ID
     * @return 评价列表
     */
    List<Review> findByFlowId(int flowId);

    /**
     * 判断某用户是否已评价过该流转。
     *
     * @param flowId     流转ID
     * @param reviewerId 评价人
     * @return 已评价返回 true
     */
    boolean existsByFlowAndReviewer(int flowId, int reviewerId);

    /**
     * 查询某用户收到的评价。
     *
     * @param revieweeId 被评价人
     * @return 评价列表
     */
    List<Review> findByRevieweeId(int revieweeId);

    /**
     * 计算某用户收到的平均评分。
     *
     * @param revieweeId 被评价人
     * @return 平均分（无评价时返回 0）
     */
    double avgScoreByRevieweeId(int revieweeId);
}
