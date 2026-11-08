package edu.campus.recycle.dto;

import java.util.ArrayList;
import java.util.List;

/**
 * 分页结果（契约第 4 节），同时携带记录、总数与页码信息，
 * 由 {@link #of(List, long, int, int)} 统一计算总页数。
 *
 * @param <T> 记录类型
 */
public class PageResult<T> {

    /** 当前页记录 */
    private List<T> records = new ArrayList<>();
    /** 满足条件的总记录数 */
    private long total;
    /** 当前页码（从 1 开始） */
    private int pageNo = 1;
    /** 每页条数 */
    private int pageSize = 10;
    /** 总页数 */
    private int totalPages;

    public PageResult() {
    }

    public PageResult(List<T> records, long total, int pageNo, int pageSize) {
        this.records = records == null ? new ArrayList<>() : records;
        this.total = total;
        this.pageNo = Math.max(pageNo, 1);
        this.pageSize = pageSize <= 0 ? 10 : pageSize;
        this.totalPages = (int) ((total + this.pageSize - 1) / this.pageSize);
    }

    /**
     * 构建分页结果。
     *
     * @param records  当前页记录
     * @param total    总记录数
     * @param pageNo   当前页码
     * @param pageSize 每页条数
     * @param <T>      记录类型
     * @return 分页结果
     */
    public static <T> PageResult<T> of(List<T> records, long total, int pageNo, int pageSize) {
        return new PageResult<>(records, total, pageNo, pageSize);
    }

    public boolean isEmpty() {
        return records == null || records.isEmpty();
    }

    public List<T> getRecords() {
        return records;
    }

    public void setRecords(List<T> records) {
        this.records = records;
    }

    public long getTotal() {
        return total;
    }

    public void setTotal(long total) {
        this.total = total;
    }

    public int getPageNo() {
        return pageNo;
    }

    public void setPageNo(int pageNo) {
        this.pageNo = pageNo;
    }

    public int getPageSize() {
        return pageSize;
    }

    public void setPageSize(int pageSize) {
        this.pageSize = pageSize;
    }

    public int getTotalPages() {
        return totalPages;
    }

    public void setTotalPages(int totalPages) {
        this.totalPages = totalPages;
    }

    @Override
    public String toString() {
        return "PageResult{total=" + total + ", pageNo=" + pageNo + ", pageSize=" + pageSize
                + ", totalPages=" + totalPages + ", records=" + (records == null ? 0 : records.size()) + '}';
    }
}
