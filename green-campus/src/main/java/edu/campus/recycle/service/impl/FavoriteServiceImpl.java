package edu.campus.recycle.service.impl;

import edu.campus.recycle.dao.FavoriteDao;
import edu.campus.recycle.dao.ItemDao;
import edu.campus.recycle.entity.Favorite;
import edu.campus.recycle.entity.Item;
import edu.campus.recycle.exception.EntityNotFoundException;
import edu.campus.recycle.service.FavoriteService;
import edu.campus.recycle.util.DbUtil;

import java.time.LocalDateTime;
import java.util.List;
import java.util.Objects;

/**
 * 收藏服务实现：toggle 采用「同一事务内判断存在性 + 插入/删除 + 计数维护」，
 * 避免并发下重复收藏（BR-09）。
 */
public class FavoriteServiceImpl implements FavoriteService {

    private final FavoriteDao favoriteDao;
    private final ItemDao itemDao;

    public FavoriteServiceImpl(FavoriteDao favoriteDao, ItemDao itemDao) {
        this.favoriteDao = Objects.requireNonNull(favoriteDao, "favoriteDao");
        this.itemDao = Objects.requireNonNull(itemDao, "itemDao");
    }

    @Override
    public boolean toggle(int userId, int itemId) {
        itemDao.findById(itemId)
                .orElseThrow(() -> EntityNotFoundException.of("物品不存在：id=" + itemId));
        return DbUtil.getInstance().executeInTransaction(conn -> {
            if (favoriteDao.exists(userId, itemId)) {
                favoriteDao.delete(userId, itemId);
                itemDao.increaseFavoriteCount(itemId, -1);
                return Boolean.FALSE;
            }
            Favorite favorite = new Favorite();
            favorite.setUserId(userId);
            favorite.setItemId(itemId);
            favorite.setCreatedAt(LocalDateTime.now().withNano(0));
            favoriteDao.insert(favorite);
            itemDao.increaseFavoriteCount(itemId, 1);
            return Boolean.TRUE;
        });
    }

    @Override
    public List<Item> listByUser(int userId) {
        return favoriteDao.findItemsByUserId(userId);
    }
}
