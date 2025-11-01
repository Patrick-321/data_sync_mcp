# Interactive Feedback MCP
# Developed by Fábio Ferreira (https://x.com/fabiomlferreira)
# Inspired by/related to dotcursorrules.com (https://dotcursorrules.com/)
# Enhanced by Pau Oliva (https://x.com/pof) with ideas from https://github.com/ttommyth/interactive-mcp
import os
import sys
import json
import tempfile
import subprocess
import base64
import re
from datetime import datetime
from typing import Annotated, Dict, Tuple, List, Optional

from fastmcp import FastMCP, Image
from pydantic import Field

# The log_level is necessary for Cline to work: https://github.com/jlowin/fastmcp/issues/81
mcp = FastMCP("Interactive Feedback MCP", log_level="ERROR")

# 默认规则文件路径
DEFAULT_RULES_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "user_rules.md")

def ensure_rules_file(file_path: str = None) -> str:
    """确保规则文件存在，如果不存在则创建"""
    if file_path is None:
        file_path = DEFAULT_RULES_FILE
    
    if not os.path.exists(file_path):
        # 创建新的规则文件，包含基本结构
        initial_content = f"""# 用户规则文件
# 生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## 项目配置

## 工作流程规则

## 确认信息

---
"""
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(initial_content)
    
    return file_path

def read_rules_file(file_path: str = None) -> str:
    """读取规则文件内容"""
    file_path = ensure_rules_file(file_path)
    with open(file_path, 'r', encoding='utf-8') as f:
        return f.read()

def search_in_rules(keywords: List[str], file_path: str = None) -> dict:
    """
    在规则文件中搜索相关信息
    返回包含匹配内容的字典，如果没有找到返回空字典
    """
    try:
        content = read_rules_file(file_path)
        results = {}
        
        for keyword in keywords:
            # 简单的关键词搜索
            pattern = re.compile(keyword, re.IGNORECASE)
            matches = pattern.findall(content)
            if matches:
                # 找到包含该关键词的章节或段落
                lines = content.split('\n')
                context_lines = []
                for i, line in enumerate(lines):
                    if pattern.search(line):
                        # 收集上下文（前后各3行）
                        start = max(0, i - 3)
                        end = min(len(lines), i + 4)
                        context_lines.extend(lines[start:end])
                
                if context_lines:
                    results[keyword] = '\n'.join(context_lines)
        
        return results
    except Exception as e:
        return {"error": str(e)}

def extract_answer_from_rules(search_results: dict) -> Optional[str]:
    """
    从搜索结果中提取用户回答
    尝试从规则文件中找到类似"**用户回答：**"的模式
    """
    for keyword, context in search_results.items():
        # 查找用户回答模式
        answer_pattern = re.compile(r'\*\*用户回答[：:]\*\*\s*(.+)', re.IGNORECASE | re.MULTILINE)
        match = answer_pattern.search(context)
        if match:
            answer = match.group(1).strip()
            if answer:
                return answer
    return None

def append_to_rules_file(content: str, section: str = "确认信息", file_path: str = None) -> str:
    """追加内容到规则文件的指定部分"""
    file_path = ensure_rules_file(file_path)
    
    # 读取现有内容
    current_content = read_rules_file(file_path)
    
    # 生成追加的内容
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    new_content = f"\n### {timestamp}\n{content}\n"
    
    # 如果指定部分不存在，添加它
    if f"## {section}" not in current_content:
        current_content += f"\n## {section}\n"
    
    # 追加到指定部分
    if f"## {section}" in current_content:
        # 在指定部分后面追加
        section_marker = f"## {section}"
        section_index = current_content.rfind(section_marker)
        if section_index != -1:
            # 找到该部分结束的位置（下一个##或文件结尾）
            next_section = current_content.find("\n## ", section_index + len(section_marker))
            if next_section == -1:
                # 没有下一个部分，追加到文件末尾
                current_content += new_content
            else:
                # 插入到下一个部分之前
                current_content = current_content[:next_section] + new_content + current_content[next_section:]
        else:
            current_content += f"\n## {section}{new_content}"
    else:
        current_content += f"\n## {section}{new_content}"
    
    # 写回文件
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(current_content)
    
    return file_path

def launch_feedback_ui(summary: str, predefinedOptions: list[str] | None = None) -> dict[str, str]:
    # Create a temporary file for the feedback result
    with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as tmp:
        output_file = tmp.name

    try:
        # Get the path to feedback_ui.py relative to this script
        script_dir = os.path.dirname(os.path.abspath(__file__))
        feedback_ui_path = os.path.join(script_dir, "feedback_ui.py")

        # Run feedback_ui.py as a separate process
        # NOTE: There appears to be a bug in uv, so we need
        # to pass a bunch of special flags to make this work
        args = [
            sys.executable,
            "-u",
            feedback_ui_path,
            "--prompt", summary,
            "--output-file", output_file,
            "--predefined-options", "|||".join(predefinedOptions) if predefinedOptions else ""
        ]
        result = subprocess.run(
            args,
            check=False,
            shell=False,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            stdin=subprocess.DEVNULL,
            close_fds=True
        )
        if result.returncode != 0:
            raise Exception(f"Failed to launch feedback UI: {result.returncode}")

        # Read the result from the temporary file
        with open(output_file, 'r') as f:
            result = json.load(f)
        os.unlink(output_file)
        return result
    except Exception as e:
        if os.path.exists(output_file):
            os.unlink(output_file)
        raise e

@mcp.tool()
def interactive_feedback(
    message: str = Field(description="The specific question for the user"),
    predefined_options: list = Field(default=None, description="Predefined options for the user to choose from (optional)"),
    search_keywords: Optional[List[str]] = Field(default=None, description="Optional keywords to search in rules file. If found, skip popup and return directly."),
    section: str = Field(default="确认信息", description="Section name in rules file to save the feedback (default: 确认信息)"),
) -> Tuple[str | Image, ...]:
    """
    Request interactive feedback from the user.
    
    Enhanced version with smart rules file lookup:
    1. If search_keywords provided, first search in rules file
    2. If found, return directly without popup
    3. If not found or no search_keywords, show popup UI
    4. After popup, automatically save to rules file
    """
    # 如果提供了搜索关键词，先搜索规则文件
    if search_keywords and len(search_keywords) > 0:
        search_results = search_in_rules(search_keywords)
        if search_results and "error" not in search_results:
            # 找到了相关信息，尝试提取用户回答
            answer = extract_answer_from_rules(search_results)
            if answer:
                # 直接返回，跳过弹窗
                return answer
    
    # 没找到或没提供搜索关键词，使用弹窗收集信息
    predefined_options_list = predefined_options if isinstance(predefined_options, list) else None
    result_dict = launch_feedback_ui(message, predefined_options_list)

    txt: str = result_dict.get("interactive_feedback", "").strip()
    img_b64_list: List[str] = result_dict.get("images", [])

    # 如果收集到了文本反馈，自动保存到规则文件
    if txt and search_keywords:
        try:
            # 保存到规则文件
            save_content = f"""**问题：** {message}
**用户回答：** {txt}"""
            append_to_rules_file(save_content, section)
        except Exception as e:
            # 保存失败不影响返回结果，只在日志中记录
            pass

    # 把 base64 变成 Image 对象
    images: List[Image] = []
    for b64 in img_b64_list:
        try:
            img_bytes = base64.b64decode(b64)
            images.append(Image(data=img_bytes, format="png"))
        except Exception:
            # 若解码失败，忽略该图片并在文字中提示
            txt += f"\n\n[warning] 有一张图片解码失败。"

    # 根据返回的实际内容组装 tuple
    if txt and images:
        return (txt, *images)
    elif txt:
        return txt
    elif images:
        return (images[0],) if len(images) == 1 else tuple(images)
    else:
        return ("",)

if __name__ == "__main__":
    mcp.run(transport="stdio")
