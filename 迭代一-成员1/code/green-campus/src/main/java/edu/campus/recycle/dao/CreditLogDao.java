package edu.campus.recycle.dao;

import edu.campus.recycle.entity.CreditLog;

import java.util.List;

/**
 * 信用分流水 DAO（契约第 5 节）。流水只追加，作为信用分变更的审计快照（BR-04）。
 */
public interface CreditLogDao extends BaseDao<CreditLog, Integer> {

    /**
     * 新增流水。
     *
     * @param log 流水
     * @return 受影响行数
     */
    @Override
    int insert(CreditLog log);

    /**
     * 查询某用户最近若干条信用分流水（按时间倒序）。
     *
     * @param userId 用户ID
     * @param limit  条数上限
     * @return 流水列表
     */
    List<CreditLog> findByUserId(int userId, int limit);
}
