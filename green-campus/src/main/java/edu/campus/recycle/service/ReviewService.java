package edu.campus.recycle.service;

import edu.campus.recycle.entity.Review;
import edu.campus.recycle.exception.BusinessRuleException;
import edu.campus.recycle.exception.DuplicateEntityException;

/**
 * 评价服务（BR-08：仅已完成流转可评价，每人每流转一次）。
 */
public interface ReviewService {

    Review review(int flowId, int reviewerId, int score, String content)
            throws BusinessRuleException, DuplicateEntityException;
}
