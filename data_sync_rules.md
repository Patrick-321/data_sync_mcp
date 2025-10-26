# 数据同步 MCP 工作规则

## 在 Cursor Settings > Rules > User Rules 中添加以下规则：

```
# 数据同步工作流程规则

## 用户群数据同步
当处理用户群数据同步任务时，使用以下工具：

1. **数据同步确认**: 在执行任何用户群数据同步操作前，使用 `audience_sync_confirmation` 工具确认：
   - 用户群ID (audience_id)
   - 任务ID (task_id) 
   - 同步详情 (sync_details)
   - 风险等级 (risk_level: low/medium/high)

2. **DMP数据验证**: 在验证DMP返回数据时，使用 `dmp_data_verification` 工具：
   - 用户群ID (audience_id)
   - 任务ID (task_id)
   - 验证类型 (verification_type: status/consistency/completeness)
   - DMP响应数据 (dmp_response)

3. **状态更新确认**: 在更新用户群状态时，使用 `status_update_confirmation` 工具：
   - 用户群ID (audience_id)
   - 任务ID (task_id)
   - 当前状态 (old_status)
   - 目标状态 (new_status)
   - 受影响的MID列表 (affected_mids)

4. **数据一致性检查**: 发现数据不一致时，使用 `data_consistency_check` 工具：
   - 用户群ID (audience_id)
   - 任务ID (task_id)
   - 不一致详情 (inconsistency_details)
   - 严重程度 (severity: low/medium/high/critical)

5. **回滚操作确认**: 需要回滚数据时，使用 `rollback_confirmation` 工具：
   - 用户群ID (audience_id)
   - 任务ID (task_id)
   - 回滚原因 (rollback_reason)
   - 回滚范围 (rollback_scope)

## 工作流程
1. 在执行任何数据同步操作前，先使用相应的确认工具
2. 根据用户反馈调整操作策略
3. 高风险操作需要明确确认
4. 所有操作都要记录日志和上下文
5. 遇到异常时优先使用数据一致性检查工具

## 特殊情况处理
- 当DMP返回0条记录时，使用 `dmp_data_verification` 工具分析原因
- 当状态未变化时，使用 `status_update_confirmation` 工具检查状态计算逻辑
- 当更新失败时，使用 `data_consistency_check` 工具诊断问题
- 当需要回滚时，使用 `rollback_confirmation` 工具确认回滚范围

## 风险控制
- 高风险操作必须使用相应的确认工具
- 所有操作都要考虑对现有数据的影响
- 重要操作前要备份相关数据
- 异常情况要及时记录和报告
```

## 使用示例

### 1. 用户群数据同步
```python
# 在代码中调用
result = audience_sync_confirmation(
    audience_id="60012262",
    task_id="Task67",
    sync_details="从DMP同步用户群数据，包含4条NORMAL记录",
    risk_level="medium"
)
```

### 2. DMP数据验证
```python
# 验证DMP返回数据
result = dmp_data_verification(
    audience_id="60012262", 
    task_id="Task76",
    verification_type="status",
    dmp_response="RawDMP=16, Old=1, New=20"
)
```

### 3. 状态更新确认
```python
# 确认状态更新
result = status_update_confirmation(
    audience_id="60012262",
    task_id="Task76", 
    old_status=1,
    new_status=20,
    affected_mids=["5094814497", "5095532901", "5095533078"]
)
```

### 4. 数据一致性检查
```python
# 检查数据一致性
result = data_consistency_check(
    audience_id="60012262",
    task_id="Task76",
    inconsistency_details="绑定表数据与DMP数据不一致",
    severity="high"
)
```

### 5. 回滚操作确认
```python
# 确认回滚操作
result = rollback_confirmation(
    audience_id="60012262",
    task_id="Task76",
    rollback_reason="DMP数据异常导致状态计算错误",
    rollback_scope="影响的所有MID状态"
)
```

## 配置说明

1. 将 `data_sync_mcp.json` 的内容合并到你的 Cursor MCP 配置中
2. 将上述规则添加到 Cursor Settings > Rules > User Rules 中
3. 重启 Cursor 使配置生效
4. 开始使用数据同步专用的 MCP 工具

## 优势

1. **专业化**: 针对数据同步工作场景优化
2. **风险控制**: 内置风险评估和确认机制
3. **效率提升**: 减少重复的确认步骤
4. **标准化**: 统一的操作流程和确认标准
5. **可追溯**: 完整的操作记录和上下文

