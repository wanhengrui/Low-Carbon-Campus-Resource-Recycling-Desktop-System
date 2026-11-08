package edu.campus.recycle.controller;

import edu.campus.recycle.dto.ItemQuery;
import edu.campus.recycle.dto.PageResult;
import edu.campus.recycle.entity.Item;
import edu.campus.recycle.exception.AppException;
import edu.campus.recycle.service.ItemService;
import edu.campus.recycle.util.ServiceFactory;

import java.util.List;

/**
 * 物品控制器（薄壳，第 3 轮裁决 v1.1 §13-15）：发布、修改、下架、检索、详情、审核。
 *
 * <p>只做参数校验、调用 {@link ItemService}、把 {@link AppException} 转成用户文案；
 * 不访问 DAO，界面层只依赖本类。</p>
 */
public class ItemController {

    private final ItemService itemService;

    public ItemController() {
        this(ServiceFactory.getInstance().getItemService());
    }

    /**
     * 构造控制器（允许注入自定义服务实现）。
     *
     * @param itemService 物品服务
     */
    public ItemController(ItemService itemService) {
        ControllerSupport.require(itemService != null, "itemService 不能为空");
        this.itemService = itemService;
    }

    /**
     * 发布物品（含图片，同一事务）。
     *
     * @return 用户可读结果文案
     */
    public String publish(Item item, List<String> imagePaths) {
        ControllerSupport.require(item != null, "物品信息不能为空");
        try {
            Item published = itemService.publish(item, imagePaths);
            return "发布成功：itemId=" + published.getId() + "，状态=" + published.getStatus()
                    + "，价格=" + published.getPrice();
        } catch (AppException e) {
            return ControllerSupport.text(e);
        }
    }

    /**
     * 修改物品。
     *
     * @return 用户可读结果文案
     */
    public String updateItem(Item item, int operatorId) {
        ControllerSupport.require(item != null && item.getId() != null, "待更新物品不能为空");
        try {
            itemService.updateItem(item, operatorId);
            return "物品修改成功：itemId=" + item.getId();
        } catch (AppException e) {
            return ControllerSupport.text(e);
        }
    }

    /**
     * 下架物品。
     *
     * @return 用户可读结果文案
     */
    public String offShelf(int itemId, int operatorId) {
        ControllerSupport.require(itemId > 0, "物品ID非法");
        try {
            itemService.offShelf(itemId, operatorId);
            return "物品已下架：itemId=" + itemId;
        } catch (AppException e) {
            return ControllerSupport.text(e);
        }
    }

    /**
     * 管理员审核（通过/驳回）。
     *
     * @return 用户可读结果文案
     */
    public String audit(int operatorId, int itemId, boolean pass, String remark) {
        ControllerSupport.require(itemId > 0, "物品ID非法");
        try {
            itemService.audit(operatorId, itemId, pass, remark);
            return pass ? "审核通过：itemId=" + itemId : "审核驳回：itemId=" + itemId;
        } catch (AppException e) {
            return ControllerSupport.text(e);
        }
    }

    /**
     * 检索物品（关键词/分类/价格区间/交易方式/状态/排序/分页）。
     */
    public PageResult<Item> search(ItemQuery query) {
        return itemService.search(query == null ? new ItemQuery() : query);
    }

    /**
     * 物品详情（同时累加浏览数）。
     *
     * @return 物品，不存在时返回 null
     */
    public Item detail(int itemId) {
        ControllerSupport.require(itemId > 0, "物品ID非法");
        try {
            return itemService.detail(itemId);
        } catch (AppException e) {
            return null;
        }
    }
}
