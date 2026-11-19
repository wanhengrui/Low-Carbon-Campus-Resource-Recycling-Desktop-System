package edu.campus.recycle.util;

import edu.campus.recycle.dao.CreditLogDao;
import edu.campus.recycle.dao.TradeFlowDao;
import edu.campus.recycle.dao.UserDao;

/**
 * 信用分监听器：流转完成后给双方增加信用分并写入 {@code credit_log} 快照（BR-04/BR-07）。
 *
 * <p>只在 {@link ItemEvent.Type#FLOW_DONE} 时生效，其它事件忽略。</p>
 *
 * <p>第 3 轮裁决（v1.1）§4-5：构造时注入 {@link TradeFlowDao}，经由
 * {@link CreditRules} 查询参与方，不再使用 {@link DaoFactory} 静态直取。</p>
 */
public class CreditChangeListener implements ItemEventListener {

    /** 完成一次流转，出让方/受让方各加 2 分 */
    public static final int FLOW_DONE_DELTA = 2;

    private final UserDao userDao;

    private final CreditLogDao creditLogDao;

    private final CreditRules creditRules;

    public CreditChangeListener(UserDao userDao, CreditLogDao creditLogDao, TradeFlowDao tradeFlowDao) {
        this.userDao = userDao;
        this.creditLogDao = creditLogDao;
        this.creditRules = new CreditRules(tradeFlowDao);
    }

    @Override
    public void onEvent(ItemEvent event) {
        if (event.getType() != ItemEvent.Type.FLOW_DONE || event.getFlowId() == null) {
            return;
        }
        Integer sellerId = creditRules.findParticipant(event.getFlowId(), true);
        Integer buyerId = creditRules.findParticipant(event.getFlowId(), false);
        if (sellerId != null) {
            CreditRules.apply(userDao, creditLogDao, sellerId, FLOW_DONE_DELTA, event.getFlowId(),
                    "完成流转（出让方）");
        }
        if (buyerId != null) {
            CreditRules.apply(userDao, creditLogDao, buyerId, FLOW_DONE_DELTA, event.getFlowId(),
                    "完成流转（受让方）");
        }
    }
}
