import sys
from PySide6.QtCore import QSettings
from PySide6.QtWidgets import (QApplication, QCheckBox, QDialog, 
                             QDialogButtonBox, QFormLayout, QHBoxLayout,
                             QLabel, QLineEdit, QMainWindow, QMessageBox, 
                             QPushButton, QVBoxLayout, QWidget)
from gui.config import SettingsDialog

class CustomSettingsManager:
    def __init__(self, main_window):
        self.main_win = main_window

    def open_settings_dialog(self):
        """打开设置弹窗"""
        dialog = SettingsDialog(self.main_win)
        # exec() 会阻塞主窗口，直到弹窗关闭
        # 如果返回 QDialog.DialogCode.Accepted 说明用户点击了“确定”并成功保存
        if dialog.exec() == QDialog.DialogCode.Accepted:
            QMessageBox.information(self.main_win, "提示", "设置已更新！")
            self.refresh_ui()  # 刷新主界面显示

    def refresh_ui(self):
        """从 QSettings 读取最新配置并刷新主界面"""
        settings = QSettings("MyCompany", "MyPySideApp")
        username = settings.value("username", "Guest")
        auto_save = settings.value("auto_save", False, type=bool)
        dark_mode = settings.value("dark_mode", False, type=bool)
        
        status_text = (
            f"当前登录用户: {username}\n"
            f"自动保存状态: {'开启' if auto_save else '关闭'}\n"
            f"当前主题模式: {'深色模式' if dark_mode else '浅色模式'}"
        )
        # self.main_win.info_label.setText(status_text)

  
