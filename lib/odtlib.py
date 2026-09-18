import os
import re, tempfile
from devicetree import dtlib
from pathlib import Path
from lib.dnode import OpenDeviceTreeNode

class OpenDeviceTree:
    def __init__(self, filepath=None):
        self.file_path = filepath
        self.include_dirs = None
        self.name = Path(self.file_path).name #filename.dts
        self.stem = Path(self.file_path).stem #filename
        self.alias = {}
        with open(self.file_path, "r", encoding="utf-8") as dts:
            self.content = dts.read()
    
    @property
    def main_node(self):
        """
        dts文件构建的节点树
        """
        node = OpenDeviceTreeNode().from_dts_text(self.content)
        return node
        
    def set_include_dirs(self, include_paths = None):
        return

    @property
    def other_nodes(self):
        """
        include文件构建的节点树
        """
        include_pattern = re.compile(r'(?:#include|/include/)\s+["<](?P<filepath>[^">]+)["<]')
        includes = re.findall(include_pattern, self.content)
        base_dir = os.path.dirname(os.path.abspath(self.file_path))
        paths = [base_dir] + (self.include_dirs if self.include_dirs else [])
        nodes = []
        print(f"Base Dir: {base_dir};")
        def find_file(filename):
            for p in paths:
                full_path = os.path.join(p, filename)
                if os.path.exists(full_path):
                    return full_path
            return None
        if includes:
            for i in includes:
                print(i)
                file = find_file(i)
                with open(file, "r", encoding="utf-8") as dtsi:
                    node = OpenDeviceTreeNode.from_dts_text(dtsi.read())
                nodes.append(node)

            return nodes
        else:
            return None
    @property
    def root_node(self):
        root = OpenDeviceTreeNode.merge_trees(self.main_node, self.other_nodes) if self.other_nodes == None else self.main_node
        return root

if __name__ == "__main__":
    dts_file_path = Path.cwd() / "devicetree/rk3399-eaidk-610.dts"
    # dts_file_path = Path.cwd() / "../devicetree/rk3399.dtsi"
    # dts_file_path = Path.cwd() / "../devicetree/test.dts"
    # dts_file_path = Path.cwd() / "../devicetree/xl.dts"
    include_folders = None 
    print(dts_file_path)
    dt = OpenDeviceTree(dts_file_path)
    try:
        # for node in dt.main_node.nodes:
        #     print(f"Name: {node.name}; Label: {node.label}; Property: {len(node.properties)} as follow: {node.properties}")
        # node = dt.main_node.find_node("aliases")
        # for key, val in node.properties.items():
        #     print(f"{key} = {val}")
        for node in dt.other_nodes:
            print(f"Name: {node.name}")
            # print(f"Name: {node.name}; Label: {node.label}; Property: {len(node.properties)} as follow: {node.properties}")
            node1 = node.find_node("aliases")
            if node1:
                for key, val in node1.properties.items():
                    print(f"{key} = {val}")
                
        aliases = dt.root_node.find_node("aliases")
        for key, val in aliases.properties.items():
            print(f"{key} = {val}")

    except Exception as e:
        print(f"❌ 运行失败: {e}")




