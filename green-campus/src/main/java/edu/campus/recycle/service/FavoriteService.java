package edu.campus.recycle.service;

import edu.campus.recycle.entity.Item;

import java.util.List;

/**
 * 收藏服务（BR-09：同一用户对同一物品收藏为开关式切换）。
 */
public interface FavoriteService {

    /**
     * 收藏/取消收藏，返回切换后的收藏状态。
     *
     * @return {@code true} 表示已收藏，{@code false} 表示已取消
     */
    boolean toggle(int userId, int itemId);

    List<Item> listByUser(int userId);
}
