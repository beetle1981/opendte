import os
import re, unicodedata
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
        self.dnode = OpenDeviceTreeNode("mynode")
        with open(file_path, "r", encoding="utf-8") as f:
            self.content = f.read()
            
        # self.content = re.sub("#include","/include/", self.content, flags=re.M)
        self.content = unicodedata.normalize("NFKC", self.content)
        self.content = re.sub(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f-\x9f]", "", self.content)
        self.content = re.sub(r"[\u200b-\u200d\ufeff\u200e\u200f\u202a-\u202e]", "", self.content)
        self.content = self.content.replace("\r\n", "\n").replace("\r", "\n")
        self.content = "\n".join([line.rstrip() for line in self.content.splitlines()])

    def find_includes(self):
        include_pattern = re.compile(r'(?:#include|/include/)\s+["<](?P<filepath>[^">]+)["<]')

        includes = re.findall(include_pattern, self.content)
        for i in includes:
            print(i)

    

if __name__ == "__main__":
    # file_path = Path.cwd() / "../devicetree/rk3399-eaidk-610.dts"
    file_path = Path.cwd() / "devicetree/test.dts"
    print(file_path)
    dt = OpenDeviceTree(file_path)
    dt.find_includes()

    # 调试：打印前 10 行并带上行号，看看第 3 行到底是什么
    for i, line in enumerate(dt.content.splitlines()[:15], 1):
        print(f"Line {i}: {repr(line)}")

    dt1 = dtlib.DT(dt.content)

    root_node = dt.root
    print("Root Node:", root_node)




