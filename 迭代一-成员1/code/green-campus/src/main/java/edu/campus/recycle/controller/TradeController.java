package edu.campus.recycle.controller;

import edu.campus.recycle.dto.TradeDetailDTO;
import edu.campus.recycle.entity.TradeFlow;
import edu.campus.recycle.exception.AppException;
import edu.campus.recycle.service.TradeService;
import edu.campus.recycle.util.ServiceFactory;

import java.util.List;

/**
 * 流转控制器（薄壳，第 3 轮裁决 v1.1 §13-15）：申请、同意、成交、取消、历史与未读数。
 *
 * <p>只做参数校验、调用 {@link TradeService}、把 {@link AppException} 转成用户文案；
 * 不访问 DAO，界面层只依赖本类。</p>
 */
public class TradeController {

    private final TradeService tradeService;

    public TradeController() {
        this(ServiceFactory.getInstance().getTradeService());
    }

    /**
     * 构造控制器（允许注入自定义服务实现）。
     *
     * @param tradeService 流转服务
     */
    public TradeController(TradeService tradeService) {
        ControllerSupport.require(tradeService != null, "tradeService 不能为空");
        this.tradeService = tradeService;
    }

    /**
     * 发起流转申请。
     *
     * @return 用户可读结果文案
     */
    public String apply(int itemId, int buyerId, String remark) {
        ControllerSupport.require(itemId > 0 && buyerId > 0, "物品ID/买家ID非法");
        try {
            TradeFlow flow = tradeService.apply(itemId, buyerId, remark);
            return "申请成功：flowId=" + flow.getId() + "，金额=" + flow.getAmount();
        } catch (AppException e) {
            return ControllerSupport.text(e);
        }
    }

    /**
     * 出让方同意申请。
     *
     * @return 用户可读结果文案
     */
    public String agree(int flowId, int operatorId) {
        ControllerSupport.require(flowId > 0, "流转ID非法");
        try {
            tradeService.agree(flowId, operatorId);
            return "已同意流转：flowId=" + flowId;
        } catch (AppException e) {
            return ControllerSupport.text(e);
        }
    }

    /**
     * 确认成交（跨表事务）。
     *
     * @return 用户可读结果文案
     */
    public String confirm(int flowId, int operatorId) {
        ControllerSupport.require(flowId > 0, "流转ID非法");
        try {
            tradeService.confirm(flowId, operatorId);
            return "确认成交成功：flowId=" + flowId;
        } catch (AppException e) {
            return ControllerSupport.text(e);
        }
    }

    /**
     * 取消流转（买卖双方或管理员，原因必填）。
     *
     * @return 用户可读结果文案
     */
    public String cancel(int flowId, int operatorId, String reason) {
        ControllerSupport.require(flowId > 0, "流转ID非法");
        ControllerSupport.require(ControllerSupport.hasText(reason), "取消原因不能为空");
        try {
            tradeService.cancel(flowId, operatorId, reason);
            return "已取消流转：flowId=" + flowId;
        } catch (AppException e) {
            return ControllerSupport.text(e);
        }
    }

    /**
     * 流转历史（分页）。
     */
    public List<TradeFlow> history(int userId, String status, int pageNo, int pageSize) {
        return tradeService.history(userId, status, Math.max(1, pageNo), Math.min(Math.max(1, pageSize), 100));
    }

    /**
     * 流转历史详情（聚合物品、买卖双方、消息与评价，§13-14）。
     */
    public List<TradeDetailDTO> historyDetail(int userId, String status, int pageNo, int pageSize) {
        return tradeService.historyDetail(userId, status,
                Math.max(1, pageNo), Math.min(Math.max(1, pageSize), 100));
    }

    /**
     * 未读消息数（§13-14）。
     */
    public int countUnread(int userId) {
        return tradeService.countUnread(userId);
    }
}
