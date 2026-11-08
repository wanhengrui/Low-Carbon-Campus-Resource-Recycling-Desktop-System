package edu.campus.recycle.service;

import edu.campus.recycle.entity.OperationLog;
import edu.campus.recycle.exception.DuplicateEntityException;

import java.util.List;

/**
 * 管理服务：两级分类维护与操作日志查询（BR-10 / BR-11）。
 */
public interface AdminService {

    void addCategory(int operatorId, String name, Integer parentId) throws DuplicateEntityException;

    void toggleCategory(int operatorId, int categoryId, boolean enabled);

    List<OperationLog> recentLogs(int limit);
}
