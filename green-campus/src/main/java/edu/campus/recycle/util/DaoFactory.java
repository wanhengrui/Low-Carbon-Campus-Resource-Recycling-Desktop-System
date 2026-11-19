package edu.campus.recycle.util;

import edu.campus.recycle.dao.CategoryDao;
import edu.campus.recycle.dao.CreditLogDao;
import edu.campus.recycle.dao.FavoriteDao;
import edu.campus.recycle.dao.ItemDao;
import edu.campus.recycle.dao.ItemImageDao;
import edu.campus.recycle.dao.OperationLogDao;
import edu.campus.recycle.dao.ReviewDao;
import edu.campus.recycle.dao.SystemConfigDao;
import edu.campus.recycle.dao.TradeFlowDao;
import edu.campus.recycle.dao.TradeMessageDao;
import edu.campus.recycle.dao.UserDao;
import edu.campus.recycle.dao.impl.CategoryDaoImpl;
import edu.campus.recycle.dao.impl.CreditLogDaoImpl;
import edu.campus.recycle.dao.impl.FavoriteDaoImpl;
import edu.campus.recycle.dao.impl.ItemDaoImpl;
import edu.campus.recycle.dao.impl.ItemImageDaoImpl;
import edu.campus.recycle.dao.impl.OperationLogDaoImpl;
import edu.campus.recycle.dao.impl.ReviewDaoImpl;
import edu.campus.recycle.dao.impl.SystemConfigDaoImpl;
import edu.campus.recycle.dao.impl.TradeFlowDaoImpl;
import edu.campus.recycle.dao.impl.TradeMessageDaoImpl;
import edu.campus.recycle.dao.impl.UserDaoImpl;

/**
 * DAO 工厂（工厂模式，单例，契约第 8 节）。
 *
 * <p>上层（Service/UI）只依赖接口，通过工厂拿到实现；替换实现（如内存 mock）
 * 或增加缓存代理时，调用方代码不需要修改。所有 DAO 无状态，可安全复用单例。</p>
 */
public final class DaoFactory {

    private static final DaoFactory INSTANCE = new DaoFactory();

    private final UserDao userDao = new UserDaoImpl();

    private final CategoryDao categoryDao = new CategoryDaoImpl();

    private final ItemDao itemDao = new ItemDaoImpl();

    private final ItemImageDao itemImageDao = new ItemImageDaoImpl();

    private final FavoriteDao favoriteDao = new FavoriteDaoImpl();

    private final TradeMessageDao tradeMessageDao = new TradeMessageDaoImpl();

    private final TradeFlowDao tradeFlowDao = new TradeFlowDaoImpl();

    private final ReviewDao reviewDao = new ReviewDaoImpl();

    private final CreditLogDao creditLogDao = new CreditLogDaoImpl();

    private final OperationLogDao operationLogDao = new OperationLogDaoImpl();

    private final SystemConfigDao systemConfigDao = new SystemConfigDaoImpl();

    private DaoFactory() {
    }

    /**
     * 全局单例。
     *
     * @return 工厂
     */
    public static DaoFactory getInstance() {
        return INSTANCE;
    }

    public UserDao getUserDao() {
        return userDao;
    }

    public CategoryDao getCategoryDao() {
        return categoryDao;
    }

    public ItemDao getItemDao() {
        return itemDao;
    }

    public ItemImageDao getItemImageDao() {
        return itemImageDao;
    }

    public FavoriteDao getFavoriteDao() {
        return favoriteDao;
    }

    public TradeMessageDao getTradeMessageDao() {
        return tradeMessageDao;
    }

    public TradeFlowDao getTradeFlowDao() {
        return tradeFlowDao;
    }

    public ReviewDao getReviewDao() {
        return reviewDao;
    }

    public CreditLogDao getCreditLogDao() {
        return creditLogDao;
    }

    public OperationLogDao getOperationLogDao() {
        return operationLogDao;
    }

    public SystemConfigDao getSystemConfigDao() {
        return systemConfigDao;
    }
}
