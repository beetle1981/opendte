import sys
from PySide6.QtWidgets import QMdiSubWindow, QApplication, QMainWindow, QSplitter, QTableView, QHeaderView, QAbstractItemView
from PySide6.QtCore import Qt
import os

from gui.file_tree import CustomFileTreeView
from gui.menu_bar import CustomMenuBar
from gui.mdi_area import MdiManagerArea
from gui.device_tree import CustomDeviceTreeView

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Open Device Tree Editor")
        self.resize(1100, 600)

        # Enable the status bar at the bottom
        self.statusBar()

        # Instantiate sub-components
        self.file_tree = CustomFileTreeView()
        self.device_tree = CustomDeviceTreeView()
        self.mdi_manager = MdiManagerArea()
        self.property_table = QTableView()
        
        # Assemble UI layout using QSplitter
        main_splitter = QSplitter(Qt.Orientation.Horizontal)
        main_splitter.addWidget(self.file_tree)    # Left Column
        main_splitter.addWidget(self.mdi_manager)    # Center Column
        main_splitter.addWidget(self.device_tree)  # Right Column
        main_splitter.addWidget(self.property_table) #Right Column2
        main_splitter.setSizes([150, 500, 200, 250])         # Initial column widths
        self.setCentralWidget(main_splitter)

        # Initialize and attach the menu bar
        self.menu_manager = CustomMenuBar(self)

        # Establish cross-module signal communications
        self.file_tree.file_double_clicked.connect(self.mdi_manager.load_file_content)
        # self.mdi_manager.subWindowActivated.connect(self.device_tree.refresh_view)
        self.mdi_manager.file_loaded.connect(self.update_window_title)
        self.device_tree.node_selected.connect(self.show_node_properties)

        # self.mdi_manager.subWindowActivated.connect(self.mdi_manager.on_sub_window_activated)
        self.mdi_manager.file_loaded.connect(self.device_tree.refresh_view)       

    def show_node_properties(self, node):
        """接收被点击的物理节点对象，生成表格模型并刷新视图"""
        if node:
            # 1. 动态生成与该节点绑定的属性表格模型
            table_model = node.properties_qt_model
            
            # 2. 直接绑定给右侧的 TableView，界面自动刷新
            self.property_table.setModel(table_model)
            self.property_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents) # 先整体自适应
            self.property_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
            # 🌟 核心：彻底禁用所有编辑触发行为（如双击、回车等），使表格变为只读
            self.property_table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)

    def update_window_title(self, file_path):
        file_name = os.path.basename(file_path)
        self.setWindowTitle(f"Editing: {file_name} - Open Device Tree Editor")
        self.statusBar().showMessage(f"Successfully opened: {file_name}", 3000)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    main_win = MainWindow()
    main_win.show()
    sys.exit(app.exec())
