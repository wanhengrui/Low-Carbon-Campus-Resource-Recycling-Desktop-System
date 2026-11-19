package edu.campus.recycle.util;

import java.sql.Connection;

/**
 * 事务回调（模板方法的可变部分）：契约第 8 节模板方法 {@code DbUtil.executeInTransaction} 的入参。
 *
 * <p>实现类只描述"在事务内做什么"，连接的开启、提交、回滚、释放由 {@link DbUtil} 统一完成。</p>
 *
 * @param <T> 返回值类型
 */
@FunctionalInterface
public interface TransactionCallback<T> {

    /**
     * 在给定连接上执行事务体。
     *
     * @param conn 已关闭自动提交的连接（DAO 内部会自动复用该连接）
     * @return 事务结果
     * @throws Exception 任意异常都会触发整体回滚
     */
    T doInTransaction(Connection conn) throws Exception;
}
