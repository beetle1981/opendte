import re
from lib.odtlib import OpenDeviceTree
from lib.dnode import OpenDeviceTreeNode

class OpenDeviceTreeManager(OpenDeviceTree):
    def __init__(self, filepath=None):
        super().__init__(filepath)
        

    @property
    def new_tree(self):
        """对主树进行树合并或分离导出的结构树"""
        if self.dts_includes:
            if self.main_tree_has_phandle:
                print(f"DEBUG: main tree has includes and phandle.")
                self.main_tree = self.trees_devide()
                return self.main_tree
            else:
                print(f"DEBUG: main tree has includes and has NO phandle.")
                return self.trees_merge()
        else:
            print(f"DEBUG: main tree has NO includes.")
            return self.main_tree

    def trees_merge(self) -> OpenDeviceTreeNode:
        """
        核心树合并算法：在物理内存中直接将主树和多个独立子树深度合并为一棵全新的 root_node 大树。
        💡 策略：
        1. 收集 main_tree 和 other_trees 中所有物理节点的 label 映射关系。
        2. 将所有树中的正常物理节点按照 绝对路径 深度合并到 final_root（相同路径节点自动合并，属性覆盖）。
        3. 处理所有以 & 开头的引用节点，利用全局标签注册表重定向合并到真实的物理节点中。如果找不到对应物理节点就保留，不跳过。
        """
        # 创建一个绝对干净的终极总根节点
        final_root = OpenDeviceTreeNode("/")

        # 1. 全局标签注册表：用于将 label 映射到 final_root 中的真实合并后节点路径
        label_to_path_registry = {}

        def collect_labels(source_node):
            """第一步辅助：收集所有正常物理节点的物理路径与 label 的对应关系"""
            if not source_node or source_node.name.startswith("&"):
                return
            if source_node.label:
                label_to_path_registry[source_node.label] = source_node.path
            for child in source_node.children.values():
                collect_labels(child)

        # 2. 根据路径在 final_root 中寻找或创建节点（用于将分散在各处的同名路径合并）
        def get_or_create_node_by_path(absolute_path: str):
            if absolute_path == "/":
                return final_root
            parts = [p for p in absolute_path.split("/") if p]
            curr = final_root
            for part in parts:
                if part in curr.children:
                    curr = curr.children[part]
                else:
                    curr = curr.add_child(part)
            return curr

        def merge_properties_and_label(source_node, target_node):
            """将源节点的属性和 label 覆盖合并到目标节点（加入黑名单过滤器）。"""
            if source_node.label:
                target_node.label = source_node.label
                
            # 🚀 【核心修复 1】：定义黑名单，严防垃圾属性混入
            property_blacklist = { "/", "dts-v1", "plugin" }
            for prop_name, prop_val in source_node.properties.items():
                clean_name = prop_name.strip()
                # 剔除带有斜杠、包含关键字或在黑名单内的属性名
                if clean_name in property_blacklist or "/" in clean_name:
                    continue
                target_node.properties[clean_name] = prop_val

        # 3. 深度遍历合并物理节点（排除引用的占位节点）
        def merge_physical_nodes(source_node):
            if not source_node or source_node.name.startswith("&"):
                return
                
            # 获取或创建目标树中的对应物理节点，并合并属性与标签
            target_node = get_or_create_node_by_path(source_node.path)
            merge_properties_and_label(source_node, target_node)
            
            # 递归合并物理子节点
            for child in source_node.children.values():
                merge_physical_nodes(child)

        # 4. 深度遍历合并引用节点（以 & 开头的节点）
        def merge_reference_nodes(source_node, current_target_parent=None):
            if not source_node:
                return
                
            if source_node.name.startswith("&"):
                ref_label = source_node.name[1:]  # 提取去掉 & 后的 label 名称
                
                # 从全局标签注册表中查找真实物理节点的绝对路径
                real_path = label_to_path_registry.get(ref_label)
                
                if real_path:
                    # 情况 A：找到了对应的真实物理节点，合并到该物理节点
                    target_node = get_or_create_node_by_path(real_path)
                    merge_properties_and_label(source_node, target_node)
                else:
                    # 情况 B：找不到标签对应的物理节点，原地保留，作为普通节点挂载到当前的父节点下
                    parent_node = current_target_parent if current_target_parent else final_root
                    
                    if source_node.name in parent_node.children:
                        target_node = parent_node.children[source_node.name]
                    else:
                        target_node = parent_node.add_child(source_node.name)
                        
                    merge_properties_and_label(source_node, target_node)

                # 递归处理引用节点底下的子节点，以当前 target_node 作为父节点上下文
                for child in source_node.children.values():
                    merge_reference_nodes(child, current_target_parent=target_node)
            else:
                # 如果是正常物理节点，追踪其在 final_root 中的对应映射，为深层的引用节点提供挂载父级
                corresponding_target = get_or_create_node_by_path(source_node.path)
                for child in source_node.children.values():
                    merge_reference_nodes(child, current_target_parent=corresponding_target)

        # === 执行合并流水线 ===
        
        # 步骤一：收集主树和所有独立子树的标签映射关系
        collect_labels(self.main_tree)
        for tree in self.other_trees:
            collect_labels(tree)
            
        # 步骤二：合并主树和所有子树的物理节点到 final_root
        merge_physical_nodes(self.main_tree)
        for tree in self.other_trees:
            merge_physical_nodes(tree)
            
        # 步骤三：解析并重定向合并所有树中的引用节点（找不到则原地作为普通节点保留）
        merge_reference_nodes(self.main_tree)
        for tree in self.other_trees:
            merge_reference_nodes(tree)

        return final_root

    def trees_devide(self) -> 'OpenDeviceTreeNode':
        """
        对主树进行结构树分离导出，清理引用并转化为标准编译器语法格式
        """
        print("\n" + "="*60)
        print("DEBUG: [trees_devide] 启动设备树高级差分与分离算法")
        print("="*60)

        # 🚀 统一局部变量引用，确保整个生命周期内数据源对齐
        main_tree = self.main_tree
        other_trees = self.other_trees if self.other_trees is not None else []

        # --------------------------------------------------------------------
        # 内部路径检索辅助函数：在 include 树列表中寻找相同路径的节点
        # --------------------------------------------------------------------
        def find_node_by_path_in_includes(path: str) -> 'OpenDeviceTreeNode | None':
            for o_tree in other_trees:
                node = find_node_recursive(o_tree, path)
                if node: return node
            return None

        def find_node_recursive(current_node, target_path):
            if not current_node: return None
            if getattr(current_node, 'path', '') == target_path:
                return current_node
            # 🚀 核心适配：使用 .values() 遍历字典里的子节点实体，防止遍历出键名字符串
            for child in getattr(current_node, 'children', {}).values():
                found = find_node_recursive(child, target_path)
                if found: return found
            return None

        # --------------------------------------------------------------------
        # step1: main_tree 从 include 里恢复节点标签，Debug 输出
        # --------------------------------------------------------------------
        print("\n🚀 DEBUG: [Step 1] 开始从 include 树列表中恢复 main_tree 的标签映射...")
        def recover_labels_recursive(node):
            if not node: return
            node_path = getattr(node, 'path', '')
            
            inc_node = find_node_by_path_in_includes(node_path)
            if inc_node and getattr(inc_node, 'label', None):
                node.label = inc_node.label
                print(f"       [Label恢复] 路径: {node_path} -> 从 include 树成功同步标签: '{node.label}'")
            else:
                if getattr(node, 'label', None):
                    print(f"       [Label保留] 路径: {node_path} -> 保持主树自有标签: '{node.label}'")
            
            for child in getattr(node, 'children', {}).values():
                recover_labels_recursive(child)

        recover_labels_recursive(main_tree)
        print("✔ DEBUG: [Step 1] 节点标签映射恢复完毕。")

        # --------------------------------------------------------------------
        # step2: main_tree 从 properties 中 phandle 或 linux phandle 提取值写入 phandle 属性，
        #        然后从 properties 删除 phandle。添加 DEBUG 输出
        # --------------------------------------------------------------------
        print("\n🚀 DEBUG: [Step 2] 开始抽取属性中的 phandle/linux,phandle 至节点实体内部...")
        def process_phandles_recursive(node):
            if not node: return
            properties = getattr(node, 'properties', {})
            
            target_key = None
            if 'phandle' in properties:
                target_key = 'phandle'
            elif 'linux,phandle' in properties:
                target_key = 'linux,phandle'
                
            if target_key:
                raw_value = properties[target_key]
                print(f"       [Phandle抓取] 节点: {getattr(node, 'path', '')} | 发现内嵌属性 '{target_key}': {raw_value}")
                
                # 解包潜在的列表或单值转化为标准整型数据
                phandle_val = raw_value[0] if isinstance(raw_value, list) else raw_value
                node.phandle = phandle_val
                
                # 从字典中剔除
                del properties[target_key]
                print(f"       [Phandle改写] 成功擦除 properties['{target_key}']，并挂载至实体 node.phandle = {phandle_val}")
            
            for child in getattr(node, 'children', {}).values():
                process_phandles_recursive(child)

        process_phandles_recursive(main_tree)
        print("✔ DEBUG: [Step 2] Phandle 实体属性提取与字典清洗完毕。")

        # --------------------------------------------------------------------
        # step3：找出有 phandle 值引用的属性，将对应引用值换成对应节点的标签的引用，添加 DEBUG 输出
        # --------------------------------------------------------------------
        print("\n🚀 DEBUG: [Step 3] 开始进行全局 phandle 引用向 Label 标签引用的全量值转换...")
        
        phandle_to_label_map = {}
        def build_phandle_map(node):
            if not node: return
            p_val = getattr(node, 'phandle', None)
            l_val = getattr(node, 'label', None)
            if p_val and l_val:
                phandle_to_label_map[p_val] = l_val
            for child in getattr(node, 'children', {}).values():
                build_phandle_map(child)
                
        build_phandle_map(main_tree)
        for o_tree in other_trees:
            build_phandle_map(o_tree)

        def replace_references_recursive(node):
            if not node: return
            properties = getattr(node, 'properties', {})
            
            for prop_name, prop_val in list(properties.items()):
                check_val = prop_val[0] if isinstance(prop_val, list) and len(prop_val) > 0 else prop_val
                
                if check_val in phandle_to_label_map:
                    target_label = phandle_to_label_map[check_val]
                    properties[prop_name] = f"&{target_label}"
                    print(f"       [引用替换] 节点: {getattr(node, 'name', '')} | 属性 '{prop_name}': {prop_val} -> 成功映射为标签引用: &{target_label}")
            
            for child in getattr(node, 'children', {}).values():
                replace_references_recursive(child)

        replace_references_recursive(main_tree)
        print("✔ DEBUG: [Step 3] 全局符号替换与标签解包映射完毕。")

        # --------------------------------------------------------------------
        # step4: main_tree 去除所有 include 含有的同名节点，相同值的属性，
        #        最后将节点名改成 &label 引用节点。添加 debug 输出
        # --------------------------------------------------------------------
        print("\n🚀 DEBUG: [Step 4] 开始实施 include 树共有资产的差分裁剪与 &label 语法改造...")
        def optimize_and_relabel_recursive(node):
            if not node: return
            node_path = getattr(node, 'path', '')
            properties = getattr(node, 'properties', {})
            
            inc_node = find_node_by_path_in_includes(node_path)
            if inc_node:
                inc_props = getattr(inc_node, 'properties', {})
                print(f"       [差分对比] 命中 include 同路径节点: {node_path}，启动属性裁剪...")
                
                for p_key in list(properties.keys()):
                    if p_key in inc_props and properties[p_key] == inc_props[p_key]:
                        del properties[p_key]
                        print(f"              [属性剥离] 移除与 include 完全相同的冗余属性: '{p_key}'")

            if getattr(node, 'label', None):
                old_name = node.name
                node.name = f"&{node.label}"
                print(f"       [语法缩编] 节点路径: {node_path} | 名称 '{old_name}' -> 成功转换为引用格式: '{node.name}'")
            else:
                print(f"       [Step 4 清洗警告] 节点 '{getattr(node, 'name', '')}' 无可用 Label，保留原名")

            for child in getattr(node, 'children', {}).values():
                optimize_and_relabel_recursive(child)

        optimize_and_relabel_recursive(main_tree)
        print("✔ DEBUG: [Step 4] 冗余属性剥离与引用层级改写完毕。")

        # --------------------------------------------------------------------
        # step5：将所有的十六进制值换成十进制值， 添加 debug输出 (🚀 已完美补全截断)
        # --------------------------------------------------------------------
        print("\n🚀 DEBUG: [Step 5] 启动数据标准化：全局检索并将所有十六进制形式的数据转换为十进制...")
        def convert_hex_to_dec_recursive(node):
            if not node: return
            properties = getattr(node, 'properties', {})
            
            for prop_name, prop_val in properties.items():
                if isinstance(prop_val, str) and prop_val.lower().startswith('0x'):
                    try:
                        dec_val = int(prop_val, 16)
                        properties[prop_name] = dec_val
                        print(f"       [进制转换] 节点: {getattr(node, 'path', '')} | 属性 '{prop_name}': {prop_val} -> {dec_val}")
                    except ValueError:
                        pass
                elif isinstance(prop_val, list):
                    new_list = []
                    has_changed = False
                    for item in prop_val:
                        if isinstance(item, str) and item.lower().startswith('0x'):
                            try:
                                new_list.append(int(item, 16))
                                has_changed = True
                            except ValueError:
                                new_list.append(item)
                        else:
                            new_list.append(item)
                    if has_changed:
                        properties[prop_name] = new_list
                        print(f"       [列表进制转换] 节点: {getattr(node, 'path', '')} | 属性 '{prop_name}' 内部元素已转十进制")

            for child in getattr(node, 'children', {}).values():
                convert_hex_to_dec_recursive(child)

        convert_hex_to_dec_recursive(main_tree)
        print("✔ DEBUG: [Step 5] 十六进制格式标准化过滤完毕。")
        
        print("\n" + "="*60)
        print("DEBUG: [trees_devide] 设备树高级分离与反解流程顺利完成！")
        print("="*60 + "\n")
        
        return main_tree
