# 🚀 无弹窗版本快速配置指南

## ✅ 当前状态

你的 MCP 配置已经包含了 `rules-manager`，所有工具已经正确配置！

## 📋 配置步骤

### 1. ✅ MCP 配置已完成

你的 Cursor `mcp.json` 已经包含了 `rules-manager` 配置：
```json
{
  "mcpServers": {
    "rules-manager": {
      "command": "uv",
      "args": ["--directory", "/Users/zhoupatrick/Desktop/interactive-feedback-mcp", "run", "rules_mcp.py"],
      "timeout": 600,
      "autoApprove": [
        "interactive_feedback_no_popup",
        "read_rules",
        "append_rule",
        "collect_user_info",
        "create_rule_section"
      ]
    }
  }
}
```

### 2. 📝 添加用户规则（重要！）

**在 Cursor Settings > Rules > User Rules 中添加以下规则：**

打开 `cursor_user_rules_no_popup.md` 文件，将其内容复制到 Cursor 用户规则中。

或者直接使用以下简化版本：

```markdown
# 交互式反馈 MCP 使用规则 - 无弹窗版本

## 🎯 核心原则

**重要：当需要使用 `interactive_feedback` 工具时，必须优先使用 `interactive_feedback_no_popup` 工具。**

## 📋 标准工作流程

1. **询问用户前**：调用 `interactive_feedback_no_popup`，**必须提供 `search_keywords` 参数**
2. **检查结果**：
   - 如果找到相关信息 → 直接使用规则文件中的信息，不再询问用户
   - 如果未找到 → 在对话中询问用户
3. **用户回答后**：立即调用 `append_rule` 保存到规则文件

## ⚠️ 重要注意事项

1. **必须提供 `search_keywords`**：这样才能让工具自动查找已有信息
2. **及时保存用户回答**：用户回答后必须立即调用 `append_rule` 保存
3. **使用有意义的章节名称**：如"项目配置"、"用户偏好"等

## 🚫 禁止使用

- **禁止直接使用 `interactive_feedback` 工具**
- **必须使用 `interactive_feedback_no_popup` 工具**

## 💡 使用示例

### 首次询问
```python
# 1. 调用工具
result = interactive_feedback_no_popup(
    message="项目使用的技术栈是什么？",
    search_keywords=["技术栈", "技术", "框架"]
)

# 2. 如果返回"需要在对话中询问用户"
# AI在对话中询问用户

# 3. 用户回答后，保存
append_rule(
    content="**问题：** 项目使用的技术栈是什么？\n**用户回答：** Python + FastAPI",
    section="项目配置"
)
```

### 后续询问（已保存过）
```python
# 1. 调用工具（会自动找到已有信息）
result = interactive_feedback_no_popup(
    message="项目使用的技术栈是什么？",
    search_keywords=["技术栈", "技术", "框架"]
)

# 2. 工具返回"找到了相关信息"
# AI直接使用规则文件中的信息，不再询问用户
```

---

**重要提醒：每次需要使用交互式反馈时，都要使用 `interactive_feedback_no_popup` 而不是 `interactive_feedback`！**
```

### 3. 🔄 重启 Cursor

添加用户规则后，**重启 Cursor** 使配置生效。

### 4. ✅ 验证配置

重启后，尝试以下操作验证配置：

1. 在对话中让 AI 询问一个项目配置问题
2. AI 应该会使用 `interactive_feedback_no_popup` 工具
3. 如果是首次询问，AI 会在对话中询问你
4. 你回答后，AI 会保存到 `user_rules.md` 文件
5. 下次相同问题时，AI 会直接从规则文件中读取，不再询问

## 📚 相关文件

- `rules_mcp.py` - MCP 服务器实现
- `cursor_user_rules_no_popup.md` - 完整的用户规则文档
- `rules_mcp_rules.md` - 详细的使用规则
- `user_rules.md` - 存储用户反馈的规则文件（自动生成）

## 🎯 核心优势

✅ **无弹窗**：通过对话+规则文件实现，用户体验更好  
✅ **智能记忆**：第一次询问后保存到规则文件，后续自动使用  
✅ **持久化存储**：所有用户反馈保存在 `user_rules.md` 文件中  
✅ **自动复用**：相同问题不会重复询问

## 💡 工作原理

1. **第一次使用**：AI 调用 `interactive_feedback_no_popup` → 在规则文件中搜索 → 未找到 → AI 在对话中询问 → 用户回答 → AI 保存到规则文件
2. **后续使用**：AI 调用 `interactive_feedback_no_popup` → 在规则文件中搜索 → **找到相关信息** → AI 直接使用，不再询问用户

## 🔍 故障排除

**问题：AI 仍然使用 `interactive_feedback` 而不是 `interactive_feedback_no_popup`**
- 检查用户规则是否正确添加
- 确保已重启 Cursor
- 检查 MCP 配置中的 `rules-manager` 是否启用

**问题：工具找不到已保存的信息**
- 确保在调用 `interactive_feedback_no_popup` 时提供了 `search_keywords`
- 检查 `user_rules.md` 文件中是否包含相关关键词

**问题：规则文件不存在**
- 工具会自动创建 `user_rules.md` 文件，无需手动创建
- 首次使用时会在项目目录下自动创建

---

🎉 **配置完成！现在 AI 会优先使用无弹窗版本的交互式反馈工具！**

