package edu.campus.recycle.service.impl;

import edu.campus.recycle.dao.CreditLogDao;
import edu.campus.recycle.dao.ReviewDao;
import edu.campus.recycle.dao.SystemConfigDao;
import edu.campus.recycle.dao.TradeFlowDao;
import edu.campus.recycle.dao.UserDao;
import edu.campus.recycle.entity.FlowStatus;
import edu.campus.recycle.entity.Review;
import edu.campus.recycle.entity.TradeFlow;
import edu.campus.recycle.exception.BusinessRuleException;
import edu.campus.recycle.exception.DuplicateEntityException;
import edu.campus.recycle.exception.EntityNotFoundException;
import edu.campus.recycle.exception.PermissionDeniedException;
import edu.campus.recycle.exception.ValidationException;
import edu.campus.recycle.service.ReviewService;
import edu.campus.recycle.util.CreditRules;
import edu.campus.recycle.util.DbUtil;
import edu.campus.recycle.util.ItemEvent;
import edu.campus.recycle.util.ItemEventBus;

import java.time.LocalDateTime;
import java.util.Objects;

/**
 * 评价服务实现：评价落库与对方信用分调整在同一事务内完成（BR-07 / BR-08）。
 */
public class ReviewServiceImpl implements ReviewService {

    private static final LoggerGuard GUARD = new LoggerGuard();

    private final ReviewDao reviewDao;
    private final TradeFlowDao tradeFlowDao;
    private final UserDao userDao;
    private final CreditLogDao creditLogDao;
    private final SystemConfigDao systemConfigDao;

    public ReviewServiceImpl(ReviewDao reviewDao, TradeFlowDao tradeFlowDao, UserDao userDao,
                             CreditLogDao creditLogDao, SystemConfigDao systemConfigDao) {
        this.reviewDao = Objects.requireNonNull(reviewDao, "reviewDao");
        this.tradeFlowDao = Objects.requireNonNull(tradeFlowDao, "tradeFlowDao");
        this.userDao = Objects.requireNonNull(userDao, "userDao");
        this.creditLogDao = Objects.requireNonNull(creditLogDao, "creditLogDao");
        this.systemConfigDao = Objects.requireNonNull(systemConfigDao, "systemConfigDao");
    }

    @Override
    public Review review(int flowId, int reviewerId, int score, String content)
            throws BusinessRuleException, DuplicateEntityException {
        if (score < 1 || score > 5) {
            throw ValidationException.of("评分必须为 1-5 分");
        }
        if (content != null && content.length() > 200) {
            throw ValidationException.of("评价内容不能超过 200 字");
        }
        TradeFlow flow = tradeFlowDao.findById(flowId)
                .orElseThrow(() -> EntityNotFoundException.of("流转记录不存在：id=" + flowId));
        if (!FlowStatus.DONE.getCode().equals(flow.getStatus())) {
            throw BusinessRuleException.of("BR-08", "仅已完成的流转可评价");
        }
        boolean participant = Objects.equals(flow.getSellerId(), reviewerId)
                || Objects.equals(flow.getBuyerId(), reviewerId);
        if (!participant) {
            throw PermissionDeniedException.of("仅交易双方可评价该流转");
        }
        if (reviewDao.existsByFlowAndReviewer(flowId, reviewerId)) {
            throw DuplicateEntityException.of("您已评价过该笔流转，不可重复评价");
        }
        int revieweeId = Objects.equals(flow.getSellerId(), reviewerId)
                ? flow.getBuyerId() : flow.getSellerId();
        Review review = new Review();
        review.setFlowId(flowId);
        review.setReviewerId(reviewerId);
        review.setRevieweeId(revieweeId);
        review.setScore(score);
        review.setContent(content == null ? "" : content.trim());
        review.setCreatedAt(LocalDateTime.now().withNano(0));
        int delta = creditDelta(score);
        DbUtil.getInstance().executeInTransaction(conn -> {
            reviewDao.insert(review);
            if (delta != 0) {
                CreditRules.apply(userDao, creditLogDao, revieweeId, delta, flowId,
                        "收到评价（" + score + " 分）信用分调整");
            }
            ItemEventBus.getInstance().publish(
                    ItemEvent.of(ItemEvent.Type.REVIEW_CREATED, flow.getItemId(), flowId, reviewerId,
                            "评价 " + score + " 分"));
            return null;
        });
        GUARD.info(() -> "评价成功：flowId=" + flowId + "，reviewerId=" + reviewerId + "，score=" + score);
        return review;
    }

    /**
     * 评价信用分规则：4-5 分奖励（credit.trade_bonus），1-2 分惩罚（credit.bad_review_penalty），3 分不变。
     */
    private int creditDelta(int score) {
        if (score >= 4) {
            return systemConfigDao.getInt("credit.trade_bonus", 2);
        }
        if (score <= 2) {
            return systemConfigDao.getInt("credit.bad_review_penalty", -5);
        }
        return 0;
    }

    /**
     * 轻量日志持有者（避免静态 Logger 字段与 checkstyle 冲突的占位实现）。
     */
    private static final class LoggerGuard {
        private final java.util.logging.Logger logger =
                java.util.logging.Logger.getLogger(ReviewServiceImpl.class.getName());

        void info(java.util.function.Supplier<String> message) {
            logger.info(message);
        }
    }
}
