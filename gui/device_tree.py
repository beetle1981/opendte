import os
from PySide6.QtGui import QStandardItem, QStandardItemModel
# 💡 补全 QMenu 和 QMessageBox 的导入
from PySide6.QtWidgets import QTreeView, QVBoxLayout, QWidget, QMenu, QMessageBox, QHeaderView
from PySide6.QtCore import Signal, Qt, QPoint
from lib.dmanager import OpenDeviceTreeManager

class CustomDeviceTreeView(QWidget):
    # 声明文件加载成功的信号
    file_loaded = Signal(str)
    node_selected = Signal(object)  # 广播被点击的 OpenDeviceTreeNode 对象

    def __init__(self, dts_file_path=None, parent=None):
        super().__init__(parent)
        self.filepath = dts_file_path
        
        # 1. 统一布局管理
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        self.tree_view = QTreeView(self)
        layout.addWidget(self.tree_view)


        # 🚀 【新增】：禁用双击编辑，使树视图在界面上表现为只读
        self.tree_view.setEditTriggers(QTreeView.EditTrigger.NoEditTriggers)
        
        # 初始化一个空模型，防止初始化时未刷新报错
        self.model = QStandardItemModel()
        self.tree_view.setModel(self.model)

        # 2. 🚀 【核心修复 1】：将右键菜单策略和信号绑定给内部真正的树视图 self.tree_view
        self.tree_view.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.tree_view.customContextMenuRequested.connect(self.show_context_menu)
        # 必须在 tree_view 已经设置了 model 之后调用
        self.tree_view.header().setSectionResizeMode(QHeaderView.ResizeToContents)

        self.tree_view.clicked.connect(self.on_tree_node_clicked)

    def on_tree_node_clicked(self, index):
        if not index.isValid():
            return

        # 1. 强行对齐到第 0 列
        first_column_index = index.siblingAtColumn(0)

        # 2. 提取标准的 UserRole
        node_object = first_column_index.data(Qt.ItemDataRole.UserRole)

        if node_object:
            self.node_selected.emit(node_object)
        else:
            print("两端已对齐标准Role，但依旧没有拿到数据，请看方案 B 调试")


    def refresh_view(self, file_path):
        """
        从设备树中提取最新的 qt_model 并同步到 QTreeView 上
        """
        self.filepath = file_path
        # 1. 重新从虚拟属性获取最新的 Model 实例
        manager = OpenDeviceTreeManager(file_path)
        
        self.model = manager.new_tree.qt_model if file_path else QStandardItemModel()
            
        # 2. 将新模型绑定给视图
        self.tree_view.setModel(self.model)
        
        # 3. 自动展开第一层节点
        self.tree_view.expandToDepth(0)
        
        # 触发加载成功信号
        self.file_loaded.emit(file_path)

    def show_context_menu(self, pos: QPoint):
        """当用户在 TreeView 上右键点击时触发"""
        # 🚀 【核心修复 2】：使用真正树视图的 indexAt 来精准定位被右键的行
        index = self.tree_view.indexAt(pos)
        
        # 创建右键菜单
        menu = QMenu(self)
        
        if index.isValid():
            # ------ 情况 A：用户右键点击了某个具体的节点 ------
            # 拿到我们在 qt_model 中挂载到 UserRole + 1 的原生 Python 节点对象
            dt_node = index.data(Qt.ItemDataRole.UserRole + 1)
            
            action_info = menu.addAction(f"查看路径: {dt_node.name if dt_node else '未知'}")
            action_edit = menu.addAction("编辑属性 (Properties)")
            menu.addSeparator() 
            action_delete = menu.addAction("删除当前节点")
            
            # 🚀 【核心修复 3】：坐标转换映射，确保菜单弹在 tree_view 鼠标点击的物理位置
            selected_action = menu.exec(self.tree_view.mapToGlobal(pos))
            
            if selected_action == action_edit:
                self.on_edit_node_properties(dt_node)
            elif selected_action == action_delete:
                self.on_delete_node(index, dt_node)
                
        else:
            # ------ 情况 B：用户右键点击了树状图的空白处 ------
            action_expand_all = menu.addAction("展开全部节点")
            action_collapse_all = menu.addAction("折叠全部节点")
            
            selected_action = menu.exec(self.tree_view.mapToGlobal(pos))
            
            if selected_action == action_expand_all:
                self.tree_view.expandAll()
            elif selected_action == action_collapse_all:
                self.tree_view.collapseAll()

    # --- 具体的业务槽函数 ---
    def on_edit_node_properties(self, dt_node):
        if dt_node:
            print(f"准备编辑节点属性: {dt_node.path}")
            print(f"当前属性列表: {dt_node.properties}")

    def on_delete_node(self, index, dt_node):
        reply = QMessageBox.question(
            self, "确认删除", 
            f"确定要删除节点 {dt_node.name} 吗？\n这将连带删除其所有子节点！",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if reply == QMessageBox.StandardButton.Yes:
            # 🚀 【核心修复 4】：self.model 是属性对象，不是成员函数，去掉原先的多余括号
            self.model.removeRow(index.row(), index.parent())
            
            # 从底层的 Python 设备树数据结构中切断连接
            if dt_node and dt_node.parent:
                if dt_node.name in dt_node.parent.children:
                    del dt_node.parent.children[dt_node.name]
            print(f"物理节点已删除: {dt_node.path}")
