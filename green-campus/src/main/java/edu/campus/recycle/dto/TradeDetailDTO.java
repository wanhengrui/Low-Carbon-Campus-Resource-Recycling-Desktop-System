package edu.campus.recycle.dto;

import edu.campus.recycle.entity.Item;
import edu.campus.recycle.entity.Review;
import edu.campus.recycle.entity.TradeFlow;
import edu.campus.recycle.entity.TradeMessage;
import edu.campus.recycle.entity.User;

import java.util.ArrayList;
import java.util.List;

/**
 * 流转详情聚合对象（契约第 4 节）：一次查询装配流转、物品、买卖双方、沟通消息与评价，
 * 避免界面层逐表拼接产生的多次往返查询。
 */
public class TradeDetailDTO {

    /** 流转记录 */
    private TradeFlow flow;
    /** 关联物品 */
    private Item item;
    /** 出让方 */
    private User seller;
    /** 受让方 */
    private User buyer;
    /** 沟通消息 */
    private List<TradeMessage> messages = new ArrayList<>();
    /** 双方评价 */
    private List<Review> reviews = new ArrayList<>();

    public TradeDetailDTO() {
    }

    public TradeDetailDTO(TradeFlow flow, Item item, User seller, User buyer,
                          List<TradeMessage> messages, List<Review> reviews) {
        this.flow = flow;
        this.item = item;
        this.seller = seller;
        this.buyer = buyer;
        this.messages = messages == null ? new ArrayList<>() : messages;
        this.reviews = reviews == null ? new ArrayList<>() : reviews;
    }

    public TradeFlow getFlow() {
        return flow;
    }

    public void setFlow(TradeFlow flow) {
        this.flow = flow;
    }

    public Item getItem() {
        return item;
    }

    public void setItem(Item item) {
        this.item = item;
    }

    public User getSeller() {
        return seller;
    }

    public void setSeller(User seller) {
        this.seller = seller;
    }

    public User getBuyer() {
        return buyer;
    }

    public void setBuyer(User buyer) {
        this.buyer = buyer;
    }

    public List<TradeMessage> getMessages() {
        return messages;
    }

    public void setMessages(List<TradeMessage> messages) {
        this.messages = messages;
    }

    public List<Review> getReviews() {
        return reviews;
    }

    public void setReviews(List<Review> reviews) {
        this.reviews = reviews;
    }

    @Override
    public String toString() {
        return "TradeDetailDTO{flow=" + (flow == null ? null : flow.getId())
                + ", item=" + (item == null ? null : item.getId())
                + ", seller=" + (seller == null ? null : seller.getId())
                + ", buyer=" + (buyer == null ? null : buyer.getId())
                + ", messages=" + messages.size() + ", reviews=" + reviews.size() + '}';
    }
}
