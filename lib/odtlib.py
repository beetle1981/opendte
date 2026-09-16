import os
import re, tempfile
from devicetree import dtlib
from pathlib import Path
from dnode import OpenDeviceTreeNode

class OpenDeviceTree:
    def __init__(self, file_path):
        self.file_path = file_path
        self.name = Path(file_path).name #filename.dts
        self.stem = Path(file_path).stem #filename
        self.include = []
        self.alias = {}
        self.main_node = OpenDeviceTreeNode("mynode")
        self.include_nodes = {}
        with open(file_path, "r", encoding="utf-8") as dts:
            self.content = dts.read()

    def find_includes(self):
        include_pattern = re.compile(r'(?:#include|/include/)\s+["<](?P<filepath>[^">]+)["<]')
        includes = re.findall(include_pattern, self.content)
        for i in includes:
            self.include.append(i)
            print(i)
        for i in self.include:
            try:
                with open(i, "r", encoding="utf-8") as dtsi:
                    self.content = self.content + "\n" + dtsi.read()
            except FileNotFoundError as e:
                 print(f"❌ 找不到包含的依赖文件: {e}")
        self.content = re.sub(r'^\s*#include\s+.*$','',self.content,flags=re.MULTILINE)
        self.content = "\n".join([line for line in self.content.splitlines() if line.strip()])

    

if __name__ == "__main__":
    dts_file_path = Path.cwd() / "../devicetree/rk3399-eaidk-610.dts"
    # dts_file_path = Path.cwd() / "../devicetree/rk3399.dtsi"
    # dts_file_path = Path.cwd() / "../devicetree/test.dts"
    # dts_file_path = Path.cwd() / "../devicetree/xl.dts"
    print(dts_file_path)
    dt = OpenDeviceTree(dts_file_path)
    dt.find_includes()

    # 调试：打印前 10 行并带上行号，看看第 3 行到底是什么
    for i, line in enumerate(dt.content.splitlines()[:15], 1):
        print(f"Line {i}: {repr(line)}")

    tmp_dir = Path.cwd() / "tmp"
    with tempfile.NamedTemporaryFile(mode='w+', suffix='.dts', delete=False, dir=tmp_dir, encoding='utf-8') as tmp:
        tmp.write(dt.content)
        tmp.flush() 
    
        dt1 = dtlib.DT(tmp.name)
    print(dt1.root)

    for node in dt1.node_iter():
        print(f"\nCurrent Node Path: {node.path}; Current Node Name: {node.name}")
        for index,value in node.props.items():
            print(f"\n{value}")




