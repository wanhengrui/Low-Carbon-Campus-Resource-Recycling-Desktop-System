package edu.campus.recycle.controller;

import edu.campus.recycle.entity.Review;
import edu.campus.recycle.exception.AppException;
import edu.campus.recycle.service.ReviewService;
import edu.campus.recycle.util.ServiceFactory;

/**
 * 评价控制器（薄壳，第 3 轮裁决 v1.1 §13-15）：成交后双方互评（BR-08）。
 *
 * <p>只做参数校验、调用 {@link ReviewService}、把 {@link AppException} 转成用户文案。</p>
 */
public class ReviewController {

    private final ReviewService reviewService;

    public ReviewController() {
        this(ServiceFactory.getInstance().getReviewService());
    }

    /**
     * 构造控制器（允许注入自定义服务实现）。
     *
     * @param reviewService 评价服务
     */
    public ReviewController(ReviewService reviewService) {
        ControllerSupport.require(reviewService != null, "reviewService 不能为空");
        this.reviewService = reviewService;
    }

    /**
     * 提交评价（评分 1-5，仅已成交流转，每人一次）。
     *
     * @return 用户可读结果文案
     */
    public String review(int flowId, int reviewerId, int score, String content) {
        ControllerSupport.require(flowId > 0, "流转ID非法");
        ControllerSupport.require(score >= 1 && score <= 5, "评分必须为 1-5");
        try {
            Review review = reviewService.review(flowId, reviewerId, score, content);
            return "评价成功：reviewId=" + review.getId() + "，评分=" + review.getScore();
        } catch (AppException e) {
            return ControllerSupport.text(e);
        }
    }
}
