import os
import re
from dnode import OpenDeviceTreeNode
from pathlib import Path

# ==================== 1. 重构后的 OpenDeviceTreeNode 类 ====================
# class OpenDeviceTreeNode:
#     def __init__(self, name, label=None, parent=None):
#         self.name = name
#         self.label = label
#         self.properties = {}
        
#         # 💡 统一修改为字典，以支持你原定义中的 self.children[child_name] 赋值与索引
#         self.children = {}
#         self.parent = parent

#     @property
#     def path(self) -> str:
#         """递归获取节点的绝对路径"""
#         if self.parent is None or self.parent.name == "/":
#             return f"/{self.name}" if self.name != "/" else "/"
#         return f"{self.parent.path}/{self.name}"

#     def add_child(self, child_name: str, label=None):
#         """创建并添加一个子节点"""
#         # 实例化时将自身 (self) 作为 parent 传入
#         child_node = OpenDeviceTreeNode(child_name, label=label, parent=self)
#         self.children[child_name] = child_node
#         return child_node

#     def __repr__(self):
#         return f"<OpenDeviceTreeNode: {self.path}>"


# ==================== 2. 洗衣流水线（清洗宏、剥离块） ====================
def clean_and_split_dts(filepath, include_paths=None):
    if include_paths is None:
        include_paths = [os.path.dirname(filepath)]
    else:
        include_paths = [os.path.dirname(filepath)] + include_paths

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

    clean_text = load_and_preprocess(filepath)
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
def parse_properties_to_dict(block_text):
    props = {}
    pattern = re.compile(r'([a-zA-Z0-9_\-#\+]+)\s*=\s*([^;]+);')
    for match in pattern.finditer(block_text):
        props[match.group(1).strip()] = match.group(2).strip()
    return props

def parse_name_and_label(raw_name):
    """
    解析设备树签名中的 label。
    例如把 "uart0: serial@10000000" 拆分为 label="uart0", name="serial@10000000"
    """
    if ":" in raw_name:
        label, name = raw_name.split(":", 1)
        return name.strip(), label.strip()
    return raw_name.strip(), None


def build_open_device_tree(origin_dts_path, include_dirs=None):
    """
    主入口：读取原始DTS文件，生成并初始化 OpenDeviceTreeNode 对象树
    """
    flat_dts_dict = clean_and_split_dts(origin_dts_path, include_dirs)
    
    # 初始化根节点
    root = OpenDeviceTreeNode(name="/")
    if "/" in flat_dts_dict:
        root.properties = parse_properties_to_dict(flat_dts_dict["/"])

    # 构建子节点分支
    for path_key, block_text in flat_dts_dict.items():
        if path_key == "/":
            continue
        parts = [p.strip() for p in path_key.split("->")[1:] if p.strip()]
        
        current_node = root
        for part in parts:
            # 💡 解析出节点自身真正的 name 和 label，存入你的新 class 中
            node_name, node_label = parse_name_and_label(part)
            
            # 使用真实具有唯一性的 node_name 作为 children 字典的 Key
            if node_name not in current_node.children:
                # 触发你定义的 add_child 方法
                current_node.add_child(node_name, label=node_label)
                
            current_node = current_node.children[node_name]
            
        current_node.properties = parse_properties_to_dict(block_text)

    return root


# ==================== 4. 自动化测试 ====================
if __name__ == "__main__":
    # dts_file_path = r"Z:\opendte\devicetree\rk3399-eaidk-610.dts"
    dts_file_path = Path.cwd() / "../devicetree/rk3399-eaidk-610.dts"
    include_folders = [r"Z:\opendte\devicetree"] 

    try:
        # 一键生成全新的 OpenDeviceTreeNode 递归树
        tree_root = build_open_device_tree(dts_file_path, include_dirs=include_folders)
        
        print("🎉 OpenDeviceTreeNode 树结构初始化成功！")
        
        # 递归遍历测试，观察 name 和 label 是否成功分离
        def traverse(node):
            print(f"路径: {node.path.ljust(150)} | 名字(Name): {node.name.ljust(30)} | 标签(Label): {str(node.label).ljust(20)} | 属性数: {len(node.properties)}")
            for child in node.children.values():
                traverse(child)
                
        traverse(tree_root)

    except Exception as e:
        print(f"❌ 运行失败: {e}")
