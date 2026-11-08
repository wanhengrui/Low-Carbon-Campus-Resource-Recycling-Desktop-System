package edu.campus.recycle.service.impl;

import edu.campus.recycle.dao.ItemDao;
import edu.campus.recycle.dao.ReviewDao;
import edu.campus.recycle.dao.TradeFlowDao;
import edu.campus.recycle.dao.TradeMessageDao;
import edu.campus.recycle.dao.UserDao;
import edu.campus.recycle.dto.TradeDetailDTO;
import edu.campus.recycle.entity.FlowStatus;
import edu.campus.recycle.entity.Item;
import edu.campus.recycle.entity.ItemStatus;
import edu.campus.recycle.entity.Review;
import edu.campus.recycle.entity.Role;
import edu.campus.recycle.entity.TradeFlow;
import edu.campus.recycle.entity.TradeMessage;
import edu.campus.recycle.entity.TradeType;
import edu.campus.recycle.entity.User;
import edu.campus.recycle.entity.UserStatus;
import edu.campus.recycle.exception.BusinessRuleException;
import edu.campus.recycle.exception.EntityNotFoundException;
import edu.campus.recycle.exception.PermissionDeniedException;
import edu.campus.recycle.service.TradeService;
import edu.campus.recycle.util.DbUtil;
import edu.campus.recycle.util.ItemEvent;
import edu.campus.recycle.util.ItemEventBus;

import java.math.BigDecimal;
import java.time.LocalDateTime;
import java.util.ArrayList;
import java.util.List;
import java.util.Objects;
import java.util.logging.Logger;

/**
 * 流转服务实现。
 *
 * <p>核心 {@link #confirm(int, int)} 在一个事务内完成：物品置 SOLD、流转置 DONE、
 * 信用分变更（观察者）、操作日志（观察者）、统计累加（观察者）；任一步失败整体回滚（BR-07）。</p>
 *
 * <p>第 3 轮裁决（v1.1）：取消权限放宽为"买卖双方或 ADMIN"（§13-7）；
 * 新增 {@link #historyDetail(int, String, int, int)} 与 {@link #countUnread(int)}（§13-14）。</p>
 */
public class TradeServiceImpl implements TradeService {

    private static final Logger LOG = Logger.getLogger(TradeServiceImpl.class.getName());

    private final TradeFlowDao tradeFlowDao;
    private final ItemDao itemDao;
    private final UserDao userDao;
    private final TradeMessageDao tradeMessageDao;
    private final ReviewDao reviewDao;

    public TradeServiceImpl(TradeFlowDao tradeFlowDao, ItemDao itemDao, UserDao userDao,
                            TradeMessageDao tradeMessageDao, ReviewDao reviewDao) {
        this.tradeFlowDao = Objects.requireNonNull(tradeFlowDao, "tradeFlowDao");
        this.itemDao = Objects.requireNonNull(itemDao, "itemDao");
        this.userDao = Objects.requireNonNull(userDao, "userDao");
        this.tradeMessageDao = Objects.requireNonNull(tradeMessageDao, "tradeMessageDao");
        this.reviewDao = Objects.requireNonNull(reviewDao, "reviewDao");
    }

    @Override
    public TradeFlow apply(int itemId, int buyerId, String remark)
            throws BusinessRuleException, EntityNotFoundException {
        Item item = itemDao.findById(itemId)
                .orElseThrow(() -> EntityNotFoundException.of("物品不存在：id=" + itemId));
        if (Objects.equals(item.getOwnerId(), buyerId)) {
            throw BusinessRuleException.of("BR-06", "不能申请自己发布的物品");
        }
        if (!ItemStatus.ON_SALE.getCode().equals(item.getStatus())) {
            throw BusinessRuleException.of("BR-06", "仅「在售」物品可发起流转申请，当前：" + item.getStatus());
        }
        User buyer = userDao.findById(buyerId)
                .orElseThrow(() -> EntityNotFoundException.of("申请用户不存在：id=" + buyerId));
        if (!UserStatus.ACTIVE.getCode().equals(buyer.getStatus())) {
            throw BusinessRuleException.of("BR-06", "账号状态异常，无法发起流转");
        }
        if (tradeFlowDao.findActiveByItemId(itemId).isPresent()) {
            throw BusinessRuleException.of("BR-05", "该物品已有进行中的流转，不可重复申请");
        }
        LocalDateTime now = LocalDateTime.now().withNano(0);
        TradeFlow flow = new TradeFlow();
        flow.setItemId(itemId);
        flow.setSellerId(item.getOwnerId());
        flow.setBuyerId(buyerId);
        flow.setFlowType(item.getTradeType());
        flow.setAmount(TradeType.SELL.getCode().equals(item.getTradeType())
                ? (item.getPrice() == null ? BigDecimal.ZERO : item.getPrice()) : BigDecimal.ZERO);
        flow.setStatus(FlowStatus.APPLYING.getCode());
        flow.setApplyRemark(remark);
        flow.setCreatedAt(now);
        DbUtil.getInstance().executeInTransaction(conn -> {
            tradeFlowDao.insert(flow);
            ItemEventBus.getInstance().publish(
                    ItemEvent.of(ItemEvent.Type.FLOW_APPLIED, itemId, flow.getId(), buyerId, "发起流转申请"));
            return null;
        });
        LOG.info(() -> "流转申请成功：flowId=" + flow.getId() + "，itemId=" + itemId);
        return flow;
    }

    @Override
    public void agree(int flowId, int operatorId) throws PermissionDeniedException, BusinessRuleException {
        TradeFlow flow = tradeFlowDao.findById(flowId)
                .orElseThrow(() -> EntityNotFoundException.of("流转记录不存在：id=" + flowId));
        if (!Objects.equals(flow.getSellerId(), operatorId)) {
            throw PermissionDeniedException.of("仅物品发布者可同意该流转申请");
        }
        if (!FlowStatus.APPLYING.getCode().equals(flow.getStatus())) {
            throw BusinessRuleException.of("BR-06", "仅「申请中」的流转可同意，当前：" + flow.getStatus());
        }
        DbUtil.getInstance().executeInTransaction(conn -> {
            tradeFlowDao.updateStatus(flowId, FlowStatus.AGREED.getCode(), null, null);
            itemDao.updateStatus(flow.getItemId(), ItemStatus.LOCKED.getCode(), null);
            ItemEventBus.getInstance().publish(
                    ItemEvent.flow(ItemEvent.Type.FLOW_AGREED, flow, operatorId, "同意流转申请"));
            return null;
        });
    }

    @Override
    public void confirm(int flowId, int operatorId) throws PermissionDeniedException, BusinessRuleException {
        DbUtil.getInstance().executeInTransaction(conn -> {
            TradeFlow flow = tradeFlowDao.findById(flowId)
                    .orElseThrow(() -> EntityNotFoundException.of("流转记录不存在：id=" + flowId));
            if (!Objects.equals(flow.getSellerId(), operatorId) && !Objects.equals(flow.getBuyerId(), operatorId)) {
                throw PermissionDeniedException.of("仅交易双方可确认成交");
            }
            if (!FlowStatus.AGREED.getCode().equals(flow.getStatus())) {
                throw BusinessRuleException.of("BR-06", "仅「已同意」的流转可确认成交，当前：" + flow.getStatus());
            }
            Item item = itemDao.findById(flow.getItemId())
                    .orElseThrow(() -> EntityNotFoundException.of("物品不存在：id=" + flow.getItemId()));
            if (ItemStatus.SOLD.getCode().equals(item.getStatus())) {
                throw BusinessRuleException.of("BR-05", "该物品已成交，不可重复成交");
            }
            LocalDateTime now = LocalDateTime.now().withNano(0);
            itemDao.updateStatus(flow.getItemId(), ItemStatus.SOLD.getCode(), null);
            tradeFlowDao.updateStatus(flowId, FlowStatus.DONE.getCode(), null, now);
            ItemEventBus.getInstance().publish(
                    ItemEvent.flow(ItemEvent.Type.FLOW_DONE, flow, operatorId, "确认成交"));
            LOG.info(() -> "确认成交成功：flowId=" + flowId + "，itemId=" + flow.getItemId());
            return null;
        });
    }

    @Override
    public void cancel(int flowId, int operatorId, String reason) throws PermissionDeniedException {
        TradeFlow flow = tradeFlowDao.findById(flowId)
                .orElseThrow(() -> EntityNotFoundException.of("流转记录不存在：id=" + flowId));
        boolean participant = Objects.equals(flow.getSellerId(), operatorId)
                || Objects.equals(flow.getBuyerId(), operatorId);
        boolean admin = userDao.findById(operatorId)
                .map(u -> Role.ADMIN.getCode().equals(u.getRole()))
                .orElse(false);
        // 第 3 轮裁决 v1.1 §13-7：买卖双方或 ADMIN 均可取消（PERM-023 语义为"非当事人且非管理员"）
        if (!participant && !admin) {
            throw PermissionDeniedException.of("仅交易双方或管理员可取消该流转");
        }
        if (!FlowStatus.APPLYING.getCode().equals(flow.getStatus())
                && !FlowStatus.AGREED.getCode().equals(flow.getStatus())) {
            throw BusinessRuleException.of("BR-06", "仅进行中的流转可取消，当前：" + flow.getStatus());
        }
        if (reason == null || reason.trim().isEmpty()) {
            throw BusinessRuleException.of("BR-06", "取消原因不能为空");
        }
        LocalDateTime now = LocalDateTime.now().withNano(0);
        DbUtil.getInstance().executeInTransaction(conn -> {
            tradeFlowDao.updateStatus(flowId, FlowStatus.CANCELLED.getCode(), reason.trim(), now);
            if (FlowStatus.AGREED.getCode().equals(flow.getStatus())) {
                itemDao.updateStatus(flow.getItemId(), ItemStatus.ON_SALE.getCode(), null);
            }
            ItemEventBus.getInstance().publish(
                    ItemEvent.flow(ItemEvent.Type.FLOW_CANCELLED, flow, operatorId, "取消流转：" + reason.trim()));
            return null;
        });
    }

    @Override
    public List<TradeFlow> history(int userId, String status, int pageNo, int pageSize) {
        int safePage = Math.max(1, pageNo);
        int safeSize = Math.min(Math.max(1, pageSize), 100);
        return tradeFlowDao.findByUserId(userId, status, safePage, safeSize);
    }

    @Override
    public List<TradeDetailDTO> historyDetail(int userId, String status, int pageNo, int pageSize) {
        int safePage = Math.max(1, pageNo);
        int safeSize = Math.min(Math.max(1, pageSize), 100);
        List<TradeFlow> flows = tradeFlowDao.findByUserId(userId, status, safePage, safeSize);
        List<TradeDetailDTO> details = new ArrayList<>(flows.size());
        for (TradeFlow flow : flows) {
            Item item = itemDao.findById(flow.getItemId()).orElse(null);
            User seller = userDao.findById(flow.getSellerId()).orElse(null);
            User buyer = userDao.findById(flow.getBuyerId()).orElse(null);
            int otherUserId = Objects.equals(flow.getSellerId(), userId)
                    ? flow.getBuyerId() : flow.getSellerId();
            List<TradeMessage> messages = tradeMessageDao.findConversation(userId, otherUserId, flow.getItemId());
            List<Review> reviews = reviewDao.findByFlowId(flow.getId());
            details.add(new TradeDetailDTO(flow, item, seller, buyer, messages, reviews));
        }
        return details;
    }

    @Override
    public int countUnread(int userId) {
        if (userId <= 0) {
            return 0;
        }
        return tradeMessageDao.countUnread(userId);
    }
}
