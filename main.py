import sys
from PySide6.QtCore import Qt, QDir
from PySide6.QtGui import QKeySequence, QAction
from PySide6.QtWidgets import QApplication, QMainWindow, QTextEdit, QMessageBox
from PySide6.QtWidgets import QApplication, QMainWindow, QSplitter, QTreeView, QFileSystemModel, QTextEdit, QListWidget

class SplitWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("PySide6 区域分割 (QSplitter)")
        self.resize(800, 500)

        # 1. 创建一个水平方向的拆分器（默认就是水平 Horizontal）
        main_splitter = QSplitter(Qt.Orientation.Horizontal)

        file_model = QFileSystemModel()
        root_path = QDir.currentPath()
        file_model.setRootPath(root_path)
        
        left_tree = QTreeView()
        left_tree.setModel(file_model)
        left_tree.setRootIndex(file_model.index(root_path))
        # 隐藏多余列，只留文件名
        for i in range(1, file_model.columnCount()):
            left_tree.setColumnHidden(i, True)

        # ====== 【第二栏：中间核心编辑器】 ======
        center_editor = QTextEdit("中间的核心代码/文本编辑区域...")

        # ====== 【第三栏：右侧结构导航/属性栏】 ======
        right_sidebar = QListWidget()
        right_sidebar.addItems(["# 类: MainApp", "  - 函数: __init__", "  - 函数: setup_ui", "# 类: DataModel"])

        # 2. 按从左到右的顺序，将三个组件逐个塞进同一个 Splitter
        main_splitter.addWidget(left_tree)      # 第一栏
        main_splitter.addWidget(center_editor)   # 第二栏
        main_splitter.addWidget(right_sidebar)  # 第三栏

        # 3. 核心设置：控制三栏的“初始宽度比例”
        # 传入一个包含 3 个整数的列表，分别对应第一、二、三栏的初始像素宽度
        main_splitter.setSizes([250, 600, 250])

        # 4. 优化：限制左侧和右侧栏的最小宽度，防止用户把它拖得太小导致画面崩溃
        left_tree.setMinimumWidth(150)
        right_sidebar.setMinimumWidth(150)
        center_editor.setMinimumWidth(300) # 编辑区保证最小宽度

        # 5. 设置为主窗口的中心组件
        self.setCentralWidget(main_splitter)
                # 2. 启用底部的状态栏（用于展示菜单项的悬浮提示）
        self.statusBar()

        # 3. 初始化创建菜单栏
        self.init_menu_bar()
    
    def init_menu_bar(self):
        # 获取主窗口自带的全局菜单栏对象
        menu_bar = self.menuBar()

        # --- 【创建一级主菜单】 ---
        file_menu = menu_bar.addMenu("文件(&F)")  # &F 代表支持 Alt+F 快捷键唤起
        edit_menu = menu_bar.addMenu("编辑(&E)")
        help_menu = menu_bar.addMenu("帮助(&H)")

        # --- 【向“文件”菜单添加具体的子动作 (Action)】 ---
        
        # 新建动作
        new_action = QAction("新建", self)
        new_action.setShortcut(QKeySequence.StandardKey.New) # 自动适配系统的 Ctrl+N (Win) 或 Cmd+N (Mac)
        new_action.setStatusTip("创建一个新文档")            # 鼠标悬浮时在左下角状态栏显示的文案
        new_action.triggered.connect(self.on_new_file)       # 绑定点击触发的方法
        file_menu.addAction(new_action)

        # 打开动作
        open_action = QAction("打开...", self)
        open_action.setShortcut("Ctrl+O")                    # 也可以手动指定字符串快捷键
        open_action.setStatusTip("打开一个已有文档")
        file_menu.addAction(open_action)

        # 添加一条灰色的菜单分割线
        file_menu.addSeparator()

        # 退出动作
        exit_action = QAction("退出", self)
        exit_action.setShortcut("Alt+F4")
        exit_action.setStatusTip("关闭当前程序")
        exit_action.triggered.connect(self.close)            # 直接绑定系统自带的关闭窗口槽函数
        file_menu.addAction(exit_action)

        # # --- 【向“编辑”菜单添加动作】 ---
        # undo_action = QAction("撤销", self)
        # undo_action.setShortcut(QKeySequence.StandardKey.Undo)
        # # 直接把菜单事件关联到文本编辑器自带的撤销功能上！
        # undo_action.triggered.connect(self.text_edit.undo)
        # edit_menu.addAction(undo_action)

        # redo_action = QAction("重做", self)
        # redo_action.setShortcut(QKeySequence.StandardKey.Redo)
        # redo_action.triggered.connect(self.text_edit.redo)
        # edit_menu.addAction(redo_action)

    # 菜单触发对应的自定义槽函数
    def on_new_file(self):
        QMessageBox.information(self, "提示", "你点击了‘新建’菜单！")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = SplitWindow()
    window.show()
    sys.exit(app.exec())