package edu.campus.recycle.dao;

import edu.campus.recycle.entity.Favorite;
import edu.campus.recycle.entity.Item;

import java.util.List;

/**
 * 收藏 DAO（契约第 5 节）。{@code UNIQUE(user_id, item_id)} 保证收藏唯一，
 * Service 层以 toggle 语义调用（BR-09）。
 */
public interface FavoriteDao extends BaseDao<Favorite, Integer> {

    /**
     * 判断是否已收藏。
     *
     * @param userId 用户ID
     * @param itemId 物品ID
     * @return 已收藏返回 true
     */
    boolean exists(int userId, int itemId);

    /**
     * 新增收藏。
     *
     * @param f 收藏记录
     * @return 受影响行数
     */
    int insert(Favorite f);

    /**
     * 取消收藏。
     *
     * @param userId 用户ID
     * @param itemId 物品ID
     * @return 受影响行数
     */
    int delete(int userId, int itemId);

    /**
     * 查询某用户收藏的物品（联表返回物品视图数据）。
     *
     * @param userId 用户ID
     * @return 物品列表
     */
    List<Item> findItemsByUserId(int userId);

    /**
     * 统计某物品被收藏次数。
     *
     * @param itemId 物品ID
     * @return 收藏数
     */
    int countByItemId(int itemId);
}
