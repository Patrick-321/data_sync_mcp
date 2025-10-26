# Data Sync MCP - 专门为数据同步工作优化的 MCP 工具
# 针对用户肖像、用户群数据同步场景
import os
import sys
import json
import tempfile
import subprocess
import base64
import logging
from typing import Annotated, Dict, Tuple, List, Optional
from datetime import datetime
from dataclasses import dataclass

from fastmcp import FastMCP
from fastmcp.utilities.types import Image
from pydantic import Field

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# 创建 MCP 服务器
mcp = FastMCP("Data Sync MCP", log_level="INFO")

@dataclass
class DataSyncContext:
    """数据同步上下文"""
    audience_id: str
    task_id: str
    operation_type: str  # "sync", "verify", "update", "rollback"
    timestamp: str
    user_id: Optional[str] = None

class DataSyncFeedbackUI:
    """专门为数据同步设计的反馈界面"""
    
    def __init__(self, context: DataSyncContext):
        self.context = context
        self.templates = {
            "audience_sync": self._get_audience_sync_template(),
            "dmp_verify": self._get_dmp_verify_template(),
            "status_update": self._get_status_update_template(),
            "data_consistency": self._get_data_consistency_template(),
            "rollback_confirm": self._get_rollback_confirm_template()
        }
    
    def _get_audience_sync_template(self) -> str:
        return f"""
# 🎯 用户群数据同步确认

**任务ID**: {self.context.task_id}
**用户群ID**: {self.context.audience_id}
**操作类型**: 数据同步
**时间**: {self.context.timestamp}

## 📊 同步详情
- 源系统: DMP
- 目标系统: 本地数据库
- 数据量: 待确认

## ⚠️ 风险提示
- 数据同步可能影响现有用户群状态
- 建议在低峰期执行
- 同步后需要验证数据一致性

请确认是否继续执行同步操作？
"""
    
    def _get_dmp_verify_template(self) -> str:
        return f"""
# 🔍 DMP 数据验证

**任务ID**: {self.context.task_id}
**用户群ID**: {self.context.audience_id}
**验证类型**: DMP 状态验证

## 📋 验证项目
- [ ] DMP 返回状态检查
- [ ] 绑定表数据完整性
- [ ] 用户群状态一致性
- [ ] 历史数据对比

## 🎛️ 验证选项
请选择验证范围：
"""
    
    def _get_status_update_template(self) -> str:
        return f"""
# 🔄 状态更新确认

**任务ID**: {self.context.task_id}
**用户群ID**: {self.context.audience_id}
**更新类型**: 状态计算与更新

## 📈 状态变更
- 当前状态: 待计算
- 目标状态: 待确认
- 影响范围: 相关用户群

## ⚡ 更新策略
请选择更新策略：
"""
    
    def _get_data_consistency_template(self) -> str:
        return f"""
# ⚖️ 数据一致性检查

**任务ID**: {self.context.task_id}
**用户群ID**: {self.context.audience_id}
**检查类型**: 数据一致性验证

## 🔍 检查项目
- [ ] 绑定表数据完整性
- [ ] DMP 与本地数据对比
- [ ] 用户群状态一致性
- [ ] 事务完整性检查

## 🚨 异常处理
如发现数据不一致，请选择处理方式：
"""
    
    def _get_rollback_confirm_template(self) -> str:
        return f"""
# ⏪ 回滚操作确认

**任务ID**: {self.context.task_id}
**用户群ID**: {self.context.audience_id}
**回滚类型**: 数据回滚

## ⚠️ 回滚警告
- 此操作将撤销最近的更改
- 可能影响相关用户群状态
- 回滚后需要重新验证数据

## 🔒 安全确认
请确认您有权限执行此操作：
"""

def launch_data_sync_ui(context: DataSyncContext, predefined_options: List[str] = None) -> Dict[str, str]:
    """启动数据同步专用的反馈界面"""
    
    # 创建临时文件
    with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as tmp:
        output_file = tmp.name
    
    try:
        # 获取脚本目录
        script_dir = os.path.dirname(os.path.abspath(__file__))
        feedback_ui_path = os.path.join(script_dir, "data_sync_ui.py")
        
        # 创建数据同步上下文
        context_data = {
            "audience_id": context.audience_id,
            "task_id": context.task_id,
            "operation_type": context.operation_type,
            "timestamp": context.timestamp,
            "user_id": context.user_id
        }
        
        # 启动专用 UI
        args = [
            sys.executable,
            "-u",
            feedback_ui_path,
            "--context", json.dumps(context_data),
            "--output-file", output_file,
            "--predefined-options", "|||".join(predefined_options) if predefined_options else ""
        ]
        
        result = subprocess.run(
            args,
            check=False,
            shell=False,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            stdin=subprocess.DEVNULL,
            close_fds=True,
            timeout=300  # 5分钟超时
        )
        
        if result.returncode != 0:
            logger.error(f"Data sync UI failed with return code: {result.returncode}")
            raise Exception(f"Failed to launch data sync UI: {result.returncode}")
        
        # 读取结果
        with open(output_file, 'r', encoding='utf-8') as f:
            result_data = json.load(f)
        
        os.unlink(output_file)
        return result_data
        
    except subprocess.TimeoutExpired:
        logger.error("Data sync UI timeout")
        return {"interactive_feedback": "操作超时，请重试", "images": []}
    except Exception as e:
        logger.error(f"Error in data sync UI: {e}")
        if os.path.exists(output_file):
            os.unlink(output_file)
        raise e

@mcp.tool()
def audience_sync_confirmation(
    audience_id: str = Field(description="用户群ID"),
    task_id: str = Field(description="任务ID"),
    sync_details: str = Field(description="同步详情描述"),
    risk_level: str = Field(default="medium", description="风险等级: low/medium/high")
) -> Tuple[str, ...]:
    """
    用户群数据同步确认工具
    用于确认用户群数据同步操作，包含风险评估和详细确认
    """
    logger.info(f"Audience sync confirmation requested: {audience_id}, task: {task_id}")
    
    context = DataSyncContext(
        audience_id=audience_id,
        task_id=task_id,
        operation_type="sync",
        timestamp=datetime.now().isoformat()
    )
    
    # 根据风险等级设置预设选项
    if risk_level == "high":
        predefined_options = [
            "✅ 确认执行同步（高风险）",
            "⚠️ 先执行预检查",
            "❌ 取消操作",
            "📋 查看详细风险评估"
        ]
    elif risk_level == "low":
        predefined_options = [
            "✅ 确认执行同步",
            "📊 查看同步预览",
            "⏰ 定时执行",
            "❌ 取消操作"
        ]
    else:  # medium
        predefined_options = [
            "✅ 确认执行同步",
            "🔍 先验证数据完整性",
            "📋 查看同步计划",
            "❌ 取消操作"
        ]
    
    result_dict = launch_data_sync_ui(context, predefined_options)
    
    txt = result_dict.get("interactive_feedback", "").strip()
    img_b64_list = result_dict.get("images", [])
    
    # 处理图片
    images = []
    for b64 in img_b64_list:
        try:
            img_bytes = base64.b64decode(b64)
            images.append(Image(data=img_bytes, format="png"))
        except Exception as e:
            logger.warning(f"Failed to decode image: {e}")
            txt += f"\n\n[warning] 图片解码失败: {str(e)}"
    
    # 返回结果
    if txt and images:
        return (txt, *images)
    elif txt:
        return txt
    elif images:
        return (images[0],) if len(images) == 1 else tuple(images)
    else:
        return ("",)

@mcp.tool()
def dmp_data_verification(
    audience_id: str = Field(description="用户群ID"),
    task_id: str = Field(description="任务ID"),
    verification_type: str = Field(description="验证类型: status/consistency/completeness"),
    dmp_response: str = Field(description="DMP 响应数据")
) -> Tuple[str, ...]:
    """
    DMP 数据验证工具
    用于验证 DMP 返回的数据质量和一致性
    """
    logger.info(f"DMP verification requested: {audience_id}, type: {verification_type}")
    
    context = DataSyncContext(
        audience_id=audience_id,
        task_id=task_id,
        operation_type="verify",
        timestamp=datetime.now().isoformat()
    )
    
    predefined_options = [
        "✅ 数据验证通过",
        "⚠️ 发现异常，需要处理",
        "🔄 重新请求 DMP 数据",
        "📊 查看详细验证报告",
        "❌ 跳过验证"
    ]
    
    result_dict = launch_data_sync_ui(context, predefined_options)
    
    txt = result_dict.get("interactive_feedback", "").strip()
    img_b64_list = result_dict.get("images", [])
    
    # 处理图片
    images = []
    for b64 in img_b64_list:
        try:
            img_bytes = base64.b64decode(b64)
            images.append(Image(data=img_bytes, format="png"))
        except Exception as e:
            logger.warning(f"Failed to decode image: {e}")
            txt += f"\n\n[warning] 图片解码失败: {str(e)}"
    
    return (txt, *images) if txt and images else (txt,) if txt else ("",)

@mcp.tool()
def status_update_confirmation(
    audience_id: str = Field(description="用户群ID"),
    task_id: str = Field(description="任务ID"),
    old_status: int = Field(description="当前状态"),
    new_status: int = Field(description="目标状态"),
    affected_mids: List[str] = Field(description="受影响的 MID 列表")
) -> Tuple[str, ...]:
    """
    状态更新确认工具
    用于确认用户群状态更新操作
    """
    logger.info(f"Status update confirmation: {audience_id}, {old_status} -> {new_status}")
    
    context = DataSyncContext(
        audience_id=audience_id,
        task_id=task_id,
        operation_type="update",
        timestamp=datetime.now().isoformat()
    )
    
    predefined_options = [
        "✅ 确认更新状态",
        "📊 查看影响范围分析",
        "⏰ 分批更新",
        "🔍 先验证状态变更",
        "❌ 取消更新"
    ]
    
    result_dict = launch_data_sync_ui(context, predefined_options)
    
    txt = result_dict.get("interactive_feedback", "").strip()
    img_b64_list = result_dict.get("images", [])
    
    # 处理图片
    images = []
    for b64 in img_b64_list:
        try:
            img_bytes = base64.b64decode(b64)
            images.append(Image(data=img_bytes, format="png"))
        except Exception as e:
            logger.warning(f"Failed to decode image: {e}")
            txt += f"\n\n[warning] 图片解码失败: {str(e)}"
    
    return (txt, *images) if txt and images else (txt,) if txt else ("",)

@mcp.tool()
def data_consistency_check(
    audience_id: str = Field(description="用户群ID"),
    task_id: str = Field(description="任务ID"),
    inconsistency_details: str = Field(description="数据不一致详情"),
    severity: str = Field(description="严重程度: low/medium/high/critical")
) -> Tuple[str, ...]:
    """
    数据一致性检查工具
    用于处理数据不一致问题
    """
    logger.info(f"Data consistency check: {audience_id}, severity: {severity}")
    
    context = DataSyncContext(
        audience_id=audience_id,
        task_id=task_id,
        operation_type="consistency",
        timestamp=datetime.now().isoformat()
    )
    
    if severity == "critical":
        predefined_options = [
            "🚨 立即修复数据不一致",
            "⏸️ 暂停相关操作",
            "📞 联系数据团队",
            "📋 生成详细报告"
        ]
    elif severity == "high":
        predefined_options = [
            "🔧 修复数据不一致",
            "📊 分析影响范围",
            "⏰ 计划修复时间",
            "📋 记录问题"
        ]
    else:
        predefined_options = [
            "🔧 修复数据不一致",
            "📊 查看详细分析",
            "⏰ 稍后处理",
            "✅ 忽略此问题"
        ]
    
    result_dict = launch_data_sync_ui(context, predefined_options)
    
    txt = result_dict.get("interactive_feedback", "").strip()
    img_b64_list = result_dict.get("images", [])
    
    # 处理图片
    images = []
    for b64 in img_b64_list:
        try:
            img_bytes = base64.b64decode(b64)
            images.append(Image(data=img_bytes, format="png"))
        except Exception as e:
            logger.warning(f"Failed to decode image: {e}")
            txt += f"\n\n[warning] 图片解码失败: {str(e)}"
    
    return (txt, *images) if txt and images else (txt,) if txt else ("",)

@mcp.tool()
def rollback_confirmation(
    audience_id: str = Field(description="用户群ID"),
    task_id: str = Field(description="任务ID"),
    rollback_reason: str = Field(description="回滚原因"),
    rollback_scope: str = Field(description="回滚范围")
) -> Tuple[str, ...]:
    """
    回滚操作确认工具
    用于确认数据回滚操作
    """
    logger.info(f"Rollback confirmation: {audience_id}, reason: {rollback_reason}")
    
    context = DataSyncContext(
        audience_id=audience_id,
        task_id=task_id,
        operation_type="rollback",
        timestamp=datetime.now().isoformat()
    )
    
    predefined_options = [
        "⏪ 确认执行回滚",
        "📊 查看回滚影响分析",
        "💾 先备份当前数据",
        "🔍 分析回滚原因",
        "❌ 取消回滚"
    ]
    
    result_dict = launch_data_sync_ui(context, predefined_options)
    
    txt = result_dict.get("interactive_feedback", "").strip()
    img_b64_list = result_dict.get("images", [])
    
    # 处理图片
    images = []
    for b64 in img_b64_list:
        try:
            img_bytes = base64.b64decode(b64)
            images.append(Image(data=img_bytes, format="png"))
        except Exception as e:
            logger.warning(f"Failed to decode image: {e}")
            txt += f"\n\n[warning] 图片解码失败: {str(e)}"
    
    return (txt, *images) if txt and images else (txt,) if txt else ("",)

if __name__ == "__main__":
    mcp.run(transport="stdio")

