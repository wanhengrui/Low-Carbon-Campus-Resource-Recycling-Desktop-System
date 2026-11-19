package edu.campus.recycle.util;

import edu.campus.recycle.service.AdminService;
import edu.campus.recycle.service.FavoriteService;
import edu.campus.recycle.service.ItemService;
import edu.campus.recycle.service.ReviewService;
import edu.campus.recycle.service.StatisticService;
import edu.campus.recycle.service.TradeService;
import edu.campus.recycle.service.UserService;
import edu.campus.recycle.service.impl.AdminServiceImpl;
import edu.campus.recycle.service.impl.FavoriteServiceImpl;
import edu.campus.recycle.service.impl.ItemServiceImpl;
import edu.campus.recycle.service.impl.ReviewServiceImpl;
import edu.campus.recycle.service.impl.StatisticServiceImpl;
import edu.campus.recycle.service.impl.TradeServiceImpl;
import edu.campus.recycle.service.impl.UserServiceImpl;

/**
 * 服务工厂（工厂模式）：集中完成 DAO 与领域服务的装配，上层只依赖接口。
 *
 * <p>与 {@link DaoFactory} 一起构成两级工厂：DAO 工厂负责持久化实现，服务工厂负责
 * 用例编排；两者均为进程内单例，切换实现时只需修改工厂内部代码。</p>
 */
public final class ServiceFactory {

    private static final ServiceFactory INSTANCE = new ServiceFactory();

    private final UserService userService;
    private final ItemService itemService;
    private final FavoriteService favoriteService;
    private final TradeService tradeService;
    private final ReviewService reviewService;
    private final StatisticService statisticService;
    private final AdminService adminService;

    private ServiceFactory() {
        DaoFactory dao = DaoFactory.getInstance();
        this.userService = new UserServiceImpl(dao.getUserDao(), dao.getCreditLogDao(),
                dao.getOperationLogDao(), dao.getSystemConfigDao());
        this.itemService = new ItemServiceImpl(dao.getItemDao(), dao.getItemImageDao(),
                dao.getCategoryDao(), dao.getUserDao(), dao.getTradeFlowDao(), dao.getSystemConfigDao());
        this.favoriteService = new FavoriteServiceImpl(dao.getFavoriteDao(), dao.getItemDao());
        this.tradeService = new TradeServiceImpl(dao.getTradeFlowDao(), dao.getItemDao(), dao.getUserDao(),
                dao.getTradeMessageDao(), dao.getReviewDao());
        this.reviewService = new ReviewServiceImpl(dao.getReviewDao(), dao.getTradeFlowDao(),
                dao.getUserDao(), dao.getCreditLogDao(), dao.getSystemConfigDao());
        this.statisticService = new StatisticServiceImpl(dao.getTradeFlowDao(), dao.getCategoryDao(),
                dao.getSystemConfigDao(), new DefaultCarbonFactorStrategy());
        this.adminService = new AdminServiceImpl(dao.getCategoryDao(), dao.getOperationLogDao(), dao.getUserDao());
    }

    /**
     * 全局单例。
     *
     * @return 服务工厂
     */
    public static ServiceFactory getInstance() {
        return INSTANCE;
    }

    public UserService getUserService() {
        return userService;
    }

    public ItemService getItemService() {
        return itemService;
    }

    public FavoriteService getFavoriteService() {
        return favoriteService;
    }

    public TradeService getTradeService() {
        return tradeService;
    }

    public ReviewService getReviewService() {
        return reviewService;
    }

    public StatisticService getStatisticService() {
        return statisticService;
    }

    public AdminService getAdminService() {
        return adminService;
    }
}
