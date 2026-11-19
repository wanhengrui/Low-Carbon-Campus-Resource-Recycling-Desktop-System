package edu.campus.recycle.dao;

import edu.campus.recycle.dto.ItemQuery;
import edu.campus.recycle.dto.StatisticsDTO;
import edu.campus.recycle.entity.Item;

import java.util.List;
import java.util.Optional;

/**
 * 物品 DAO（契约第 5 节）。检索使用动态条件 + 白名单排序（策略模式），
 * 所有条件均以 {@code PreparedStatement} 参数化，杜绝 SQL 注入。
 */
public interface ItemDao extends BaseDao<Item, Integer> {

    /**
     * 插入物品并回填自增主键。
     *
     * @param item 物品
     * @return 受影响行数
     */
    @Override
    int insert(Item item);

    /**
     * 按主键查询物品。
     *
     * @param id 物品ID
     * @return 物品
     */
    Optional<Item> findById(int id);

    /**
     * 多条件检索物品。
     *
     * @param query 检索条件
     * @return 当前页物品列表
     */
    List<Item> search(ItemQuery query);

    /**
     * 统计检索命中总数。
     *
     * @param query 检索条件
     * @return 总条数
     */
    int countSearch(ItemQuery query);

    /**
     * 更新物品状态并记录审核/下架备注。
     *
     * @param itemId 物品ID
     * @param status 目标状态
     * @param remark 备注，可为 null
     * @return 受影响行数
     */
    int updateStatus(int itemId, String status, String remark);

    /**
     * 浏览数 +1。
     *
     * @param itemId 物品ID
     * @return 受影响行数
     */
    int increaseViewCount(int itemId);

    /**
     * 收藏数增减（收藏/取消收藏时调用）。
     *
     * @param itemId 物品ID
     * @param delta  +1 或 -1
     * @return 受影响行数
     */
    int increaseFavoriteCount(int itemId, int delta);

    /**
     * 查询某用户发布的物品。
     *
     * @param ownerId 发布者ID
     * @return 物品列表
     */
    List<Item> findByOwnerId(int ownerId);

    /**
     * 按分类统计已完成流转的笔数、金额与减排量（LEFT JOIN 到分类名）。
     *
     * @return 分类统计列表
     */
    List<StatisticsDTO> countByCategory();
}
