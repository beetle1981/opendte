import os, re
from PySide6.QtGui import QStandardItemModel, QStandardItem
from PySide6.QtCore import Qt

class OpenDeviceTreeNode:
    def __init__(self, name=None, label=None, parent=None):
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

    @property
    def nodes(self):
        return list(self.traverse())

    def add_child(self, child_name: str, label=None):
        """创建并添加一个子节点"""
        child_node = OpenDeviceTreeNode(child_name, label=label, parent=self)
        self.children[child_name] = child_node
        return child_node

    def find_node(self, name: str = None, label: str = None):
        """全能查询函数：在整棵树中深度优先搜索（DFS）匹配 name 或 label 的节点。"""
        stack = [self]
        while stack:
            curr = stack.pop()
            if label is not None and curr.label == label:
                return curr
            
            clean_search_name = name.strip() if name else None
            if clean_search_name and "aliases" in clean_search_name.lower():
                clean_search_name = "aliases"
                
            if clean_search_name and curr.name == clean_search_name:
                return curr
            stack.extend(curr.children.values())
        return None

    def __repr__(self):
        return f"<DTNode: {self.path}>"

    # customer function

    def traverse(self):
        # print(f"路径: {self.path.ljust(150)} | 名字(Name): {self.name.ljust(30)} | 标签(Label): {str(self.label).ljust(20)} | 属性数: {len(self.properties)}")
        yield self
        for child in self.children.values():
            yield from child.traverse()

    @property
    def qt_model(self):
        """
        动态将当前节点及其子树转换为 QStandardItemModel 虚拟属性。
        直接支持：model = node.qt_model
        """
        # 1. 动态兼容导入 PySide6 或 PyQt6
        model = QStandardItemModel()
        model.setHorizontalHeaderLabels(["名字 (Name)", "标签 (Label)", "属性数"])

        def add_node_to_item(qt_parent, dt_node):
            item_name = QStandardItem(dt_node.name)
            item_label = QStandardItem(str(dt_node.label) if dt_node.label else "")
            item_props_count = QStandardItem(str(len(dt_node.properties)))
            
            # 将当前原生节点挂载到 Item 数据中，方便 UI 点击交互
            item_name.setData(dt_node, role=Qt.UserRole + 1)
            
            row = [item_name, item_label, item_props_count]
            qt_parent.appendRow(row)
            
            for child_node in dt_node.children.values():
                add_node_to_item(item_name, child_node)

        # 如果是根节点 '/'，为了不让 UI 多套一层无意义的根目录，直接展开它的子节点
        if self.name == "/" and self.children:
            for child in self.children.values():
                add_node_to_item(model, child)
        else:
            add_node_to_item(model, self)

        return model

    @classmethod
    def from_dts_text(cls, dts_content: str) -> "OpenDeviceTreeNode":
        """工厂方法：接收纯 DTS 文本字符串，清洗并构建设备树。"""
        cleaned_lines = []
        for line in dts_content.splitlines():
            line = re.sub(r'//.*', '', line)  
            stripped = line.strip()
            if not stripped or re.match(r'^(?:#include|/include/)\s+', stripped):
                continue
            cleaned_lines.append(line)
            
        dts_text = "\n".join(cleaned_lines)
        dts_text = re.sub(r'/\*.*?\*/', '', dts_text, flags=re.DOTALL)  

        root = cls("/")
        current_node = root
        node_stack = []  

        tokens = re.findall(r'\/|[a-zA-Z0-9_\-\+\#\.\,\/\@\&]+|[\{\}\;\=]', dts_text)
        
        idx = 0
        while idx < len(tokens):
            token = tokens[idx]
            if token == ';':
                idx += 1
                continue
                
            if token == '}':
                if node_stack:
                    current_node = node_stack.pop()
                else:
                    current_node = root  
                idx += 1
                if idx < len(tokens) and tokens[idx] == ';':
                    idx += 1
                continue

            lookahead_idx = idx
            node_label = None
            node_name = None
            is_label_ref = False
            is_node = False
            
            first_token = tokens[lookahead_idx]
            # 💡 【关键修复点】：这里保留原始 token 作为名字，不再截取 token[1:]
            if first_token.startswith('&'):
                is_label_ref = True
                node_name = first_token  # 🚀 直接完整保留 '&aliases' 或 '&soc'
                lookahead_idx += 1
            else:
                if lookahead_idx + 1 < len(tokens) and tokens[lookahead_idx + 1] == ':':
                    node_label = first_token
                    lookahead_idx += 2
                if lookahead_idx < len(tokens):
                    node_name = tokens[lookahead_idx]
                    lookahead_idx += 1

            while lookahead_idx < len(tokens):
                t = tokens[lookahead_idx]
                if t == '{':
                    is_node = True
                    break
                if t == '=' or t == ';':
                    break
                lookahead_idx += 1

            if is_node:
                node_stack.append(current_node)
                
                if node_name == '/':
                    current_node = root
                else:
                    if is_label_ref:
                        # 对于 &label 块，首先在全局尝试查找去除 & 符号后的原始 label
                        raw_label_name = node_name[1:]
                        existing_node = root.find_node(label=raw_label_name) or root.find_node(name=raw_label_name)
                        
                        # 💡 如果找到了对应的节点，就合并进去；
                        # 如果没有找到（或者它就是希望名字带 &），则以带 & 的全名作为新子节点追加
                        current_node = existing_node if existing_node else root.add_child(node_name)
                    else:
                        current_node = current_node.add_child(node_name, label=node_label)
                idx = lookahead_idx + 1
                continue
            else:
                prop_name = token
                lookahead_idx = idx + 1
                
                if lookahead_idx < len(tokens) and tokens[lookahead_idx] == '=':
                    idx = lookahead_idx + 1
                    prop_vals = []
                    while idx < len(tokens) and tokens[idx] != ';':
                        prop_vals.append(tokens[idx])
                        idx += 1
                    
                    val_str = " ".join(prop_vals)
                    current_node.properties[prop_name] = val_str
                            
                    if idx < len(tokens) and tokens[idx] == ';':
                        idx += 1
                else:
                    prop_name = token
                    current_node.properties[prop_name] = ""
                    idx = lookahead_idx
                    if idx < len(tokens) and tokens[idx] == ';':
                        idx += 1
                        
        return root
    @property
    def to_dts_file(self) -> str:
        """
        虚拟属性：将当前的节点树逆向生成为标准的、带有规范化缩进的 DTS 源码文本。
        """
        def serialize_node(node, level=0):
            indent = "    " * level
            lines = []
            
            # 1. 构造节点头部，如 "i2c0: i2c@40003000 {"
            if node.name == "/":
                lines.append(f"{indent}/ {{")
            else:
                header = ""
                if node.label:
                    header += f"{node.label}: "
                header += f"{node.name} {{"
                lines.append(f"{indent}{header}")
            
            # 2. 写入当前层级的所有属性 (格式化对齐)
            prop_indent = "    " * (level + 1)
            for k, v in node.properties.items():
                if v == "":
                    # 只有键没有值（空属性/布尔属性）
                    lines.append(f"{prop_indent}{k};")
                else:
                    lines.append(f"{prop_indent}{k} = {v};")
            
            # 3. 递归写入所有子节点，通过名称排序保持代码工整
            for child_name in sorted(node.children.keys()):
                child_lines = serialize_node(node.children[child_name], level + 1)
                lines.extend(child_lines)
                
            # 4. 节点闭合右大括号
            lines.append(f"{indent}}};")
            return lines

        # 从当前节点作为局部/全局起点开始序列化并用换行符拼接
        return "\n".join(serialize_node(self))

    @classmethod
    def merge_trees(cls, main_tree: "OpenDeviceTreeNode", other_trees: list["OpenDeviceTreeNode"]) -> "OpenDeviceTreeNode":
        """
        核心树合并算法：在物理内存中直接将主树和多个独立子树深度合并为一棵全新的 root_node 大树。
        💡 策略：
          1. 先把 other_trees（include 文件产生的独立树）深度合并进入新根（构建底层骨架）。
          2. 最后把 main_tree（主文件产生的树）深度合并进去（同名节点追加，同名属性覆盖 Overwrite）。
        """
        # 创建一个绝对干净的终极总根节点
        final_root = cls("/")

        def merge_node_to_target(source_node, target_node):
            """
            将 source_node（源节点）的所有属性和子节点，深度增量合并到 target_node（目标节点）中。
            """
            if not source_node:
                return

            # 1. 💡 同名属性直接发生 Overwrite 覆盖 / 不同名属性天然追加 (Dict 特性)
            for prop_name, prop_val in source_node.properties.items():
                target_node.properties[prop_name] = prop_val

            # 2. 💡 深度合并子节点
            for src_child_name, src_child_node in source_node.children.items():
                
                # 处理带有 & 符号的引用节点（如将 &aliases 块重定向到真实的 aliases 节点上）
                is_ref = src_child_name.startswith("&")
                
                if is_ref:
                    # 尝试在全局查找去掉 & 符号后的物理节点，或者带 & 符号的节点进行会师
                    raw_name = src_child_name[1:]
                    existing_dest = final_root.find_node(label=raw_name) or final_root.find_node(name=raw_name)
                    
                    if existing_dest:
                        # 找到了已有物理节点，直接将引用内部的属性/子树合并进去
                        merge_node_to_target(src_child_node, existing_dest)
                        continue
                        
                # 标准节点或未撞上物理节点的引用块，触发 add_child 增量去重机制
                # 如果 target_node 下已有 src_child_name 节点，返回已有对象；否则新建并追加（List 附加元素特征）
                tgt_child_node = target_node.add_child(src_child_name, label=src_child_node.label)
                
                # 递归向下执行子树级增量深拷贝合并
                merge_node_to_target(src_child_node, tgt_child_node)

        # 🚀 步骤 1: 优先遍历并合并所有 include 文件长出的独立骨架树
        for sub_tree in other_trees:
            # include 独立树通常顶级 children 就是各自的根节点子集（例如包含 root.children['aliases']）
            # 我们将这些独立子树的直接子孙，合并到终极 final_root 对应层级下
            if sub_tree.name == "/":
                merge_node_to_target(sub_tree, final_root)
            else:
                tgt_node = final_root.add_child(sub_tree.name, label=sub_tree.label)
                merge_node_to_target(sub_tree, tgt_node)

        # 🚀 步骤 2: 最后将主树 main_tree 深度灌入终极根节点
        # 由于它是最后注入，主树里定义的同名属性将会把刚才 include 里带来的默认旧属性完全覆盖掉
        if main_tree.name == "/":
            merge_node_to_target(main_tree, final_root)
        else:
            tgt_node = final_root.add_child(main_tree.name, label=main_tree.label)
            merge_node_to_target(main_tree, tgt_node)

        return final_root
