import re
from lib.odtlib import OpenDeviceTree
from lib.dnode import OpenDeviceTreeNode

class OpenDeviceTreeManager(OpenDeviceTree):
    def __init__(self, filepath=None):
        super().__init__(filepath)
        

    @property
    def new_tree(self):
        """对主树进行树合并或分离导出的结构树"""
        if self.dts_includes is not None:
            if self.main_tree_has_phandle:
                print(f"DEBUG: main tree has includes and phandle.")
                # return self.trees_devide()
                return self.main_tree
            else:
                print(f"DEBUG: main tree has includes and has NO phandle.")
                return self.trees_merge()
        else:
            print(f"DEBUG: main tree has NO includes.")
            return self.main_tree

    def trees_devide(self) -> 'OpenDeviceTreeNode':
        # --------------------------------------------------------------------
        # step1: main_tree 从 include 里恢复节点标签，Debug 输出
        # --------------------------------------------------------------------
        print("\n🚀 DEBUG: [Step 1] 开始从 include 树列表中恢复 main_tree 的标签映射...")
        main_tree = self.main_tree
        self.recover_labels_recursive(main_tree)
        print("✔ DEBUG: [Step 1] 节点标签映射恢复完毕。")

        return main_tree

    def find_node_by_path_in_includes(self, path: str) -> 'OpenDeviceTreeNode | None':
        for o_tree in self.other_trees:
            node = o_tree.find_node_by_path(o_tree, path)
            if node: return node
        return None

    def recover_labels_recursive(self, node: OpenDeviceTreeNode) -> 'OpenDeviceTreeNode':
        if not node: return
        node_path = getattr(node, 'path', '') 
        print("A")       
        inc_node = self.find_node_by_path_in_includes(node_path)
        if inc_node and getattr(inc_node, 'label', None):
            node.label = inc_node.label
            print(f"       [Label恢复] 路径: {node_path} -> 从 include 树成功同步标签: '{node.label}'")
        else:
            if getattr(node, 'label', None):
                print(f"       [Label保留] 路径: {node_path} -> 保持主树自有标签: '{node.label}'")
        
        for child in getattr(node, 'children', {}).values():
            self.recover_labels_recursive(child)




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


