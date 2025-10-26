# 🎯 数据同步 MCP 工具

专门为**用户肖像和用户群数据同步**工作场景优化的 MCP 工具，基于你的实际工作需求设计。

## 🚀 快速开始

### 1. 一键部署
```bash
chmod +x setup_data_sync_mcp.sh
./setup_data_sync_mcp.sh
```

### 2. 手动部署
```bash
# 安装依赖
uv sync

# 测试服务器
uv run data_sync_mcp.py --help

# 测试 UI
uv run data_sync_ui.py --help
```

## 🛠️ 核心功能

### 1. 用户群数据同步确认
```python
audience_sync_confirmation(
    audience_id="60012262",
    task_id="Task67",
    sync_details="从DMP同步用户群数据，包含4条NORMAL记录",
    risk_level="medium"
)
```

### 2. DMP 数据验证
```python
dmp_data_verification(
    audience_id="60012262",
    task_id="Task76",
    verification_type="status",
    dmp_response="RawDMP=16, Old=1, New=20"
)
```

### 3. 状态更新确认
```python
status_update_confirmation(
    audience_id="60012262",
    task_id="Task76",
    old_status=1,
    new_status=20,
    affected_mids=["5094814497", "5095532901", "5095533078"]
)
```

### 4. 数据一致性检查
```python
data_consistency_check(
    audience_id="60012262",
    task_id="Task76",
    inconsistency_details="绑定表数据与DMP数据不一致",
    severity="high"
)
```

### 5. 回滚操作确认
```python
rollback_confirmation(
    audience_id="60012262",
    task_id="Task76",
    rollback_reason="DMP数据异常导致状态计算错误",
    rollback_scope="影响的所有MID状态"
)
```

## 📋 配置说明

### 1. MCP 配置
将以下内容添加到 Cursor 的 MCP 配置中：

```json
{
  "mcpServers": {
    "data-sync": {
      "command": "uv",
      "args": ["--directory", "/path/to/interactive-feedback-mcp", "run", "data_sync_mcp.py"],
      "timeout": 600,
      "autoApprove": [
        "audience_sync_confirmation",
        "dmp_data_verification", 
        "status_update_confirmation",
        "data_consistency_check",
        "rollback_confirmation"
      ]
    }
  }
}
```

### 2. 用户规则
将 `data_sync_rules.md` 中的规则添加到 Cursor Settings > Rules > User Rules 中。

## 🎯 工作流程

### 典型的数据同步流程：

1. **数据同步确认** → 确认同步操作和风险
2. **DMP 数据验证** → 验证 DMP 返回数据质量
3. **状态更新确认** → 确认状态变更操作
4. **数据一致性检查** → 检查数据完整性
5. **回滚操作确认** → 异常情况下的回滚确认

### 风险控制：

- **低风险**: 数据验证、状态查询
- **中等风险**: 数据同步、状态更新
- **高风险**: 回滚操作、大规模数据变更

## 🎨 界面特性

### 1. 专业化界面
- 深蓝色主题，适合长时间使用
- 标签页设计：基本信息、操作确认、风险评估
- 实时风险等级显示

### 2. 智能预设选项
- 根据操作类型和风险等级自动生成选项
- 快速选择常用操作
- 支持自定义输入

### 3. 风险评估
- 自动评估操作风险等级
- 提供详细的风险说明
- 给出针对性的建议措施

## 📊 使用场景

### 场景1: 用户群数据同步
```
用户: "帮我同步用户群 60012262 的数据"
AI: [调用 audience_sync_confirmation] 显示同步详情和风险
用户: "确认执行同步"
AI: [继续] 执行同步操作
```

### 场景2: DMP 数据验证
```
AI: [调用 dmp_data_verification] "DMP 返回了 4 条记录，请确认数据质量"
用户: "数据验证通过"
AI: [继续] 处理验证通过的数据
```

### 场景3: 状态更新确认
```
AI: [调用 status_update_confirmation] "需要更新 3 个 MID 的状态，请确认"
用户: "确认更新状态"
AI: [继续] 执行状态更新
```

### 场景4: 数据一致性检查
```
AI: [调用 data_consistency_check] "发现数据不一致，严重程度：高"
用户: "修复数据不一致"
AI: [继续] 执行数据修复
```

### 场景5: 回滚操作
```
AI: [调用 rollback_confirmation] "需要回滚操作，请确认回滚范围"
用户: "确认执行回滚"
AI: [继续] 执行回滚操作
```

## 🔧 技术特性

### 1. 异步处理
- 非阻塞的 UI 进程
- 支持超时控制
- 错误恢复机制

### 2. 数据安全
- 临时文件自动清理
- 敏感数据保护
- 操作日志记录

### 3. 扩展性
- 模块化设计
- 易于添加新功能
- 支持自定义模板

## 📈 效率提升

### 传统方式 vs MCP 方式：

**传统方式**:
```
用户: "同步用户群数据"
AI: [生成代码]
用户: "不对，需要先验证 DMP 数据"
AI: [重新生成] ← 消耗第2个请求
用户: "还要检查数据一致性"
AI: [再次生成] ← 消耗第3个请求
```

**MCP 方式**:
```
用户: "同步用户群数据"
AI: [调用 audience_sync_confirmation] "请确认同步操作"
用户: "确认"
AI: [调用 dmp_data_verification] "请验证 DMP 数据"
用户: "验证通过"
AI: [调用 data_consistency_check] "请检查数据一致性"
用户: "检查通过"
AI: [完成同步] ← 只消耗1个请求！
```

**效率提升**: 3个请求 → 1个请求 = **3倍效率提升**

## 🚨 故障排除

### 常见问题：

1. **MCP 服务器启动失败**
   ```bash
   # 检查 Python 版本
   python3 --version
   
   # 检查依赖
   uv sync
   
   # 测试服务器
   uv run data_sync_mcp.py --help
   ```

2. **UI 界面无法显示**
   ```bash
   # 检查 PySide6 安装
   uv run python -c "import PySide6; print('PySide6 OK')"
   
   # 测试 UI
   uv run data_sync_ui.py --help
   ```

3. **配置不生效**
   - 检查 MCP 配置文件路径
   - 重启 Cursor
   - 检查用户规则配置

## 📚 相关文件

- `data_sync_mcp.py`: 主要的 MCP 服务器
- `data_sync_ui.py`: 专用的用户界面
- `data_sync_mcp.json`: MCP 配置文件
- `data_sync_rules.md`: 用户规则配置
- `data_sync_example.py`: 使用示例
- `setup_data_sync_mcp.sh`: 一键部署脚本

## 🤝 贡献

欢迎提交 Issue 和 Pull Request 来改进这个工具！

## 📄 许可证

MIT License

