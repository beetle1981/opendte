import os, re
from PySide6.QtGui import QStandardItemModel, QStandardItem
from PySide6.QtCore import Qt

class OpenDeviceTreeNode:
    def __init__(self, name, label=None, parent=None):
        self.name = name
        self.label = label
        self.properties = {}

        self.children = {}
        self.parent = parent

    @property
    def path(self) -> str:
        """递归获取节点的绝对路径"""
        if self.parent is None or self.parent.name == "/":
            return f"/{self.name}" if self.name != "/" else "/"
        return f"{self.parent.path}/{self.name}"

    @property
    def phandle(self) -> str:
        for prop in self.properties:
            print(prop)

    @property
    def nodes(self):
        return list(self.traverse())

    def add_child(self, child_name: str, label=None):
        """创建并添加一个子节点"""
        child_node = OpenDeviceTreeNode(child_name, label=label, parent=self)
        self.children[child_name] = child_node
        return child_node

    def __repr__(self):
        return f"<DTNode: {self.path}>"

    # customer function

    def traverse(self):
        print(f"路径: {self.path.ljust(150)} | 名字(Name): {self.name.ljust(30)} | 标签(Label): {str(self.label).ljust(20)} | 属性数: {len(self.properties)}")
        yield self
        for child in self.children.values():
            yield from child.traverse()

    @property
    def qt_model(self):
        """
        动态将当前节点及其子树转换为 QStandardItemModel 虚拟属性。
        直接支持：model = node.qt_model
        """
        # 1. 动态兼容导入 PySide6 或 PyQt6
        model = QStandardItemModel()
        model.setHorizontalHeaderLabels(["名字 (Name)", "标签 (Label)", "属性数"])

        def add_node_to_item(qt_parent, dt_node):
            item_name = QStandardItem(dt_node.name)
            item_label = QStandardItem(str(dt_node.label) if dt_node.label else "")
            item_props_count = QStandardItem(str(len(dt_node.properties)))
            
            # 将当前原生节点挂载到 Item 数据中，方便 UI 点击交互
            item_name.setData(dt_node, role=Qt.UserRole + 1)
            
            row = [item_name, item_label, item_props_count]
            qt_parent.appendRow(row)
            
            for child_node in dt_node.children.values():
                add_node_to_item(item_name, child_node)

        # 如果是根节点 '/'，为了不让 UI 多套一层无意义的根目录，直接展开它的子节点
        if self.name == "/" and self.children:
            for child in self.children.values():
                add_node_to_item(model, child)
        else:
            add_node_to_item(model, self)

        return model

    # def get_node(self, name: str, )