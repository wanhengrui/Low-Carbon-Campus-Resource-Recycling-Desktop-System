package edu.campus.recycle.dao;

import edu.campus.recycle.entity.TradeMessage;

import java.util.List;

/**
 * 流转沟通消息 DAO（契约第 5 节）。消息按物品 + 双方用户组成会话。
 */
public interface TradeMessageDao extends BaseDao<TradeMessage, Integer> {

    /**
     * 新增消息。
     *
     * @param m 消息
     * @return 受影响行数
     */
    @Override
    int insert(TradeMessage m);

    /**
     * 查询指定物品下两名用户之间的会话（双向，按时间升序）。
     *
     * @param userId      当前用户
     * @param otherUserId 对方用户
     * @param itemId      物品ID
     * @return 消息列表
     */
    List<TradeMessage> findConversation(int userId, int otherUserId, int itemId);

    /**
     * 将某物品下发给指定用户的消息全部标记为已读。
     *
     * @param toUserId 接收者
     * @param itemId   物品ID
     * @return 更新条数
     */
    int markRead(int toUserId, int itemId);

    /**
     * 统计用户未读消息数。
     *
     * @param userId 接收者用户ID
     * @return 未读条数
     */
    int countUnread(int userId);
}
