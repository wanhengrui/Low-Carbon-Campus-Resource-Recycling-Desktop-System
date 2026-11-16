# 迭代一 · UI 事件流与 SwingWorker 规则

## 1. 标准事件模板

所有业务按钮统一按下面模板实现，禁止在 EDT 中直接访问数据库/Service：

```java
button.setEnabled(false);
new SwingWorker<PageResult<Item>, Void>() {
    @Override
    protected PageResult<Item> doInBackground() {
        return itemController.search(query);   // 只做后台调用
    }

    @Override
    protected void done() {
        try {
            PageResult<Item> page = get();
            tableModel.setRows(page.getRecords());  // 只在 EDT 更新控件
            pageLabel.setText("第 " + page.getPageNo() + " 页 / 共 " + page.getTotalPages() + " 页");
        } catch (ExecutionException ex) {
            Throwable cause = ex.getCause();
            if (cause instanceof AppException) {
                UiMessages.error(ItemSearchPanel.this, (AppException) cause);
            } else {
                UiMessages.error(ItemSearchPanel.this, "系统异常：" + cause.getMessage());
            }
        } catch (InterruptedException ex) {
            Thread.currentThread().interrupt();
        } finally {
            button.setEnabled(true);
        }
    }
}.execute();
```

## 2. 线程规则

| 规则 | 要求 |
|---|---|
| EDT 只做 UI | `doInBackground()` 中禁止操作 Swing 组件 |
| 耗时操作 | 登录、检索、发布、成交、评价、导出、管理员操作全部放 `SwingWorker` |
| 更新控件 | 只在 `done()` 中更新表格、按钮、标签、对话框 |
| 防重复提交 | 提交前 `setEnabled(false)`，`finally` 恢复 |
| 取消/关闭 | 窗口关闭时取消未完成 Worker，避免回调操作已 dispose 的组件 |
| 异常 | 只捕获 `AppException`；未知异常统一提示“系统异常”，并写日志 |

## 3. 关键事件流

### 3.1 登录

```text
LoginFrame 登录按钮
→ 校验非空
→ SwingWorker: AppController.login(username, password)
→ 成功: new MainFrame(app, result).setVisible(true); LoginFrame.dispose()
→ 失败: AppException.getUserMessage() 显示在状态栏，密码框全选
```

### 3.2 注册

```text
LoginFrame 注册按钮
→ RegisterDialog（模态）
→ 校验必填 + 两次密码一致
→ SwingWorker: UserController.register(... role=STUDENT ...)
→ 成功: 提示并关闭；失败: 状态栏显示返回文案
```

### 3.3 检索

```text
检索按钮
→ 组装 ItemQuery（关键词/分类/价格/交易方式/排序/分页）
→ SwingWorker: ItemController.search(query)
→ done(): ItemTableModel.setRows(...)
→ 双击行: ItemController.detail(itemId) → ItemDetailDialog
```

### 3.4 发布

```text
发布按钮
→ PublishItemDialog 校验字段
→ SwingWorker: ItemController.publish(item, imagePaths)
→ done(): 刷新“我的物品”/检索列表；提示“待审核”
```

### 3.5 流转

```text
申请: TradeController.apply(itemId, buyerId, remark)
同意: TradeController.agree(flowId, sellerId)
成交: TradeController.confirm(flowId, sellerId)  // 二次确认
取消: TradeController.cancel(flowId, operatorId, reason) // 原因必填
→ 完成后刷新流转表 + 物品状态 + 未读数
```

### 3.6 管理后台

```text
审核: ItemController.audit(operatorId, itemId, pass, remark)
下架: ItemController.offShelf(itemId, operatorId)
冻结: UserController.freezeUser(operatorId, userId)
分类: AdminController.addCategory/toggleCategory
日志: AdminController.recentLogs
→ 每个危险操作二次确认；完成后刷新列表
```

## 4. UI 文案与状态

- 角色：学生 / 教师 / 管理员。
- 物品状态：`DRAFT/PENDING/ON_SALE/LOCKED/SOLD/OFF_SHELF/REJECTED` 需要中文映射。
- 流转状态：`APPLYING/AGREED/DONE/CANCELLED` 需要中文映射。
- 错误提示统一从 `AppException.getUserMessage()` 取，不在 UI 重新拼业务文案。
- 空列表：显示“暂无数据”，不要显示空白表格。
- 加载中：按钮文字改为“查询中…/提交中…”，必要时显示 `JProgressBar`。

## 5. 迭代一已落地的部分

- 登录、注册已使用 `SwingWorker`；
- 主界面导航与占位卡已落地；
- 业务页的 `SwingWorker` 模板已在本文件冻结，迭代二直接复制使用。
