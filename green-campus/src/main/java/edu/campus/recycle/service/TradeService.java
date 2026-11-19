package edu.campus.recycle.service;

import edu.campus.recycle.dto.TradeDetailDTO;
import edu.campus.recycle.entity.TradeFlow;
import edu.campus.recycle.exception.BusinessRuleException;
import edu.campus.recycle.exception.EntityNotFoundException;
import edu.campus.recycle.exception.PermissionDeniedException;

import java.util.List;

/**
 * 流转服务：申请 → 同意 → 确认成交 → 取消，及历史查询。
 *
 * <p>方法签名逐字对齐《共享契约-实体与接口基线》第 6 节与第 3 轮裁决（v1.1）§13-14。</p>
 */
public interface TradeService {

    TradeFlow apply(int itemId, int buyerId, String remark) throws BusinessRuleException, EntityNotFoundException;

    void agree(int flowId, int operatorId) throws PermissionDeniedException, BusinessRuleException;

    /**
     * 确认成交：物品置 SOLD、流转置 DONE、信用分变更、操作日志、统计事件全部在同一事务内完成（BR-07）。
     */
    void confirm(int flowId, int operatorId) throws PermissionDeniedException, BusinessRuleException;

    void cancel(int flowId, int operatorId, String reason) throws PermissionDeniedException;

    List<TradeFlow> history(int userId, String status, int pageNo, int pageSize);

    /**
     * 流转历史详情（第 3 轮裁决 v1.1 §13-14）：一次装配流转、物品、买卖双方、
     * 沟通消息与评价，供界面层直接渲染，避免逐表往返查询。
     *
     * @param userId   当事人（出让方或受让方）
     * @param status   流转状态过滤，可为空
     * @param pageNo   页码，从 1 开始
     * @param pageSize 每页条数
     * @return 详情列表，按创建时间倒序
     */
    List<TradeDetailDTO> historyDetail(int userId, String status, int pageNo, int pageSize);

    /**
     * 未读消息数（第 3 轮裁决 v1.1 §13-14）。
     *
     * @param userId 接收者
     * @return 未读条数
     */
    int countUnread(int userId);
}
