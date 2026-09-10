    
from PySide6.QtWidgets import QFileDialog
from PySide6.QtCore import QDir
    # 核心功能：打开文件夹槽函数
def on_open_folder(self):
    # 弹出 Windows 原生文件夹选择对话框
    # 参数说明：self, 对话框标题, 默认打开路径（这里设为当前用户工作目录）
    selected_directory = QFileDialog.getExistingDirectory(
        self, 
        "选择要打开的文件夹", 
        QDir.currentPath(),
        QFileDialog.Option.ShowDirsOnly # 只显示文件夹
    )

    # 如果用户点击了“取消”或者没选文件夹，selected_directory 会返回空字符串
    if selected_directory:
        # 1. 更新文件系统模型的根路径
        self.file_model.setRootPath(selected_directory)
        # 2. 让树状视图定位并展示这个新路径
        self.tree_view.setRootIndex(self.file_model.index(selected_directory))
        # 3. 联动更新主窗口的标题，显示当前打开的项目路径
        self.setWindowTitle(f"PySide6 现代编辑器 - {selected_directory}")
        self.text_editor.setPlainText(f"已成功加载文件夹：{selected_directory}\n请在左侧双击文件进行编辑。")
        self.statusBar().showMessage(f"当前工作目录: {selected_directory}", 3000)