import os
from PySide6.QtGui import QStandardItem, QStandardItemModel
from PySide6.QtWidgets import QTreeView, QVBoxLayout, QWidget
from PySide6.QtCore import Signal, Qt
from lib.odtlib import OpenDeviceTree
from lib.dnode import OpenDeviceTreeNode


# class CustomDeviceTreeView(QWidget):
#     file_loaded = Signal(str)

#     def __init__(self, dts_file_path=None):
#         super().__init__()
        
#         self.tree_view = QTreeView(self)
#         self.tree = OpenDeviceTree(dts_file_path)
#         self.model = self.tree.qt_model
#         self.model.setHorizontalHeaderLabels(["节点名称 (Node)", "属性 (Properties)"])
#         self.tree_view.setModel(self.model)
        
#         if dts_file_path:
#             self.load_dts_file(dts_file_path)

class CustomDeviceTreeView(QWidget):
    # 声明文件加载成功的信号
    file_loaded = Signal(str)

    def __init__(self, dts_file_path=None, parent=None):
        super().__init__(parent)
        self.filepath = dts_file_path
        # 1. 统一布局管理
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        self.tree_view = QTreeView(self)
        layout.addWidget(self.tree_view)
        
        # 2. 弱耦合初始化：先实例化解析引擎
        # 💡 注意：建议确保 OpenDeviceTree 内部支持传入空路径时不崩溃
        
        self.model = QStandardItemModel()

    def refresh_view(self, file_path):
        """
        从设备树中提取最新的 qt_model 并同步到 QTreeView 上
        """
        # 1. 重新从虚拟属性获取最新的 Model 实例
        self.model = OpenDeviceTree(file_path).root_node.qt_model
        
        # 2. 💡 动态覆盖/定制当前组件需要的表头名称
        # 如果你想保持你在类属性里定义的3列，那就不要改；如果想强行改成 2 列，需要确保底层数据列数匹配
        # 这里演示如何更改表头文字：
        if self.model and self.model.columnCount() >= 2:
            self.model.setHorizontalHeaderLabels(["节点名称 (Node)", "额外信息"])
            
        # 3. 将新模型绑定给视图
        self.tree_view.setModel(self.model)
        
        # 4. 可选：自动展开第一层节点
        self.tree_view.expandToDepth(0)
