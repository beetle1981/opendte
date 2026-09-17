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
        self.include = []
        self.alias = {}
        self.main_node = self.build_open_device_tree()
        self.include_nodes = {}
        with open(self.file_path, "r", encoding="utf-8") as dts:
            self.content = dts.read()
    

    def set_include_dirs(self, include_paths = None):
        return

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

    def clean_and_split_dts(self):
        if self.include_dirs is None:
            include_paths = [os.path.dirname(self.file_path)]
        else:
            include_paths = [os.path.dirname(self.file_path)] + self.include_dirs

        def find_file(filename):
            for path in include_paths:
                full_path = os.path.join(path, filename)
                if os.path.exists(full_path):
                    return full_path
            return None

        def load_and_preprocess(current_file):
            if not os.path.exists(current_file):
                return ""
            output_lines = []
            with open(current_file, 'r', encoding='utf-8') as f:
                for line in f:
                    stripped = line.strip()
                    if not stripped:
                        continue
                    include_match = re.match(r'^(?:#include|/include/)\s+"([^"]+)"', stripped)
                    if include_match:
                        inc_path = find_file(include_match.group(1))
                        if inc_path:
                            output_lines.append(load_and_preprocess(inc_path))
                        continue
                    if stripped.startswith("#"):
                        continue
                    output_lines.append(line)
            return "".join(output_lines)

        clean_text = load_and_preprocess(self.file_path)
        clean_text = re.sub(r'/dts-v1/;\s*', '', clean_text)

        flat_dict = {}
        def parse_level(text, current_head=""):
            lines = text.splitlines()
            current_node_lines = []
            i = 0
            while i < len(lines):
                line = lines[i]
                stripped = line.strip()
                if '{' in line and '=' not in stripped:
                    sub_head = line.split('{')[0].strip()
                    if not sub_head and current_node_lines:
                        sub_head = current_node_lines.pop().strip()
                    
                    brace_count = 0
                    sub_lines = []
                    while i < len(lines):
                        sub_lines.append(lines[i])
                        brace_count += lines[i].count('{')
                        brace_count -= lines[i].count('}')
                        if brace_count == 0:
                            break
                        i += 1
                    sub_full = "\n".join(sub_lines)
                    sub_inner = sub_full[sub_full.find('{')+1 : sub_full.rfind('}')]
                    full_sub_head = f"{current_head} -> {sub_head}" if current_head else sub_head
                    parse_level(sub_inner, full_sub_head)
                else:
                    current_node_lines.append(line)
                i += 1
            if current_head:
                flat_dict[current_head] = "\n".join([l for l in current_node_lines if l.strip()])

        parse_level(clean_text, "/")
        return flat_dict
    # ==================== 3. 属性与标签提取组装 ====================
    def parse_properties_to_dict(self, block_text):
        props = {}
        pattern = re.compile(r'([a-zA-Z0-9_\-#\+]+)\s*=\s*([^;]+);')
        for match in pattern.finditer(block_text):
            props[match.group(1).strip()] = match.group(2).strip()
        return props

    def parse_name_and_label(self, raw_name):
        """
        解析设备树签名中的 label。
        例如把 "uart0: serial@10000000" 拆分为 label="uart0", name="serial@10000000"
        """
        if ":" in raw_name:
            label, name = raw_name.split(":", 1)
            return name.strip(), label.strip()
        return raw_name.strip(), None


    def build_open_device_tree(self):
        """
        主入口：读取原始DTS文件，生成并初始化 OpenDeviceTreeNode 对象树
        """
        flat_dts_dict = self.clean_and_split_dts()
        
        # 初始化根节点
        root = OpenDeviceTreeNode(name="/")
        if "/" in flat_dts_dict:
            root.properties = self.parse_properties_to_dict(flat_dts_dict["/"])

        # 构建子节点分支
        for path_key, block_text in flat_dts_dict.items():
            if path_key == "/":
                continue
            parts = [p.strip() for p in path_key.split("->")[1:] if p.strip()]
            
            current_node = root
            for part in parts:
                # 💡 解析出节点自身真正的 name 和 label，存入你的新 class 中
                node_name, node_label = self.parse_name_and_label(part)
                
                # 使用真实具有唯一性的 node_name 作为 children 字典的 Key
                if node_name not in current_node.children:
                    # 触发你定义的 add_child 方法
                    current_node.add_child(node_name, label=node_label)
                    
                current_node = current_node.children[node_name]
                
            current_node.properties = self.parse_properties_to_dict(block_text)

        return root


if __name__ == "__main__":
    dts_file_path = Path.cwd() / "devicetree/rk3399-eaidk-610.dts"
    # dts_file_path = Path.cwd() / "../devicetree/rk3399.dtsi"
    # dts_file_path = Path.cwd() / "../devicetree/test.dts"
    # dts_file_path = Path.cwd() / "../devicetree/xl.dts"
    include_folders = None 
    print(dts_file_path)
    dt = OpenDeviceTree(dts_file_path)
    dt.find_includes()

    # 调试：打印前 10 行并带上行号，看看第 3 行到底是什么
    for i, line in enumerate(dt.content.splitlines()[:15], 1):
        print(f"Line {i}: {repr(line)}")

    # tmp_dir = Path.cwd() / "tmp"
    # with tempfile.NamedTemporaryFile(mode='w+', suffix='.dts', delete=False, dir=tmp_dir, encoding='utf-8') as tmp:
    #     tmp.write(dt.content)
    #     tmp.flush() 
    
    #     dt1 = dtlib.DT(tmp.name)
    # print(dt1.root)

    # for node in dt1.node_iter():
    #     print(f"\nCurrent Node Path: {node.path}; Current Node Name: {node.name}")
    #     for index,value in node.props.items():
    #         print(f"\n{value}")

    try:
        # 一键生成全新的 OpenDeviceTreeNode 递归树
        # tree_root = dt.main_node

        print("🎉 OpenDeviceTreeNode 树结构初始化成功！")
        # for node in dt.main_node.traverse():
        #     pass

        for node in dt.main_node.nodes:
            print(f"Name: {node.name} |Label: {node.label} |Path: {node.path} |Prop: {node.properties} |Child: {node.children}")
        
        # # 递归遍历测试，观察 name 和 label 是否成功分离
        # def traverse(node):
        #     print(f"路径: {node.path.ljust(150)} | 名字(Name): {node.name.ljust(30)} | 标签(Label): {str(node.label).ljust(20)} | 属性数: {len(node.properties)}")
        #     for child in node.children.values():
        #         traverse(child)
                
        # tree_root.traverse()

    except Exception as e:
        print(f"❌ 运行失败: {e}")




