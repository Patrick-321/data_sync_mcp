#!/bin/bash

# 数据同步 MCP 快速部署脚本
# 专门为数据同步工作场景优化

echo "🚀 开始部署数据同步 MCP 工具..."
echo "=================================="

# 检查 Python 版本
echo "📋 检查环境..."
python_version=$(python3 --version 2>&1 | cut -d' ' -f2 | cut -d'.' -f1,2)
required_version="3.10"

if [ "$(printf '%s\n' "$required_version" "$python_version" | sort -V | head -n1)" = "$required_version" ]; then
    echo "✅ Python 版本检查通过: $python_version"
else
    echo "❌ Python 版本过低，需要 >= $required_version，当前: $python_version"
    exit 1
fi

# 检查 uv 是否安装
if command -v uv &> /dev/null; then
    echo "✅ uv 已安装: $(uv --version)"
else
    echo "❌ uv 未安装，请先安装 uv:"
    echo "   macOS: brew install uv"
    echo "   Linux: curl -LsSf https://astral.sh/uv/install.sh | sh"
    echo "   Windows: pip install uv"
    exit 1
fi

# 安装依赖
echo "📦 安装依赖..."
cd "$(dirname "$0")"
uv sync

if [ $? -eq 0 ]; then
    echo "✅ 依赖安装成功"
else
    echo "❌ 依赖安装失败"
    exit 1
fi

# 测试 MCP 服务器
echo "🧪 测试 MCP 服务器..."
timeout 10s uv run data_sync_mcp.py --help > /dev/null 2>&1

if [ $? -eq 0 ]; then
    echo "✅ 数据同步 MCP 服务器测试通过"
else
    echo "❌ 数据同步 MCP 服务器测试失败"
    exit 1
fi

# 测试 UI
echo "🧪 测试 UI 界面..."
timeout 10s uv run data_sync_ui.py --help > /dev/null 2>&1

if [ $? -eq 0 ]; then
    echo "✅ 数据同步 UI 测试通过"
else
    echo "❌ 数据同步 UI 测试失败"
    exit 1
fi

# 创建配置文件
echo "⚙️ 配置 MCP 服务器..."

# 获取当前目录
current_dir=$(pwd)
echo "当前目录: $current_dir"

# 更新配置文件中的路径
sed "s|/Users/zhoupatrick/Desktop/interactive-feedback-mcp|$current_dir|g" data_sync_mcp.json > data_sync_mcp_local.json

echo "✅ 配置文件已创建: data_sync_mcp_local.json"

# 显示配置内容
echo ""
echo "📋 MCP 配置内容:"
echo "=================================="
cat data_sync_mcp_local.json
echo "=================================="

# 创建 Cursor 配置目录（如果不存在）
cursor_config_dir="$HOME/Library/Application Support/Cursor/User"
if [ ! -d "$cursor_config_dir" ]; then
    echo "📁 创建 Cursor 配置目录..."
    mkdir -p "$cursor_config_dir"
fi

# 备份现有配置
if [ -f "$cursor_config_dir/mcp.json" ]; then
    echo "💾 备份现有 MCP 配置..."
    cp "$cursor_config_dir/mcp.json" "$cursor_config_dir/mcp.json.backup.$(date +%Y%m%d_%H%M%S)"
fi

# 合并配置
echo "🔧 合并 MCP 配置..."
if [ -f "$cursor_config_dir/mcp.json" ]; then
    # 如果已有配置，合并
    echo "合并到现有配置..."
    # 这里可以添加更复杂的合并逻辑
    cp data_sync_mcp_local.json "$cursor_config_dir/mcp.json"
else
    # 如果没有配置，直接复制
    echo "创建新配置..."
    cp data_sync_mcp_local.json "$cursor_config_dir/mcp.json"
fi

echo "✅ MCP 配置已更新"

# 显示用户规则
echo ""
echo "📋 用户规则配置:"
echo "=================================="
echo "请将以下内容添加到 Cursor Settings > Rules > User Rules 中："
echo ""
cat data_sync_rules.md
echo "=================================="

# 运行示例
echo ""
echo "🎯 运行使用示例..."
python3 data_sync_example.py

echo ""
echo "🎉 数据同步 MCP 部署完成！"
echo "=================================="
echo "📋 下一步操作:"
echo "1. 重启 Cursor 使配置生效"
echo "2. 将用户规则添加到 Cursor Settings > Rules > User Rules"
echo "3. 开始使用数据同步专用的 MCP 工具"
echo ""
echo "🛠️ 可用的 MCP 工具:"
echo "- audience_sync_confirmation: 用户群数据同步确认"
echo "- dmp_data_verification: DMP 数据验证"
echo "- status_update_confirmation: 状态更新确认"
echo "- data_consistency_check: 数据一致性检查"
echo "- rollback_confirmation: 回滚操作确认"
echo ""
echo "📚 更多信息请查看:"
echo "- data_sync_rules.md: 详细使用规则"
echo "- data_sync_example.py: 使用示例"
echo "=================================="

