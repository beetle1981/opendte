import os, re

class OpenDeviceTreeNode:
    def __init__(self, name, label=None):
        self.name = name
        self.label = label
        self.properties = {}

        self.children = []
        self.parent = None


    def add_child(self, child_node):
        child_node.parent = self
        self.children.append(child_node)

    def __repr__(self):
        return f"<Node: {self.label or ''} : {self.name}>"