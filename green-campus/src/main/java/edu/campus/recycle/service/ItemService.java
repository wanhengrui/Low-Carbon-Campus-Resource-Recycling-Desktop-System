package edu.campus.recycle.service;

import edu.campus.recycle.dto.ItemQuery;
import edu.campus.recycle.dto.PageResult;
import edu.campus.recycle.entity.Item;
import edu.campus.recycle.exception.BusinessRuleException;
import edu.campus.recycle.exception.EntityNotFoundException;
import edu.campus.recycle.exception.PermissionDeniedException;
import edu.campus.recycle.exception.ValidationException;

import java.util.List;

/**
 * 物品服务：发布（含图片，同一事务）、修改、下架、检索、详情、审核。
 *
 * <p>方法签名逐字对齐《共享契约-实体与接口基线》第 6 节。</p>
 */
public interface ItemService {

    /**
     * 发布物品并批量保存图片（BR-04 信用分门槛、BR-12 图片规则）。
     *
     * @param item       物品实体（ownerId/categoryId/title 必填）
     * @param imagePaths 图片相对路径列表，可为空
     * @return 已回填主键的物品
     */
    Item publish(Item item, List<String> imagePaths) throws ValidationException, BusinessRuleException;

    void updateItem(Item item, int operatorId) throws PermissionDeniedException, EntityNotFoundException;

    void offShelf(int itemId, int operatorId) throws PermissionDeniedException;

    PageResult<Item> search(ItemQuery query);

    Item detail(int itemId) throws EntityNotFoundException;

    void audit(int operatorId, int itemId, boolean pass, String remark) throws PermissionDeniedException;
}
