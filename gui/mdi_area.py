from PySide6.QtWidgets import QMdiArea, QTextEdit, QMessageBox, QFileDialog
from PySide6.QtCore import Signal, Qt
import os

# class CustomTextEditor(QTextEdit):
class MdiManagerArea(QMdiArea):
    # Signal emitted when a text file is successfully loaded, carrying the file path
    file_loaded = Signal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        # 在这里可以设置 MDI 区域的背景或滚动条策略
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)

    def create_new_document(self):
        """新建一个文本文档子窗口"""
        text_edit = QTextEdit()

        text_edit.setUndoRedoEnabled(True)
        
        # 将组件添加到 MDI 区域，并返回子窗口对象
        sub_window = self.addSubWindow(text_edit)
        sub_window.setWindowTitle("No Title")
        sub_window.resize(400, 300)
        sub_window.show()
        return sub_window

    def load_file_content(self, file_path):
        """Reads file data safely and updates the editor layout."""
        if os.path.isfile(file_path):
            try:
                # Attempt to open and read with standard UTF-8 encoding
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()

                    text_edit = QTextEdit()
                    text_edit.setPlainText(content)

                    sub_window = self.addSubWindow(text_edit)
                    sub_window.setWindowTitle(file_path)
                    sub_window.resize(400, 300)
                    sub_window.show()
                
                # Emit signal to notify main script for window title modifications
                self.file_loaded.emit(file_path)
                
            except Exception as e:
                QMessageBox.critical(
                    self, 
                    "Read Error", 
                    f"Could not open this file (it might not be a valid text format).\nReason: {str(e)}"
                )


    def undo_active_doc(self):
        """对当前激活的子窗口执行撤销"""
        active_sub = self.activeSubWindow()
        if active_sub:
            # 获取包裹在子窗口内部的 QTextEdit 控件
            text_edit = active_sub.widget()
            if isinstance(text_edit, QTextEdit):
                text_edit.undo()

    def redo_active_doc(self):
        """对当前激活的子窗口执行重做"""
        active_sub = self.activeSubWindow()
        if active_sub:
            text_edit = active_sub.widget()
            if isinstance(text_edit, QTextEdit):
                text_edit.redo()

    def open_existing_document(self):
        """打开现有文件"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "打开文件", "", "文本文件 (*.txt);;所有文件 (*.*)"
        )
        if not file_path:
            return None

        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()
            
            text_edit = QTextEdit()
            text_edit.setUndoRedoEnabled(True)
            text_edit.setPlainText(content)
            
            # 【关键】记录当前文件的真实路径
            text_edit.file_path = file_path
            
            sub_window = self.addSubWindow(text_edit)
            # 窗口标题只显示文件名，不显示冗长的全路径
            sub_window.setWindowTitle(os.path.basename(file_path))
            sub_window.resize(400, 300)
            sub_window.show()
            return sub_window
            
        except Exception as e:
            QMessageBox.warning(self, "错误", f"无法读取文件:\n{e}")
            return None

    def save_active_doc(self):
        """保存当前激活的子窗口"""
        active_sub = self.activeSubWindow()
        if not active_sub:
            return
            
        text_edit = active_sub.widget()
        if not isinstance(text_edit, QTextEdit):
            return

        # 如果 file_path 为 None，说明是新建的文件，去走“另存为”流程
        if text_edit.file_path is None:
            self.save_as_active_doc()
        else:
            # 已经是存在的文件，直接静默覆盖保存
            self._write_to_file(text_edit.file_path, text_edit, active_sub)

    def save_as_active_doc(self):
        """当前激活窗口另存为"""
        active_sub = self.activeSubWindow()
        if not active_sub:
            return
            
        text_edit = active_sub.widget()
        if not isinstance(text_edit, QTextEdit):
            return

        # 弹出保存文件对话框
        file_path, _ = QFileDialog.getSaveFileName(
            self, "保存文件", "", "文本文件 (*.txt);;所有文件 (*.*)"
        )
        if file_path:
            self._write_to_file(file_path, text_edit, active_sub)

    def _write_to_file(self, file_path, text_edit, sub_window):
        """内部核心写入方法"""
        try:
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(text_edit.toPlainText())
            
            # 更新路径属性和窗口标题
            text_edit.file_path = file_path
            sub_window.setWindowTitle(os.path.basename(file_path))
            
            # 可以在状态栏提示或短暂弹窗，这里简单处理
        except Exception as e:
            QMessageBox.warning(self, "错误", f"无法保存文件:\n{e}")
