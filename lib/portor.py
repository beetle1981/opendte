import re

class OpenDeviceTreePortor:
    @staticmethod
    def text_import(node_cls, dts_content: str):
        """工厂方法：接收纯 DTS 文本字符串，清洗并精准构建设备树（彻底解决根节点丢失与路径切分 BUG）。"""
        cleaned_lines = []
        for line in dts_content.splitlines():
            line = re.sub(r'//.*', '', line)  
            stripped = line.strip()
            if not stripped or re.match(r'^(?:#include|/include/)\s+', stripped):
                continue
            cleaned_lines.append(line)
            
        dts_text = "\n".join(cleaned_lines)
        dts_text = re.sub(r'/\*.*?\*/', '', dts_text, flags=re.DOTALL)  

        # 🚀 始终维持全局唯一的干净根节点
        root = node_cls("/")
        current_node = root
        node_stack = []  

        # 🚀 【核心修复 1】：重新调优后的工业级分词正则
        # 将斜杠 / 独立出来，且在常规字符集 [^...] 中强行排除 / { } ; = :，确保根节点符号绝不被粘连吞噬
        tokens = re.findall(r'\/|[\{\}\;\=\:]|[a-zA-Z0-9_\-\+\#\.\,\@\&]+', dts_text)
        
        idx = 0
        while idx < len(tokens):
            token = tokens[idx]
            if token == ';' or token == ':':  
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

            # --- 精准前瞻上下文 ---
            lookahead_idx = idx
            node_label = None
            node_name = None
            is_label_ref = False
            is_node = False
            
            if lookahead_idx < len(tokens):
                first_token = tokens[lookahead_idx]
                
                if first_token.startswith('&'):
                    is_label_ref = True
                    node_name = first_token  
                    lookahead_idx += 1
                else:
                    if lookahead_idx + 1 < len(tokens) and tokens[lookahead_idx + 1] == ':':
                        node_label = first_token          
                        lookahead_idx += 2                
                        
                        if lookahead_idx < len(tokens):
                            node_name = tokens[lookahead_idx]  
                            lookahead_idx += 1
                    else:
                        node_name = first_token
                        lookahead_idx += 1

            # 边界熔断断言：向后检索大括号，撞上赋值或分号立即切断，证明是属性而非节点
            while lookahead_idx < len(tokens):
                t = tokens[lookahead_idx]
                if t == '{':
                    is_node = True
                    break
                if t == '=' or t == ';':
                    break
                lookahead_idx += 1

            # --- 状态执行分支 ---
            if is_node:
                node_stack.append(current_node)
                
                # 🚀 【核心修复 2】：当精准匹配到根节点 '/' 时，直接切回全局唯一的 root 实例上下文
                # 绝不让它作为普通的 add_child 子节点挂载，从而 100% 留住根节点的属性和直接子节点！
                if node_name == '/':
                    current_node = root
                    if node_label:
                        root.label = node_label
                else:
                    if is_label_ref:
                        raw_label_name = node_name[1:]
                        existing_node = root.find_node(label=raw_label_name) or root.find_node(name=raw_label_name)
                        
                        if existing_node:
                            current_node = existing_node
                            if node_label:
                                current_node.label = node_label
                        else:
                            current_node = root.add_child(node_name, label=node_label)
                    else:
                        current_node = current_node.add_child(node_name, label=node_label)
                        if node_label:
                            current_node.label = node_label
                            
                idx = lookahead_idx + 1
                continue
            else:
                # --- 属性解析分支 ---
                prop_name = token
                lookahead_idx = idx + 1
                
                if prop_name == ':':
                    idx += 1
                    continue

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

    def text_export(self):
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