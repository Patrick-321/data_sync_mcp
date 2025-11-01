# 交互式反馈 MCP 使用规则 - 无弹窗版本

## 🎯 核心原则

**重要：当需要使用 `interactive_feedback` 工具时，必须优先使用 `interactive_feedback_no_popup` 工具。**

`interactive_feedback_no_popup` 提供了与 `interactive_feedback` 完全相同的功能，但使用对话+规则文件代替弹窗，用户体验更好，且支持智能记忆。

## 📋 标准工作流程

### 1. 询问用户前的标准流程

**步骤1：调用工具**
- 使用 `interactive_feedback_no_popup` 工具
- **必须提供 `search_keywords` 参数**，用于搜索规则文件中已有的信息
- 可选提供 `predefined_options` 参数，提供预设选项

**步骤2：检查结果**
- 如果工具返回"✅ 在规则文件中找到了相关信息" → **直接使用规则文件中的信息，不再询问用户**
- 如果工具返回"📋 需要在对话中询问用户" → **继续下一步**

### 2. 询问用户（如果未找到信息）

- 在对话中直接询问用户问题
- 如果有预设选项，提供给用户选择
- 等待用户回答

### 3. 保存用户回答（用户回答后）

- **立即调用 `append_rule` 工具**将问题和答案保存到规则文件
- 使用有意义的 `section` 名称，如：
  - "项目配置" - 项目相关的配置信息
  - "工作流程规则" - 工作流程相关的规则
  - "用户偏好" - 用户的偏好设置
  - "数据库配置" - 数据库相关的配置
  - "API配置" - API相关的配置

## 🔄 使用示例

### 示例1：首次询问项目配置

```python
# 1. AI调用工具
result = interactive_feedback_no_popup(
    message="项目使用的技术栈是什么？",
    predefined_options=["Python", "Node.js", "Java", "Go"],
    search_keywords=["技术栈", "技术", "框架", "编程语言"],
    section="项目配置"
)

# 2. 如果返回"需要在对话中询问用户"
# AI在对话中询问：
"请问项目使用的技术栈是什么？
选项：
- Python
- Node.js
- Java
- Go"

# 3. 用户回答："Python + FastAPI + PostgreSQL"

# 4. AI保存回答
append_rule(
    content=f"""
### 项目技术栈配置
**问题：** 项目使用的技术栈是什么？
**用户回答：** Python + FastAPI + PostgreSQL
""",
    section="项目配置"
)
```

### 示例2：后续询问（已保存过）

```python
# 1. AI调用工具
result = interactive_feedback_no_popup(
    message="项目使用的技术栈是什么？",
    search_keywords=["技术栈", "技术", "框架", "编程语言"]
)

# 2. 工具返回"✅ 在规则文件中找到了相关信息"
# AI直接使用规则文件中的信息，不再询问用户
```

## ⚠️ 重要注意事项

1. **必须提供 `search_keywords`**
   - 每次调用 `interactive_feedback_no_popup` 时，必须提供 `search_keywords` 参数
   - 这样才能让工具自动查找规则文件中已有的信息
   - 使用多个相关关键词，提高查找准确性

2. **及时保存用户回答**
   - 用户回答后，**必须立即调用 `append_rule`** 保存
   - 不要忘记保存，确保信息持久化

3. **使用有意义的章节名称**
   - 保存时使用有意义的 `section` 名称
   - 方便后续查找和管理

4. **格式规范**
   - 保存时使用 Markdown 格式
   - 包含问题、用户回答、时间戳等信息

## 🔍 与 `read_rules` 的配合使用

- 需要查看完整规则文件时，使用 `read_rules` 工具
- 可以帮助理解项目的完整上下文
- 可以在询问用户前先查看规则文件

## 🚫 禁止使用

- **禁止直接使用 `interactive_feedback` 工具**
- **必须使用 `interactive_feedback_no_popup` 工具**
- 除非用户明确要求使用弹窗版本

## 💡 最佳实践

1. **智能复用**：每次询问前都要先搜索规则文件，避免重复询问相同问题
2. **及时保存**：用户回答后立即保存，确保信息持久化
3. **使用关键词**：提供相关的 `search_keywords`，提高查找准确性
4. **分类管理**：使用不同的 `section` 名称，便于管理和查找
5. **格式统一**：保存时使用统一的 Markdown 格式

## 🎯 特殊场景处理

### 场景1：需要立即确认的关键操作
- 仍然使用 `interactive_feedback_no_popup`
- 在 `message` 中明确说明这是关键操作
- 即使规则文件中有相关信息，也可以再次确认

### 场景2：批量收集信息
- 使用 `collect_user_info` 工具
- 一次性收集多个问题的答案
- 收集完后统一保存到规则文件

### 场景3：创建新的章节
- 使用 `create_rule_section` 工具
- 为新的主题创建专门的章节

## 📚 工具参考

- `interactive_feedback_no_popup`: 核心工具，替代 `interactive_feedback`
- `append_rule`: 保存用户回答到规则文件
- `read_rules`: 读取完整规则文件
- `collect_user_info`: 批量收集用户信息
- `create_rule_section`: 创建新章节

---

**重要提醒：每次需要使用交互式反馈时，都要使用 `interactive_feedback_no_popup` 而不是 `interactive_feedback`！**

