import os
import re
from pathlib import Path
from pydevicetree import Devicetree
from lib.dnode import OpenDeviceTreeNode

class OpenDeviceTree:
    def __init__(self, file_path):
        self.file_path = file_path
        self.name = Path(file_path).name #filename.dts
        self.stem = Path(file_path).stem #filename
        self.include = []
        self.alias = {}
        self.dnode = OpenDeviceTreeNode()




    def merge_dts_includes(file_path, include_dirs=None):
        """纯 Python 实现：递归读取并展开 /include/ "xxxx.dtsi" 行"""
        include_dirs = include_dirs or ["."]
        main_dir = os.path.dirname(os.path.abspath(file_path))
        if main_dir not in include_dirs:
            include_dirs.insert(0, main_dir)

        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()

        # 匹配 /include/ "filename.dtsi"
        include_pattern = r'/include/\s*"([^"]+)"'

        def replace_match(match):
            inc_filename = match.group(1)
            # 在所有 include 路径中寻找该文件
            for d in include_dirs:
                full_path = os.path.join(d, inc_filename)
                if os.path.exists(full_path):
                    # 递归展开子文件
                    return merge_dts_includes(full_path, include_dirs)
            raise FileNotFoundError(f"无法在路径列表中找到 include 文件: {inc_filename}")

        # 循环替换，直到没有任何 /include/ 关键字
        while re.search(include_pattern, content):
            content = re.sub(include_pattern, replace_match, content)

        # 顺便洗掉阻碍解析的 # 开头的宏指令
        content = re.sub(r"^\s*#.*$", "", content, flags=re.MULTILINE)
        return content


    # ================= 使用方法 =================
    # 1. 展开所有 include 并获取干净的完整 DTS 文本
    full_dts_text = merge_dts_includes("main_board.dts", include_dirs=["."])

    # 2. 直接用 pydevicetree 解析，无需依赖 libfdt 和 dtc 工具！
    tree = Devicetree.parseString(full_dts_text)
