import os

from PySide6.QtWidgets import QMdiArea, QTextEdit, QMessageBox, QFileDialog
from PySide6.QtCore import Signal, Qt
from lib.dmanager import OpenDeviceTreeManager

# class CustomTextEditor(QTextEdit):
class MdiManagerArea(QMdiArea):
    # Signal emitted when a text file is successfully loaded, carrying the file path
    file_loaded = Signal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        # 在这里可以设置 MDI 区域的背景或滚动条策略
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.setViewMode(self.ViewMode.TabbedView)
        self.setTabsClosable(True)
        self.setTabsMovable(True)

        self.subWindowActivated.connect(self.on_sub_window_activated)

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

    def restore_dts(self):
        active_sub = self.activeSubWindow()
        if not active_sub:
            return
            
        text_edit = active_sub.widget()
        if not isinstance(text_edit, QTextEdit):
            return
        dt = OpenDeviceTreeManager(text_edit.file_path)
        
        print(f"File Path: {text_edit.file_path}")
        sub_window = self.create_new_document()
        text_edit = sub_window.widget()
        text_edit.setPlainText("Processing")        
        text_edit.setPlainText(dt.trees_devide().to_dts_file)
        return

    def load_file_content(self, file_path):
        """双击左侧文件树时安全读取文件或激活已打开的编辑器视图"""
        if not os.path.isfile(file_path):
            return

        # 🚀【核心修改】：遍历所有已打开的子窗口，防止重复打开
        for sub_window in self.subWindowList():
            if hasattr(sub_window, 'filepath') and sub_window.filepath == file_path:
                # 🌟 找到了已经打开的同名文件窗口，直接将其设为当前激活窗口并返回
                self.setActiveSubWindow(sub_window)
                # 显式发射信号，确保左下角设备树强制同步刷新（防触发钝化）
                self.file_loaded.emit(file_path)
                return

        # 🌟 如果没找到已打开的窗口，则走原有的新建/读取流程
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()

                text_edit = QTextEdit()
                text_edit.setUndoRedoEnabled(True)
                text_edit.setPlainText(content)
                
                # 为 widget 和 sub_window 同时挂载相同规范的路径名
                text_edit.file_path = file_path

                sub_window = self.addSubWindow(text_edit)
                sub_window.setWindowTitle(os.path.basename(file_path))
                sub_window.filepath = file_path # 供激活信号读取
                
                sub_window.resize(400, 300)
                sub_window.show()
                
                self.file_loaded.emit(file_path)
                            
        except Exception as e:
            QMessageBox.critical(
                self, 
                "Read Error", 
                f"Could not open this file (it might not be a valid text format).\nReason: {str(e)}"
            )

    def on_sub_window_activated(self, sub_window):
        """当用户切换选项卡或激活不同的 MDI 子窗口时触发"""
        # 1. 防御性检查：如果 sub_window 为 None 或不是有效的子窗口对象，直接拦截返回
        if not sub_window or isinstance(sub_window, str):
            return

        # 2. 🚀【核心修复】：确保提取出来的 file_path 必须是真正的字符串，而不是窗口对象本身
        file_path = None
        
        # 优先尝试从窗口容器的属性上安全获取路径字符串
        if hasattr(sub_window, 'filepath') and isinstance(sub_window.filepath, str):
            file_path = sub_window.filepath
        else:
            # 如果容器上没有，尝试去内部的文本编辑器上拿
            try:
                text_edit = sub_window.widget()
                if text_edit and hasattr(text_edit, 'file_path') and isinstance(text_edit.file_path, str):
                    file_path = text_edit.file_path
                    sub_window.filepath = file_path  # 顺手做好对齐挂载
            except Exception:
                pass  # 防止中间转换过程中有其他非文本组件导致崩溃

        # 3. 只有当拿到的路径是【绝对合法的字符串】时，才允许发射信号去刷新设备树
        if file_path and isinstance(file_path, str) and os.path.isfile(file_path):
            self.file_loaded.emit(file_path)


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

    def close_all_documents(self):
        """
        🚀【外部调用接口】：一键安全关闭所有 QTextEdit 子窗口
        """
        # 逐个检查并关闭子窗口
        for sub_window in self.subWindowList():
            # 1. 临时将其切为活动窗口，增强视觉提示
            self.setActiveSubWindow(sub_window)
            
            # 2. 调用单窗口检查，如果用户点击了“取消”，直接中断整个关闭链条
            if not self.check_and_save_sub_window(sub_window):
                print("用户中止了全部关闭流程")
                return
                
            # 3. 检查通过（已存/无改动/选择不存），安全关闭当前子窗口
            sub_window.close()
        self.file_loaded.emit("")

    # ----------------------------------------------------
    # 其余原有的保存、撤销、激活等方法均保持不变...
    # ----------------------------------------------------
    def on_sub_window_activated(self, sub_window):
        if not sub_window or isinstance(sub_window, str):
            return
        file_path = None
        if hasattr(sub_window, 'filepath') and isinstance(sub_window.filepath, str):
            file_path = sub_window.filepath
        else:
            try:
                text_edit = sub_window.widget()
                if text_edit and hasattr(text_edit, 'file_path') and isinstance(text_edit.file_path, str):
                    file_path = text_edit.file_path
                    sub_window.filepath = file_path  
            except Exception:
                pass  
        if file_path and isinstance(file_path, str) and os.path.isfile(file_path):
            self.file_loaded.emit(file_path)
    def check_and_save_sub_window(self, sub_window) -> bool:
            """
            检查单个子窗口是否需要保存。
            返回值: True 代表可以安全关闭（已保存、未修改或用户选择放弃）; False 代表用户点击了取消
            """
            if not sub_window:
                return True
                
            text_edit = sub_window.widget()
            if not isinstance(text_edit, QTextEdit):
                return True

            # 💡 利用 Qt 原生的 isModified() 机制判断文本是否被动过
            if text_edit.document().isModified():
                # 获取文档名称提示用户
                doc_name = sub_window.windowTitle()
                
                # 弹出标准的“是/否/取消”确认提示框
                reply = QMessageBox.question(
                    self,
                    "未保存的更改",
                    f"文档 '{doc_name}' 已被修改，是否保存？",
                    QMessageBox.StandardButton.Yes | 
                    QMessageBox.StandardButton.No | 
                    QMessageBox.StandardButton.Cancel,
                    QMessageBox.StandardButton.Yes
                )
                
                if reply == QMessageBox.StandardButton.Yes:
                    # 走保存流程
                    if text_edit.file_path is None:
                        # 如果是新文件，弹出另存为对话框
                        file_path, _ = QFileDialog.getSaveFileName(
                            self, f"另存为 - {doc_name}", "", "文本文件 (*.txt);;所有文件 (*.*)"
                        )
                        if file_path:
                            return self._write_to_file(file_path, text_edit, sub_window)
                        return False  # 用户在另存为弹窗中点了取消
                    else:
                        # 已有文件，直接静默覆盖保存
                        return self._write_to_file(text_edit.file_path, text_edit, sub_window)
                        
                elif reply == QMessageBox.StandardButton.Cancel:
                    return False  # 用户中止了关闭流程
                    
            return True  # 未修改或用户明确点击了 "No"（不保存），允许安全关闭
