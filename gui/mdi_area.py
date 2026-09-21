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
        self.setViewMode(self.ViewMode.TabbedView)
        self.setTabsClosable(True)
        self.setTabsMovable(True)

        self.subWindowActivated.connect(self.on_sub_window_activated)

        # 🌟 完美的 QTabBar 激活蓝色背景、白色文字样式表
        # tab_style = """
        # QTabBar::tab {
        #     background-color: #f0f0f0;  /* 未激活标签页的背景色 */
        #     color: #333333;             /* 未激活标签页的文字颜色 */
        #     padding: 8px 16px;          /* 标签页内边距 */
        #     border: 1px solid #dcdfe6;
        #     border-bottom: none;
        #     border-top-left-radius: 4px;
        #     border-top-right-radius: 4px;
        #     min-width: 80px;
        # }

        # QTabBar::tab:selected {
        #     background-color: #0078d7;  /* 🚀 核心：激活（选中）状态显示为经典蓝色 */
        #     color: #ffffff;             /* 🚀 核心：激活（选中）状态文字显示为纯白色 */
        #     border-color: #0078d7;
        #     font-weight: bold;          /* 可选：加粗文字使其更明显 */
        # }

        # QTabBar::tab:hover:!selected {
        #     background-color: #e6f7ff;  /* 可选：鼠标悬停在未选中标签上的颜色 */
        # }
        # """

        # # 🌟 在你的 MdiManagerArea 初始化中应用它
        # self.setStyleSheet(tab_style)


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
            with open(file_path, 'r', encoding='utf-8') as f:
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
