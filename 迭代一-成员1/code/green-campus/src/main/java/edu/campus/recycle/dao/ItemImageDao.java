package edu.campus.recycle.dao;

import edu.campus.recycle.entity.ItemImage;

import java.util.List;

/**
 * 物品图片 DAO（契约第 5 节）。图片只存相对路径，二进制不入库（BR-12）。
 */
public interface ItemImageDao extends BaseDao<ItemImage, Integer> {

    /**
     * 批量插入图片（单事务）。
     *
     * @param images 图片列表
     * @return 成功插入条数
     */
    int batchInsert(List<ItemImage> images);

    /**
     * 按物品查询图片（按 sort_order 升序）。
     *
     * @param itemId 物品ID
     * @return 图片列表
     */
    List<ItemImage> findByItemId(int itemId);

    /**
     * 删除某物品的全部图片。
     *
     * @param itemId 物品ID
     * @return 删除条数
     */
    int deleteByItemId(int itemId);
}
