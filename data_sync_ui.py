# Data Sync UI - 专门为数据同步工作设计的用户界面
import os
import sys
import json
import argparse
import base64
import uuid
from datetime import datetime
from typing import Optional, TypedDict, List, Dict

from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QCheckBox, QTextEdit, QTextBrowser, QGroupBox,
    QFrame, QScrollArea, QGridLayout, QProgressBar, QTabWidget
)
from PySide6.QtCore import Qt, Signal, QObject, QTimer, QSettings, QDateTime, QBuffer, QIODevice
from PySide6.QtGui import QTextCursor, QIcon, QKeyEvent, QPalette, QColor, QPixmap, QShortcut, QKeySequence, QFont

class DataSyncResult(TypedDict):
    interactive_feedback: str
    images: List[str]
    operation_type: str
    audience_id: str
    task_id: str

def get_data_sync_palette(app: QApplication):
    """数据同步专用的深色主题"""
    darkPalette = app.palette()
    # 主色调 - 深蓝色系
    darkPalette.setColor(QPalette.Window, QColor(30, 30, 40))
    darkPalette.setColor(QPalette.WindowText, Qt.white)
    darkPalette.setColor(QPalette.Base, QColor(25, 25, 35))
    darkPalette.setColor(QPalette.AlternateBase, QColor(40, 40, 50))
    darkPalette.setColor(QPalette.ToolTipBase, QColor(30, 30, 40))
    darkPalette.setColor(QPalette.ToolTipText, Qt.white)
    darkPalette.setColor(QPalette.Text, Qt.white)
    darkPalette.setColor(QPalette.Button, QColor(45, 45, 55))
    darkPalette.setColor(QPalette.ButtonText, Qt.white)
    darkPalette.setColor(QPalette.Highlight, QColor(0, 120, 215))  # 蓝色高亮
    darkPalette.setColor(QPalette.HighlightedText, Qt.white)
    return darkPalette

class DataSyncTextEdit(QTextEdit):
    """数据同步专用的文本编辑器"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.image_data = []
        
    def keyPressEvent(self, event: QKeyEvent):
        if event.key() == Qt.Key_Return and event.modifiers() == Qt.ControlModifier:
            # Ctrl+Enter 提交
            parent = self.parent()
            while parent and not isinstance(parent, DataSyncUI):
                parent = parent.parent()
            if parent:
                parent._submit_feedback()
        else:
            super().keyPressEvent(event)
    
    def insertFromMimeData(self, source_data):
        """处理粘贴内容，包括图片"""
        try:
            if source_data.hasImage():
                image = source_data.imageData()
                if image:
                    try:
                        # 转换图片为 Base64
                        pixmap = QPixmap.fromImage(image)
                        buffer = QBuffer()
                        buffer.open(QIODevice.WriteOnly)
                        pixmap.save(buffer, "PNG")
                        img_bytes = buffer.data()
                        base64_string = base64.b64encode(img_bytes).decode('utf-8')
                        
                        # 保存图片数据
                        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                        unique_id = str(uuid.uuid4())[:8]
                        filename = f"data_sync_image_{timestamp}_{unique_id}.png"
                        
                        image_info = {
                            'base64': base64_string,
                            'filename': filename
                        }
                        self.image_data.append(image_info)
                        
                        # 插入图片占位符
                        cursor = self.textCursor()
                        cursor.insertText(f"[图片: {filename}]")
                        
                    except Exception as e:
                        print(f"处理图片时出错: {e}")
                        cursor = self.textCursor()
                        cursor.insertText(f"[图片处理失败: {str(e)}]")
            else:
                super().insertFromMimeData(source_data)
        except Exception as e:
            print(f"处理粘贴内容时出错: {e}")
            super().insertFromMimeData(source_data)
    
    def get_image_data(self):
        """返回图片数据列表"""
        return self.image_data.copy()

class DataSyncUI(QMainWindow):
    """数据同步专用的用户界面"""
    
    def __init__(self, context: Dict, predefined_options: Optional[List[str]] = None):
        super().__init__()
        self.context = context
        self.predefined_options = predefined_options or []
        self.feedback_result = None
        
        self.setWindowTitle("数据同步确认 - Data Sync MCP")
        self.setWindowFlags(self.windowFlags() | Qt.WindowStaysOnTopHint)
        
        # 设置窗口大小和位置
        self.resize(900, 700)
        self.center_window()
        
        self._create_ui()
        self._setup_shortcuts()
    
    def center_window(self):
        """窗口居中显示"""
        screen = QApplication.primaryScreen().geometry()
        x = (screen.width() - self.width()) // 2
        y = (screen.height() - self.height()) // 2
        self.move(x, y)
    
    def _create_ui(self):
        """创建用户界面"""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        layout.setContentsMargins(15, 10, 15, 10)
        
        # 创建标签页
        tab_widget = QTabWidget()
        
        # 基本信息标签页
        info_tab = self._create_info_tab()
        tab_widget.addTab(info_tab, "📊 基本信息")
        
        # 操作确认标签页
        action_tab = self._create_action_tab()
        tab_widget.addTab(action_tab, "⚡ 操作确认")
        
        # 风险评估标签页
        risk_tab = self._create_risk_tab()
        tab_widget.addTab(risk_tab, "⚠️ 风险评估")
        
        layout.addWidget(tab_widget)
        
        # 按钮区域
        button_layout = QHBoxLayout()
        
        cancel_button = QPushButton("❌ 取消")
        cancel_button.clicked.connect(self.close)
        cancel_button.setStyleSheet(self._get_button_style("cancel"))
        
        submit_button = QPushButton("✅ 确认")
        submit_button.clicked.connect(self._submit_feedback)
        submit_button.setStyleSheet(self._get_button_style("submit"))
        
        button_layout.addWidget(cancel_button)
        button_layout.addStretch()
        button_layout.addWidget(submit_button)
        
        layout.addLayout(button_layout)
    
    def _create_info_tab(self) -> QWidget:
        """创建基本信息标签页"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # 任务信息组
        task_group = QGroupBox("📋 任务信息")
        task_layout = QGridLayout(task_group)
        
        task_layout.addWidget(QLabel("任务ID:"), 0, 0)
        task_layout.addWidget(QLabel(self.context.get("task_id", "N/A")), 0, 1)
        
        task_layout.addWidget(QLabel("用户群ID:"), 1, 0)
        task_layout.addWidget(QLabel(self.context.get("audience_id", "N/A")), 1, 1)
        
        task_layout.addWidget(QLabel("操作类型:"), 2, 0)
        task_layout.addWidget(QLabel(self.context.get("operation_type", "N/A")), 2, 1)
        
        task_layout.addWidget(QLabel("时间戳:"), 3, 0)
        task_layout.addWidget(QLabel(self.context.get("timestamp", "N/A")), 3, 1)
        
        layout.addWidget(task_group)
        
        # 操作详情
        details_group = QGroupBox("📝 操作详情")
        details_layout = QVBoxLayout(details_group)
        
        self.details_text = QTextBrowser()
        self.details_text.setMaximumHeight(200)
        self.details_text.setHtml(self._get_operation_details_html())
        details_layout.addWidget(self.details_text)
        
        layout.addWidget(details_group)
        
        layout.addStretch()
        return widget
    
    def _create_action_tab(self) -> QWidget:
        """创建操作确认标签页"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # 预设选项
        if self.predefined_options:
            options_group = QGroupBox("🎯 快速选择")
            options_layout = QVBoxLayout(options_group)
            
            self.option_checkboxes = []
            for option in self.predefined_options:
                checkbox = QCheckBox(option)
                checkbox.setStyleSheet("""
                    QCheckBox {
                        font-size: 14px;
                        padding: 5px;
                    }
                    QCheckBox::indicator {
                        width: 18px;
                        height: 18px;
                    }
                """)
                self.option_checkboxes.append(checkbox)
                options_layout.addWidget(checkbox)
            
            layout.addWidget(options_group)
        
        # 自定义输入
        custom_group = QGroupBox("✏️ 自定义输入")
        custom_layout = QVBoxLayout(custom_group)
        
        self.feedback_text = DataSyncTextEdit()
        self.feedback_text.setPlaceholderText("在此输入您的反馈或说明 (Ctrl+Enter 提交)")
        self.feedback_text.setStyleSheet("""
            QTextEdit {
                border: 1px solid #444;
                border-radius: 5px;
                padding: 10px;
                background-color: #2a2a2a;
                font-size: 13px;
            }
        """)
        custom_layout.addWidget(self.feedback_text)
        
        layout.addWidget(custom_group)
        layout.addStretch()
        return widget
    
    def _create_risk_tab(self) -> QWidget:
        """创建风险评估标签页"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # 风险等级
        risk_group = QGroupBox("🚨 风险等级")
        risk_layout = QVBoxLayout(risk_group)
        
        risk_level = self._get_risk_level()
        risk_label = QLabel(f"当前风险等级: {risk_level}")
        risk_label.setStyleSheet(f"""
            QLabel {{
                font-size: 16px;
                font-weight: bold;
                color: {self._get_risk_color(risk_level)};
                padding: 10px;
            }}
        """)
        risk_layout.addWidget(risk_label)
        
        # 风险说明
        risk_desc = QTextBrowser()
        risk_desc.setHtml(self._get_risk_description(risk_level))
        risk_layout.addWidget(risk_desc)
        
        layout.addWidget(risk_group)
        
        # 建议措施
        suggestions_group = QGroupBox("💡 建议措施")
        suggestions_layout = QVBoxLayout(suggestions_group)
        
        suggestions_text = QTextBrowser()
        suggestions_text.setHtml(self._get_suggestions_html(risk_level))
        suggestions_layout.addWidget(suggestions_text)
        
        layout.addWidget(suggestions_group)
        layout.addStretch()
        return widget
    
    def _get_operation_details_html(self) -> str:
        """获取操作详情的 HTML"""
        operation_type = self.context.get("operation_type", "unknown")
        
        if operation_type == "sync":
            return """
            <h3>🔄 数据同步操作</h3>
            <p>此操作将同步用户群数据，包括：</p>
            <ul>
                <li>从 DMP 获取最新用户群状态</li>
                <li>更新本地数据库中的用户群信息</li>
                <li>验证数据一致性</li>
                <li>记录同步日志</li>
            </ul>
            """
        elif operation_type == "verify":
            return """
            <h3>🔍 数据验证操作</h3>
            <p>此操作将验证数据质量，包括：</p>
            <ul>
                <li>检查 DMP 返回数据的完整性</li>
                <li>验证用户群状态的一致性</li>
                <li>对比历史数据</li>
                <li>生成验证报告</li>
            </ul>
            """
        elif operation_type == "update":
            return """
            <h3>🔄 状态更新操作</h3>
            <p>此操作将更新用户群状态，包括：</p>
            <ul>
                <li>计算新的用户群状态</li>
                <li>更新相关 MID 的状态</li>
                <li>验证状态变更的正确性</li>
                <li>记录状态变更历史</li>
            </ul>
            """
        elif operation_type == "rollback":
            return """
            <h3>⏪ 回滚操作</h3>
            <p>此操作将回滚数据变更，包括：</p>
            <ul>
                <li>撤销最近的数据库变更</li>
                <li>恢复用户群到之前的状态</li>
                <li>验证回滚的完整性</li>
                <li>记录回滚操作日志</li>
            </ul>
            """
        else:
            return f"""
            <h3>❓ 未知操作类型</h3>
            <p>操作类型: {operation_type}</p>
            <p>请确认操作详情</p>
            """
    
    def _get_risk_level(self) -> str:
        """获取风险等级"""
        operation_type = self.context.get("operation_type", "unknown")
        
        if operation_type == "rollback":
            return "HIGH"
        elif operation_type == "sync":
            return "MEDIUM"
        elif operation_type == "update":
            return "MEDIUM"
        elif operation_type == "verify":
            return "LOW"
        else:
            return "UNKNOWN"
    
    def _get_risk_color(self, risk_level: str) -> str:
        """获取风险等级对应的颜色"""
        colors = {
            "LOW": "#4CAF50",      # 绿色
            "MEDIUM": "#FF9800",   # 橙色
            "HIGH": "#F44336",     # 红色
            "CRITICAL": "#9C27B0", # 紫色
            "UNKNOWN": "#9E9E9E"   # 灰色
        }
        return colors.get(risk_level, "#9E9E9E")
    
    def _get_risk_description(self, risk_level: str) -> str:
        """获取风险描述"""
        descriptions = {
            "LOW": """
            <h4>🟢 低风险</h4>
            <p>此操作风险较低，主要影响：</p>
            <ul>
                <li>仅读取数据，不修改</li>
                <li>对系统性能影响较小</li>
                <li>可以安全执行</li>
            </ul>
            """,
            "MEDIUM": """
            <h4>🟡 中等风险</h4>
            <p>此操作存在中等风险，可能影响：</p>
            <ul>
                <li>修改用户群数据</li>
                <li>影响相关业务逻辑</li>
                <li>需要验证数据一致性</li>
            </ul>
            """,
            "HIGH": """
            <h4>🔴 高风险</h4>
            <p>此操作存在高风险，可能影响：</p>
            <ul>
                <li>大规模数据变更</li>
                <li>影响多个用户群</li>
                <li>可能导致数据丢失</li>
                <li>需要谨慎执行</li>
            </ul>
            """,
            "CRITICAL": """
            <h4>🟣 极高风险</h4>
            <p>此操作存在极高风险，可能影响：</p>
            <ul>
                <li>系统稳定性</li>
                <li>数据完整性</li>
                <li>业务连续性</li>
                <li>需要高级权限确认</li>
            </ul>
            """
        }
        return descriptions.get(risk_level, "<p>风险等级未知</p>")
    
    def _get_suggestions_html(self, risk_level: str) -> str:
        """获取建议措施"""
        suggestions = {
            "LOW": """
            <h4>💡 建议措施</h4>
            <ul>
                <li>✅ 可以随时执行</li>
                <li>📊 建议记录操作日志</li>
                <li>⏰ 可在业务高峰期执行</li>
            </ul>
            """,
            "MEDIUM": """
            <h4>💡 建议措施</h4>
            <ul>
                <li>🔍 执行前先验证数据</li>
                <li>⏰ 建议在低峰期执行</li>
                <li>📋 准备回滚方案</li>
                <li>👥 通知相关团队</li>
            </ul>
            """,
            "HIGH": """
            <h4>💡 建议措施</h4>
            <ul>
                <li>🚨 需要高级权限确认</li>
                <li>💾 执行前完整备份</li>
                <li>⏰ 必须在维护窗口执行</li>
                <li>👥 需要团队协作</li>
                <li>📋 准备详细回滚计划</li>
            </ul>
            """,
            "CRITICAL": """
            <h4>💡 建议措施</h4>
            <ul>
                <li>🛑 需要最高权限确认</li>
                <li>💾 多重备份策略</li>
                <li>⏰ 紧急维护窗口</li>
                <li>👥 全员待命</li>
                <li>📞 准备应急联系</li>
                <li>📋 详细应急预案</li>
            </ul>
            """
        }
        return suggestions.get(risk_level, "<p>无特殊建议</p>")
    
    def _get_button_style(self, button_type: str) -> str:
        """获取按钮样式"""
        if button_type == "submit":
            return """
                QPushButton {
                    background-color: #4CAF50;
                    color: white;
                    border: none;
                    padding: 12px 24px;
                    font-size: 14px;
                    font-weight: bold;
                    border-radius: 6px;
                }
                QPushButton:hover {
                    background-color: #45a049;
                }
                QPushButton:pressed {
                    background-color: #3d8b40;
                }
            """
        else:  # cancel
            return """
                QPushButton {
                    background-color: #f44336;
                    color: white;
                    border: none;
                    padding: 12px 24px;
                    font-size: 14px;
                    font-weight: bold;
                    border-radius: 6px;
                }
                QPushButton:hover {
                    background-color: #da190b;
                }
                QPushButton:pressed {
                    background-color: #c1170a;
                }
            """
    
    def _setup_shortcuts(self):
        """设置快捷键"""
        # Ctrl+Enter 提交
        submit_shortcut = QShortcut(QKeySequence("Ctrl+Return"), self)
        submit_shortcut.activated.connect(self._submit_feedback)
        
        # Escape 取消
        cancel_shortcut = QShortcut(QKeySequence("Escape"), self)
        cancel_shortcut.activated.connect(self.close)
    
    def _submit_feedback(self):
        """提交反馈"""
        feedback_text = self.feedback_text.toPlainText().strip()
        selected_options = []
        
        # 获取选中的预设选项
        if hasattr(self, 'option_checkboxes'):
            for i, checkbox in enumerate(self.option_checkboxes):
                if checkbox.isChecked():
                    selected_options.append(self.predefined_options[i])
        
        # 获取图片数据
        image_data = self.feedback_text.get_image_data()
        
        # 组合反馈内容
        final_feedback_parts = []
        
        if selected_options:
            final_feedback_parts.append("; ".join(selected_options))
        
        if feedback_text:
            final_feedback_parts.append(feedback_text)
        
        final_feedback = "\n\n".join(final_feedback_parts)
        images_b64 = [img['base64'] for img in image_data]
        
        self.feedback_result = DataSyncResult(
            interactive_feedback=final_feedback,
            images=images_b64,
            operation_type=self.context.get("operation_type", ""),
            audience_id=self.context.get("audience_id", ""),
            task_id=self.context.get("task_id", "")
        )
        self.close()
    
    def run(self) -> DataSyncResult:
        """运行界面"""
        self.show()
        QApplication.instance().exec()
        
        if not self.feedback_result:
            return DataSyncResult(
                interactive_feedback="",
                images=[],
                operation_type=self.context.get("operation_type", ""),
                audience_id=self.context.get("audience_id", ""),
                task_id=self.context.get("task_id", "")
            )
        
        return self.feedback_result

def data_sync_ui(context: Dict, predefined_options: Optional[List[str]] = None, output_file: Optional[str] = None) -> Optional[DataSyncResult]:
    """启动数据同步 UI"""
    # 启用高 DPI 缩放
    QApplication.setAttribute(Qt.AA_EnableHighDpiScaling)
    QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps)
    
    # 创建应用
    app = QApplication.instance() or QApplication()
    app.setPalette(get_data_sync_palette(app))
    app.setStyle("Fusion")
    
    # 设置字体
    default_font = app.font()
    default_font.setPointSize(13)
    app.setFont(default_font)
    
    # 创建 UI
    ui = DataSyncUI(context, predefined_options)
    result = ui.run()
    
    if output_file and result:
        # 确保目录存在
        os.makedirs(os.path.dirname(output_file) if os.path.dirname(output_file) else ".", exist_ok=True)
        # 保存结果
        with open(output_file, "w", encoding='utf-8') as f:
            json.dump(result, f, ensure_ascii=False, indent=2)
        return None
    
    return result

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="数据同步反馈 UI")
    parser.add_argument("--context", help="上下文数据 JSON")
    parser.add_argument("--predefined-options", default="", help="预设选项 (||| 分隔)")
    parser.add_argument("--output-file", help="输出文件路径")
    args = parser.parse_args()
    
    context = json.loads(args.context) if args.context else {}
    predefined_options = [opt for opt in args.predefined_options.split("|||") if opt] if args.predefined_options else None
    
    result = data_sync_ui(context, predefined_options, args.output_file)
    if result:
        print(f"\n收到的反馈:\n{result['interactive_feedback']}")
    sys.exit(0)

