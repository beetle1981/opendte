import os, re
from PySide6.QtGui import QStandardItemModel, QStandardItem
from PySide6.QtCore import Qt
from lib.portor import OpenDeviceTreePortor

class OpenDeviceTreeNode:
    def __init__(self, name=None, label=None, parent=None):
        self.name = name
        self.label = label
        self._phandle = None
        self.properties = {}

        self.children = {}
        self.parent = parent

    @property
    def path(self) -> str:
        """递归获取节点的绝对路径"""
        if self.parent is None or self.parent.name == "/":
            return f"/{self.name}" if self.name != "/" else "/"
        return f"{self.parent.path}/{self.name}"

    def find_node_by_path(self, node, path):
        if node.path == path:
            return node
        for child in node.children.values():
            return self.find_node_by_path(child, path)
        return None
    
    @property
    def phandle(self):
        """原有的只读获取方法（保持你底层的逻辑不变）"""
        return getattr(self, '_phandle', None)

    # 🚀【核心修复】：使用 .setter 声明，且函数名必须继续叫 phandle
    @phandle.setter
    def phandle(self, value: str):
        """允许外部安全写入修改 phandle 值"""
        # 将传入的值绑定到底层的私有变量上（通常是 _phandle）
        self._phandle = value
        print(f"DEBUG: [OpenDeviceTreeNode] 成功写入核心属性 phandle = {value}")

    @property
    def nodes(self):
        return list(self.traverse())

    def add_child(self, child_name: str, label=None):
        """创建并添加一个子节点"""
        child_node = OpenDeviceTreeNode(child_name, label=label, parent=self)
        self.children[child_name] = child_node
        return child_node

    def find_node(self, name: str = None, label: str = None):
        """全能查询函数：在整棵树中深度优先搜索（DFS）匹配 name 或 label 的节点。"""
        stack = [self]
        while stack:
            curr = stack.pop()
            if label is not None and curr.label == label:
                return curr
            
            clean_search_name = name.strip() if name else None
            if clean_search_name and "aliases" in clean_search_name.lower():
                clean_search_name = "aliases"
                
            if clean_search_name and curr.name == clean_search_name:
                return curr
            stack.extend(curr.children.values())
        return None

    # @property
    # def properties(self, name:str = None):
    #     node = self.find_node(name=name)
    #     if node is not None:
    #         return node.properties 
    #     else: return None

    @property
    def properties_qt_model(self) -> QStandardItemModel:
        """动态生成表格模型，并支持双击修改后自动写回当前节点字典"""
        model = QStandardItemModel()
        model.setHorizontalHeaderLabels(["属性 (Property)", "值 (Value)"])

        for prop_name, prop_val in self.properties.items():
            item_name = QStandardItem(str(prop_name))
            item_val = QStandardItem(str(prop_val))

            # 属性名设为只读，属性值保持可编辑
            item_name.setFlags(item_name.flags() & ~Qt.ItemIsEditable)
            model.appendRow([item_name, item_val])

        # 核心：监听表格修改信号，实现自动反向写回内存
        def sync_back_to_node(item):
            if item.column() == 1:  # 仅在“值”列被修改时触发
                row = item.row()
                prop_name_item = model.item(row, 0)
                if prop_name_item:
                    p_name = prop_name_item.text()
                    self._properties[p_name] = item.text()  # 写回字典

        model.itemChanged.connect(sync_back_to_node)
        return model

    def __repr__(self):
        return f"<DTNode: {self.path}>"

    # customer function

    def traverse(self):
        # print(f"路径: {self.path.ljust(150)} | 名字(Name): {self.name.ljust(30)} | 标签(Label): {str(self.label).ljust(20)} | 属性数: {len(self.properties)}")
        yield self
        for child in self.children.values():
            yield from child.traverse()

    @property
    def qt_model(self):
        model = QStandardItemModel()
        model.setHorizontalHeaderLabels(["名称（Name）", "别名（Label）", "属性数量（Property Qty）"])
        # for column in range(model.columnCount()):
        #     model.setHeaderData(column, Qt.Orientation.Horizontal, Qt.AlignmentFlag.AlignCenter, Qt.ItemDataRole.TextAlignmentRole)

        def add_node_to_item(qt_parent, dt_node):
            # 如果是根节点，显示为 "/" 增加辨识度
            display_name = "/" if dt_node.name == "/" else dt_node.name
            
            item_name = QStandardItem(display_name)
            item_label = QStandardItem(str(dt_node.label) if dt_node.label else "")
            item_props_count = QStandardItem(str(len(dt_node.properties)))
            
            # 🚀【核心修改点】：统一使用标准的 UserRole 存储物理节点对象
            item_name.setData(dt_node, role=Qt.ItemDataRole.UserRole)
            
            row = [item_name, item_label, item_props_count]
            qt_parent.appendRow(row)
            
            for child_node in dt_node.children.values():
                add_node_to_item(item_name, child_node)

        # 直接从自身（根节点）开始往下递归渲染
        add_node_to_item(model, self)
        return model

    @classmethod
    def from_dts_text(cls, dts_content: str) -> "OpenDeviceTreeNode":
        root = OpenDeviceTreePortor.text_import(cls,dts_content)
        return root

    @property
    def to_dts_file(self) -> str:
        content = OpenDeviceTreePortor.text_export(self)
        return content
