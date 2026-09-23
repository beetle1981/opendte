import sys, os
from pathlib import Path
from PySide6.QtCore import QSettings
from PySide6.QtGui import QAction
from PySide6.QtWidgets import (QApplication, QCheckBox, QDialog, 
                             QDialogButtonBox, QFormLayout, QHBoxLayout,
                             QLabel, QLineEdit, QMainWindow, QMessageBox, 
                             QPushButton, QVBoxLayout, QWidget, QFileDialog)

class SettingsDialog(QDialog):
    """软件设置弹窗"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Kernel path configuration（内核目录设置）")
        self.resize(500, 200)
        
        # 初始化配置存储
        self.settings = QSettings("RoyStudio", "OpenDTE")
        
        # 1. 创建表单布局和控件
        layout = QVBoxLayout()
        form_layout = QFormLayout()
        hbox_layout = QHBoxLayout()
        
        self.kernel_path_input =  QLineEdit()
        self.kernel_path_input.setPlaceholderText("Please select folder...")
        self.kernel_path_input.setReadOnly(True)

        browse_btn = QPushButton("Browse（浏览）...")
        browse_btn.clicked.connect(self.choose_folder)
        browse_btn.setFixedWidth(100)

        note_label = QLabel("Note: this path use to find the dts-binding folder in kernel files.")
        note_label.setStyleSheet("color: blue; font-weight: bold;")

        hbox_layout.addWidget(self.kernel_path_input)
        hbox_layout.addWidget(browse_btn)

        form_layout.addRow("Kernel Path（内核目录）:", hbox_layout)

        layout.addLayout(form_layout)
        
        # 2. 创建标准的“确定/取消”按钮组
        self.button_box = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )

        default_btn = QPushButton("Default")
        default_btn.clicked.connect(self.load_default_settings)
        # default_btn.setFixedWidth(100)

        self.button_box.addButton(default_btn, QDialogButtonBox.ButtonRole.ActionRole)
        
        self.button_box.accepted.connect(self.save_and_accept)  # 点击确定
        self.button_box.rejected.connect(self.reject)           # 点击取消
        layout.addWidget(note_label)
        layout.addWidget(self.button_box)
        
        self.setLayout(layout)
        
        # 3. 打开弹窗时，先加载当前已有的配置到界面上
        self.load_current_settings()

    def load_current_settings(self):
        """将当前存储的配置回显到弹窗控件中"""
        self.kernel_path_input.setText(self.settings.value("kernelpath", "~/kernel"))

    def load_default_settings(self):
        current_dir = str(Path.cwd())
        print(current_dir)
        self.kernel_path_input.setText(current_dir)

    def save_and_accept(self):
        """点击确定时，保存数据并关闭弹窗"""
        self.settings.setValue("kernelpath", self.kernel_path_input.text())
        
        self.accept() # 触发成功关闭信号，通知主窗口配置已变动


    # def clear_settings(self):
    #     """清除配置并恢复默认"""
    #     self.settings.clear()
    #     QMessageBox.information(self, "提示", "配置已重置，下次启动生效。")

    def choose_folder(self):
        current_path = self.kernel_path_input.text()
        initial_dir = current_path if current_path else os.path.expanduser("~")
        
        # 弹出原生文件夹选择器
        selected_dir = QFileDialog.getExistingDirectory(
            self,
            caption="选择文件夹",
            dir=initial_dir,
            options=QFileDialog.Option.ShowDirsOnly  # 关键：只显示和允许选择文件夹
        )
        
        # 如果用户没有点取消（即选择了有效路径），则更新输入框
        if selected_dir:
            # os.path.normpath 可以自动将 Qt 的 '/' 转换为符合当前系统规范的斜杠（如 Windows 的 '\'）
            standard_path = os.path.normpath(selected_dir)
            self.kernel_path_input.setText(standard_path)
