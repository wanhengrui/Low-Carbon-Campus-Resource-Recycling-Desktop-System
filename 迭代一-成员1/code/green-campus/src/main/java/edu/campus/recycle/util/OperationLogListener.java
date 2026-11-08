package edu.campus.recycle.util;

import edu.campus.recycle.dao.OperationLogDao;
import edu.campus.recycle.entity.OperationLog;

/**
 * 操作日志监听器：把领域事件落库到 {@code operation_log}（BR-11 仅追加）。
 *
 * <p>与业务操作处于同一事务的连接上，事件发布成功即日志写入成功。</p>
 */
public class OperationLogListener implements ItemEventListener {

    private final OperationLogDao operationLogDao;

    public OperationLogListener(OperationLogDao operationLogDao) {
        this.operationLogDao = operationLogDao;
    }

    @Override
    public void onEvent(ItemEvent event) {
        OperationLog log = new OperationLog();
        log.setOperatorId(event.getOperatorId());
        log.setOperation(event.getType().name());
        if (event.getFlowId() != null) {
            log.setTargetType("FLOW");
            log.setTargetId(event.getFlowId());
        } else {
            log.setTargetType("ITEM");
            log.setTargetId(event.getItemId());
        }
        log.setDetail(event.getDetail());
        log.setIp("localhost");
        log.setCreatedAt(event.getOccurredAt());
        operationLogDao.insert(log);
    }
}
