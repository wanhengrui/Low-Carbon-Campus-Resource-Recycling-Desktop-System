package edu.campus.recycle.dao;

import edu.campus.recycle.entity.OperationLog;

import java.util.List;

/**
 * 操作日志 DAO（契约第 5 节）。日志仅追加，不提供修改与删除（BR-11）。
 */
public interface OperationLogDao extends BaseDao<OperationLog, Integer> {

    /**
     * 追加一条操作日志。
     *
     * @param log 日志
     * @return 受影响行数
     */
    @Override
    int insert(OperationLog log);

    /**
     * 查询最近若干条操作日志（按时间倒序）。
     *
     * @param limit 条数上限
     * @return 日志列表
     */
    List<OperationLog> findRecent(int limit);
}
