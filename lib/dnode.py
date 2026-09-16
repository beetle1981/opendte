import os, re

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

    def add_child(self, child_name: str, label=None):
        """创建并添加一个子节点"""
        child_node = OpenDeviceTreeNode(child_name, label=label, parent=self)
        self.children[child_name] = child_node
        return child_node

    def __repr__(self):
        return f"<DTNode: {self.path}>"