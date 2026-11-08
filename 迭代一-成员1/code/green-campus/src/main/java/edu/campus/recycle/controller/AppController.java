package edu.campus.recycle.controller;

import edu.campus.recycle.config.DatabaseInitializer;
import edu.campus.recycle.dto.ItemQuery;
import edu.campus.recycle.dto.LoginResult;
import edu.campus.recycle.dto.PageResult;
import edu.campus.recycle.dto.StatisticsDTO;
import edu.campus.recycle.entity.Item;
import edu.campus.recycle.entity.TradeFlow;
import edu.campus.recycle.entity.User;
import edu.campus.recycle.service.FavoriteService;
import edu.campus.recycle.service.ItemService;
import edu.campus.recycle.service.ReviewService;
import edu.campus.recycle.service.StatisticService;
import edu.campus.recycle.service.TradeService;
import edu.campus.recycle.service.UserService;
import edu.campus.recycle.util.ServiceFactory;

import java.time.LocalDateTime;
import java.util.List;

/**
 * 应用控制器骨架：位于 UI 与 Service 之间，负责会话状态（当前登录用户）编排。
 *
 * <p>迭代一的 Swing 界面由成员3实现，本类只提供与界面无关的调用入口；
 * 控制器不直接访问 DAO，全部经由 {@link ServiceFactory} 装配的服务接口。</p>
 */
public class AppController {

    private final UserService userService;
    private final ItemService itemService;
    private final FavoriteService favoriteService;
    private final TradeService tradeService;
    private final ReviewService reviewService;
    private final StatisticService statisticService;

    private User currentUser;

    public AppController() {
        ServiceFactory factory = ServiceFactory.getInstance();
        this.userService = factory.getUserService();
        this.itemService = factory.getItemService();
        this.favoriteService = factory.getFavoriteService();
        this.tradeService = factory.getTradeService();
        this.reviewService = factory.getReviewService();
        this.statisticService = factory.getStatisticService();
    }

    /**
     * 初始化数据库（界面启动时调用一次）。
     */
    public void bootstrapDatabase() {
        DatabaseInitializer.initialize();
    }

    /**
     * 登录并记录会话。
     *
     * @return 登录结果
     */
    public LoginResult login(String username, String rawPassword) {
        LoginResult result = userService.login(username, rawPassword);
        this.currentUser = userService.findById(result.getUserId());
        return result;
    }

    /**
     * 退出登录。
     */
    public void logout() {
        this.currentUser = null;
    }

    public User getCurrentUser() {
        return currentUser;
    }

    public Item publishItem(Item item, List<String> imagePaths) {
        return itemService.publish(item, imagePaths);
    }

    public PageResult<Item> searchItems(ItemQuery query) {
        return itemService.search(query);
    }

    public Item itemDetail(int itemId) {
        return itemService.detail(itemId);
    }

    public TradeFlow applyTrade(int itemId, String remark) {
        if (currentUser == null) {
            throw new IllegalStateException("请先登录");
        }
        return tradeService.apply(itemId, currentUser.getId(), remark);
    }

    public void confirmTrade(int flowId) {
        if (currentUser == null) {
            throw new IllegalStateException("请先登录");
        }
        tradeService.confirm(flowId, currentUser.getId());
    }

    public boolean toggleFavorite(int itemId) {
        if (currentUser == null) {
            throw new IllegalStateException("请先登录");
        }
        return favoriteService.toggle(currentUser.getId(), itemId);
    }

    public List<StatisticsDTO> statistics() {
        LocalDateTime now = LocalDateTime.now();
        return statisticService.statisticsByCategory(LocalDateTime.of(2000, 1, 1, 0, 0), now);
    }
}
