# 🚀 增强版 interactive_feedback - 智能规则文件集成

## 🎯 新功能说明

`interactive_feedback` 工具现在已增强，支持**智能规则文件查找**功能！

### ✨ 主要特性

1. **智能查找**：如果提供了 `search_keywords`，会先在规则文件中搜索相关信息
2. **跳过弹窗**：如果找到相关信息，直接返回，**不再弹窗**
3. **自动保存**：如果通过弹窗收集了信息，**自动保存到规则文件**
4. **向后兼容**：不提供 `search_keywords` 时，行为与原来完全一致

## 🔄 工作流程

### 场景1：规则文件中有信息（跳过弹窗）

```
AI 调用 interactive_feedback(
    message="项目使用的数据库类型是什么？",
    search_keywords=["数据库", "数据库类型"]
)
    ↓
搜索规则文件 user_rules.md
    ↓
找到相关信息 ✅
    ↓
直接返回用户回答，**不弹窗**！
```

### 场景2：规则文件中没有信息（正常弹窗）

```
AI 调用 interactive_feedback(
    message="项目使用的数据库类型是什么？",
    search_keywords=["数据库", "数据库类型"]
)
    ↓
搜索规则文件 user_rules.md
    ↓
未找到相关信息 ❌
    ↓
显示弹窗 UI，收集用户输入
    ↓
用户回答后，**自动保存到规则文件**
```

### 场景3：没有提供 search_keywords（原始行为）

```
AI 调用 interactive_feedback(
    message="项目使用的数据库类型是什么？"
)
    ↓
直接显示弹窗 UI（与原来完全一致）
```

## 📋 新增参数

### `search_keywords` (可选)

**类型**：`List[str]`  
**说明**：用于在规则文件中搜索相关信息的关键词列表  
**示例**：`["数据库", "数据库类型", "DB"]`

### `section` (可选)

**类型**：`str`  
**默认值**：`"确认信息"`  
**说明**：保存用户回答时使用的章节名称  
**示例**：`"项目配置"`, `"数据库配置"`, `"API配置"`

## 💡 使用示例

### 示例1：智能查找（跳过弹窗）

```python
# 第一次使用 - 弹窗收集
result = interactive_feedback(
    message="项目使用的数据库类型是什么？",
    predefined_options=["MySQL", "PostgreSQL", "MongoDB"],
    search_keywords=["数据库", "数据库类型"]
)
# 显示弹窗，用户选择：PostgreSQL
# 自动保存到规则文件

# 第二次使用 - 直接返回，不弹窗！
result = interactive_feedback(
    message="项目使用的数据库类型是什么？",
    search_keywords=["数据库", "数据库类型"]
)
# 从规则文件中找到：PostgreSQL
# 直接返回，不弹窗！
```

### 示例2：自定义章节名称

```python
result = interactive_feedback(
    message="项目使用的技术栈是什么？",
    search_keywords=["技术栈", "技术", "框架"],
    section="项目配置"  # 保存到"项目配置"章节
)
```

### 示例3：向后兼容（不提供 search_keywords）

```python
result = interactive_feedback(
    message="你觉得这个设计怎么样？",
    predefined_options=["很好", "一般", "需要改进"]
)
# 行为与原来完全一致，直接显示弹窗
```

## 📊 优势对比

| 特性 | 原版 interactive_feedback | 增强版 interactive_feedback |
|------|---------------------------|------------------------------|
| 弹窗收集 | ✅ 总是弹窗 | ✅ 智能判断 |
| 规则文件查找 | ❌ 不支持 | ✅ 支持 |
| 自动保存 | ❌ 不支持 | ✅ 支持 |
| 跳过弹窗 | ❌ 不支持 | ✅ 如果找到信息则跳过 |
| 向后兼容 | ✅ | ✅ 完全兼容 |

## 🔍 规则文件格式

工具会自动识别以下格式的规则文件内容：

```markdown
### 2025-11-02 01:53:51

### 数据库配置
**问题：** 项目使用的数据库类型是什么？
**用户回答：** PostgreSQL
```

工具会搜索包含关键词的内容，并提取 `**用户回答：**` 后面的答案。

## ⚙️ 配置说明

### 规则文件路径

默认路径：`user_rules.md`（与 `server.py` 同目录）

如果规则文件不存在，工具会自动创建。

## 🎯 最佳实践

1. **提供搜索关键词**：使用 `search_keywords` 参数，让工具能够查找已有信息
2. **使用有意义的章节名称**：使用 `section` 参数组织不同类型的信息
3. **重复使用相同关键词**：确保相同问题使用相同的 `search_keywords`

## 📚 相关文档

- [无弹窗版本规则](./cursor_user_rules_no_popup.md)
- [规则管理 MCP](./RULES_MCP_README.md)
- [主 README](./README.md)

## 🔄 迁移指南

### 从原版迁移

**不需要任何改动！** 增强版完全向后兼容。

如果你想使用新功能，只需添加 `search_keywords` 参数：

```python
# 原版（仍然有效）
interactive_feedback(message="问题")

# 增强版（添加 search_keywords）
interactive_feedback(
    message="问题",
    search_keywords=["关键词1", "关键词2"]
)
```

### 从 interactive_feedback_no_popup 迁移

如果你之前使用 `interactive_feedback_no_popup`，现在可以直接使用增强版的 `interactive_feedback`：

```python
# 之前
interactive_feedback_no_popup(
    message="问题",
    search_keywords=["关键词"]
)

# 现在
interactive_feedback(
    message="问题",
    search_keywords=["关键词"]
)
# 行为完全一致，但还保留了弹窗功能！
```

## 🎉 总结

现在 `interactive_feedback` 工具兼具：
- ✅ **弹窗功能**（如果规则文件中没有信息）
- ✅ **智能查找**（如果规则文件中有信息，跳过弹窗）
- ✅ **自动保存**（收集的信息自动保存到规则文件）
- ✅ **向后兼容**（不提供 `search_keywords` 时行为不变）

**一个工具，两全其美！** 🎯

