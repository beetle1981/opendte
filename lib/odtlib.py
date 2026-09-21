import os
import re, tempfile
from devicetree import dtlib
from pathlib import Path
from lib.dmanager import OpenDeviceTreeManager

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
    def main_tree(self):
        """
        dts文件构建的节点树
        """
        node = OpenDeviceTreeManager().from_dts_text(self.content)
        return node
        
    def set_include_dirs(self, include_paths = None):
        pass

    @property
    def other_trees(self):
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
                if file:
                    try:
                        with open(file, "r", encoding="utf-8") as dtsi:
                            node = OpenDeviceTreeManager.from_dts_text(dtsi.read())
                        nodes.append(node)
                    except Exception as e:
                        print(f"File not found: {e}")

            return nodes
        else:
            return None
    @property
    def root_tree(self):
        root = OpenDeviceTreeManager.trees_merge(self.main_tree, self.other_trees) if self.other_trees != None else self.main_tree
        return root

    @property
    def sub_tree(self):
        clean_tree = OpenDeviceTreeManager.clean_phandle(self.main_tree)
        return OpenDeviceTreeManager.trees_devide(clean_tree, self.other_trees) if self.other_trees != None else self.main_tree