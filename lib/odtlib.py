import os
import re, tempfile
from devicetree import dtlib
from pathlib import Path
from lib.dmanager import OpenDeviceTreeManager
from PySide6.QtCore import QSettings
# from lib.header import HeaderAnalyzer

class OpenDeviceTree:
    def __init__(self, filepath=None):
        self.file_path = Path(filepath)
        self.base_dir = os.path.dirname(os.path.abspath(self.file_path))
        self.include_dirs = []  # 💡 规范初始化：默认设为空列表，防止 NoneType 迭代报错
        self.name = Path(self.file_path).name  # filename.dts
        self.stem = Path(self.file_path).stem  # filename
        self.defines = {}

        # self._include_pattern = re.compile(r'(?:#include|/include/)\s*["<]([^">]+)["<]')
        self._include_pattern = re.compile(r'(?:#include|/include/)\s*["<](.*?)[">]')

        self.settings = QSettings("RoyStudio", "OpenDTE")
        self.kernelpath = self.settings.value("kernelpath", "Z:\6.12__rockchip64__arm64")

        self._load_content()

    def _load_content(self):
        if not self.file_path.exists():
            raise FileNotFoundError(f"找不到 DTS 文件: {self.dts_path}")
        
        # 设备树文件通常为 utf-8 或 ascii 编码
        with open(self.file_path, 'r', encoding='utf-8', errors='ignore') as f:
            self.content = f.read()
    
    @property
    def main_tree(self):
        """dts 文件构建的节点主树"""
        # 💡 注意：确保 from_dts_text 是实例方法还是类方法，如果是类方法建议用类名调用
        node = OpenDeviceTreeManager().from_dts_text(self.content)
        return node
        
    def set_include_dirs(self, include_paths=None):
        """动态设置或追加外挂头文件的搜索路径目录列表"""
        if isinstance(include_paths, list):
            self.include_dirs = include_paths
        elif isinstance(include_paths, str):
            self.include_dirs = [include_paths]

    def _find_file(self, filename):
        """【封装内部方法】在所有搜索路径中定位文件的绝对路径"""
        base_dir = os.path.dirname(os.path.abspath(self.file_path))
        paths = [base_dir] + (self.include_dirs if self.include_dirs else [])
        for p in paths:
            full_path = os.path.join(p, filename)
            if os.path.exists(full_path):
                return os.path.normpath(full_path)
        return None

    @property
    def other_trees(self):
        """include 头文件/包含文件构建的独立子树列表"""
        # 正则同时匹配 #include "..." 和 /include/ "..."
        nodes = []

        for i in self.dts_includes:
            print(f"Found include reference: {i}")
            file = self._find_file(i)
            if file:
                try:
                    with open(file, "r", encoding="utf-8") as dtsi:
                        node = OpenDeviceTreeManager.from_dts_text(dtsi.read())
                    nodes.append(node)
                except Exception as e:
                    print(f"Read error or failed parsing for {file}: {e}")
            else:
                print(f"Warning: Include file '{i}' could not be found in any search paths.")

        # 🚀【核心修复】：如果匹配到了 include，但一个物理文件都没找到（nodes 为空），
        # 应当安全返回 None，防止下游 trees_merge 收到空列表引发空循环。
        return nodes if nodes else None

    @property
    def root_tree(self):
        """主树与所有合法外挂独立子树深度合并后的总根节点树"""
        # 🌟 由于 other_trees 内部做好了空列表防御，此处可以直接用 is not None 规避隐式 Bug
        if self.other_trees is not None:
            root = OpenDeviceTreeManager.trees_merge(self.main_tree, self.other_trees)
        else:
            root = self.main_tree
        return root

    @property
    def sub_tree(self):
        """对主树清理 phandle 引用后进行树分离导出的结构树"""
        clean_tree = OpenDeviceTreeManager.clean_phandle(self.main_tree)
        if self.other_trees is not None:
            return OpenDeviceTreeManager.trees_devide(clean_tree, self.other_trees)
        else:
            return self.main_tree

    def _extract_file_includes(self, file_abs_path):
        """辅助方法：读取单个物理文件并提取其内部的第一层 include"""
        try:
            with open(file_abs_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            raw_list = re.findall(self._include_pattern, content)
            return [inc.strip() for inc in raw_list if inc.strip()]
        except Exception as e:
            print(f"Warning: Failed to read {file_abs_path} for nested tracking: {e}")
            return []

    @property
    def all_raw_includes(self):
        """
        🚀【核心重构】：利用递归追踪，获取主文件及所有嵌套 dtsi 文件中的【全部】原始引用列表
        """
        all_found = []
        visited_files = set()  # 防止 dtsi 循环引用导致死循环

        def _track_recursive(current_file_path):
            if current_file_path in visited_files:
                return
            visited_files.add(current_file_path)

            # 1. 提取当前文件包含的直接引用
            direct_includes = self._extract_file_includes(current_file_path)
            
            for inc in direct_includes:
                if inc not in all_found:
                    all_found.append(inc)
                
                # 2. 如果引用的是设备树文件（非 .h），需要继续向下递归穿透
                if not inc.lower().endswith('.h'):
                    abs_child_file = self._find_file(inc)
                    if abs_child_file and os.path.exists(abs_child_file):
                        _track_recursive(abs_child_file)

        # 从主文件开始启动深度优先递归搜索
        _track_recursive(os.path.abspath(self.file_path))
        return all_found

    @property
    def dts_includes(self):
        """【新实现】提取并定位所有引用的设备树子文件（.dtsi / .dts）的绝对路径列表"""
        dtsi_paths = []
        for i in self.all_raw_includes:
        # 过滤出非 .h 的文件
            if not i.lower().endswith('.h'):
                abs_file = self._find_file(i)
                if abs_file:
                    dtsi_paths.append(abs_file)
        return dtsi_paths

    @property
    def dts_headers(self):
        """提取并定位【所有嵌套层级中】引用的 C 头文件（.h）的绝对路径列表"""
        header_paths = []
        for i in self.all_raw_includes:
            if i.lower().endswith('.h'):
                header_path = Path(self.kernelpath) / "include" / i
                # print(f"DEBUG: Hearder Path: {header_path}")
                header_paths.append(header_path)
        return header_paths

    @property
    def dts_defines(self) -> dict:
        """
        🚀【新实现】：遍历所有 dts_headers 文件，提取并生成所有 #define 的映射字典
        """
        defines_dict = {}
        
        # 1. 专门用于匹配 #define 键值对的正则表达式
        # 第一组 ([A-Za-z_][A-Za-z0-9_]*) 匹配合法的宏名称
        # 第二组 (.+) 匹配后面的值，并去除末尾的注释或空格
        define_pattern = re.compile(r'#define\s+([A-Za-z_][A-Za-z0-9_]*)\s+(.+)')

        # 2. 获取你上面已经拼好的绝对路径列表
        headers = self.dts_headers
        if not headers:
            return defines_dict

        # 3. 逐个打开头文件进行解析
        for h_path in headers:
            # 确保路径是 Path 对象并真实存在
            path_obj = Path(h_path)
            if not path_obj.exists():
                print(f"Warning: 头文件不存在，跳过解析: {path_obj}")
                continue

            try:
                with open(path_obj, 'r', encoding='utf-8', errors='ignore') as f:
                    for line in f:
                        line = line.strip()
                        
                        # 排除带参数的宏定义（如 #define MACRO(x) ...）
                        if '(' in line and line.find('(') < line.find(' '):
                            continue
                            
                        match = define_pattern.match(line)
                        if match:
                            macro_name = match.group(1).strip()
                            macro_value = match.group(2).strip()
                            
                            # 💡 清洗数据：切除值末尾可能夹杂的 C 语言注释 /* ... */ 或 // ...
                            macro_value = re.sub(r'/\*.*?\*/', '', macro_value)
                            macro_value = re.sub(r'//.*$', '', macro_value).strip()
                            
                            # 存入全局字典（如果多个文件存在同名宏，后者会自动覆盖前者，符合 C 语言覆盖特性）
                            defines_dict[macro_name] = macro_value
                            
            except Exception as e:
                print(f"Error reading header file {path_obj}: {e}")

        # 4. 更新类实例自身的 defines 变量并返回
        self.defines = defines_dict
        return defines_dict

