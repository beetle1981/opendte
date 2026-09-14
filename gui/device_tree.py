import os
from pydevicetree import Devicetree
from PySide6.QtGui import QStandardItem, QStandardItemModel
from PySide6.QtWidgets import QTreeView, QVBoxLayout, QWidget
from PySide6.QtCore import Signal, Qt


class CustomDeviceTreeView(QWidget):
    file_loaded = Signal(str)

    def __init__(self, dts_file_path=None):
        super().__init__()
        
        self.tree_view = QTreeView(self)
        
        self.model = QStandardItemModel()
        self.model.setHorizontalHeaderLabels(["节点名称 (Node)", "属性 (Properties)"])
        self.tree_view.setModel(self.model)
        
        if dts_file_path:
            self.load_dts_file(dts_file_path)
            
    def load_dts_file(self, file_path):
        try:
            # 使用 pydevicetree 的 parseFile 方法直接解析文件
            # 如果你的 DTS 中带有 #include 且本地装有 gcc/cpp，它可以自动调用系统预处理器
            tree = Devicetree.parseFile(file_path)
            
            self.model.removeRows(0, self.model.rowCount())
            
            # tree.root 即可直接获取根节点对象
            build_qt_tree_from_pydevicetree(tree.root, self.model.invisibleRootItem())
            
            self.tree_view.expandToDepth(1)
            self.tree_view.resizeColumnToContents(0)
            print("pydevicetree 解析并渲染成功！")
            
        except Exception as e:
            print(f"pydevicetree 解析失败: {e}")

def build_qt_tree_from_pydevicetree(node, qt_parent_item):
    """
    使用 pydevicetree 库的数据结构递归构建树形 UI
    """
    # 1. 确定当前节点的显示名称 (如果是根节点，其名称通常为空，显示为 "/")
    node_name = node.name if node.name else "/"
    name_item = QStandardItem(node_name)
    
    # 2. 提取当前节点的所有属性
    prop_list = []
    # node.properties 是一个包含 Property 对象的列表
    for prop in node.properties:
        # prop.name 是键名 (如 "compatible"), prop.value 是解析好的值 (字符串、列表或整数)
        prop_list.append(f"{prop.name} = {prop.value}")
    
    props_str = "; ".join(prop_list)
    props_item = QStandardItem(props_str)
    
    # 3. 将名称和属性作为“一行(Row)”添加到父级节点
    qt_parent_item.appendRow([name_item, props_item])
    
    # 4. 递归处理所有的子节点 (node.children 是一个包含子节点对象的列表)
    for child in node.children:
        build_qt_tree_from_pydevicetree(child, name_item)

