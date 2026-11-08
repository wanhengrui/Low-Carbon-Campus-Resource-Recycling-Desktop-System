package edu.campus.recycle.util;

import edu.campus.recycle.dao.CreditLogDao;
import edu.campus.recycle.dao.TradeFlowDao;
import edu.campus.recycle.dao.UserDao;
import edu.campus.recycle.entity.CreditLog;
import edu.campus.recycle.entity.TradeFlow;
import edu.campus.recycle.entity.User;

import java.time.LocalDateTime;
import java.util.Objects;

/**
 * 信用分变更规则（公共逻辑，避免监听器与 UserService 重复实现）。
 *
 * <p>区间约束 [0,150] 在此统一裁剪，并保证"更新用户分数 + 写 credit_log 快照"
 * 在同一连接/事务中完成（BR-04）。</p>
 *
 * <p>第 3 轮裁决（v1.1）§4-5：参与方查询改为<b>构造函数注入</b> {@link TradeFlowDao}，
 * 去掉对 {@link DaoFactory} 的静态直取，便于单元测试替换假实现。</p>
 */
public final class CreditRules {

    /** 信用分下限 */
    public static final int MIN_SCORE = 0;

    /** 信用分上限 */
    public static final int MAX_SCORE = 150;

    /** 流转 DAO（构造注入，无静态工厂依赖） */
    private final TradeFlowDao tradeFlowDao;

    /**
     * 构造信用规则协助对象。
     *
     * @param tradeFlowDao 流转 DAO，用于查询流转参与方
     */
    public CreditRules(TradeFlowDao tradeFlowDao) {
        this.tradeFlowDao = Objects.requireNonNull(tradeFlowDao, "tradeFlowDao");
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
     * @param flowId 流转ID
     * @param seller true 查出让方，false 查受让方
     * @return 用户ID，流转不存在时返回 null
     */
    public Integer findParticipant(int flowId, boolean seller) {
        TradeFlow flow = tradeFlowDao.findById(flowId).orElse(null);
        if (flow == null) {
            return null;
        }
        return seller ? flow.getSellerId() : flow.getBuyerId();
    }
}
