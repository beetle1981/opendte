import re
from lib.dnode import OpenDeviceTreeNode

class OpenDeviceTreeManager(OpenDeviceTreeNode):
    @classmethod
    def trees_merge(cls, main_tree, other_trees: list):
        """
        核心树合并算法：在物理内存中直接将主树和多个独立子树深度合并为一棵全新的 root_node 大树。
        💡 策略：
        1. 收集 main_tree 和 other_trees 中所有物理节点的 label 映射关系。
        2. 将所有树中的正常物理节点按照 绝对路径 深度合并到 final_root（相同路径节点自动合并，属性覆盖）。
        3. 处理所有以 & 开头的引用节点，利用全局标签注册表重定向合并到真实的物理节点中。如果找不到对应物理节点就保留，不跳过。
        """
        # 创建一个绝对干净的终极总根节点
        final_root = cls("/")

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
        collect_labels(main_tree)
        for tree in other_trees:
            collect_labels(tree)
            
        # 步骤二：合并主树和所有子树的物理节点到 final_root
        merge_physical_nodes(main_tree)
        for tree in other_trees:
            merge_physical_nodes(tree)
            
        # 步骤三：解析并重定向合并所有树中的引用节点（找不到则原地作为普通节点保留）
        merge_reference_nodes(main_tree)
        for tree in other_trees:
            merge_reference_nodes(tree)

        return final_root

    @classmethod
    def trees_devide(cls, root_tree, other_trees: list):
        """
        核心树逆向拆分算法：将深度合并后的终极总大树（root_tree），
        根据各个 include 子树（other_trees）的初始物理骨架，拆分回各自独立的文件节点状态，
        并提取出原本属于主树（main_tree）的独有节点和覆盖属性。
        
        返回值：
          main_tree: 一个全新的、属于主文件的 OpenDeviceTreeNode 树
        """
        # 1. 创建全新的干净主树根节点
        main_tree = cls("/")
        
        # 2. 建立各 include 子树的物理路径和 Label 注册表字典
        # 格式: { "/soc/i2c@40003000": other_tree_obj, ... }
        path_to_include_tree_map = {}
        # 记录所有的 include 子树中曾经拥有过的 label 集合，以便主树提炼 &label 覆盖块
        include_labels_registry = {}

        def build_include_maps(source_node, belonging_tree):
            if not source_node or source_node.name.startswith('&'):
                return
            
            # 建立绝对路径到它所属的 include 树对象的映射
            path_to_include_tree_map[source_node.path] = belonging_tree
            if source_node.label:
                # 记录这个 label 原本属于哪一个绝对路径
                include_labels_registry[source_node.label] = source_node.path
                
            for child in source_node.children.values():
                build_include_maps(child, belonging_tree)

        # 扫描并初始化所有包含文件的路径图谱
        for sub_tree in other_trees:
            # 清空这些作为模板的 include 树的老属性，准备接收大树融合后的最新值
            # 注意：如果您只想提取主树，不想修改传入的 other_trees 实例，
            # 可以对 other_trees 先行做深拷贝，或者让此函数只返回 main_tree
            build_include_maps(sub_tree, sub_tree)

        # 3. 辅助函数：根据路径创建或寻回节点
        def get_or_create_node_by_path(target_root, absolute_path: str):
            if absolute_path == "/":
                return target_root
            parts = [p for p in absolute_path.split('/') if p]
            curr = target_root
            for part in parts:
                curr = curr.add_child(part)
            return curr

        # 4. 深度扫描融合大树（root_tree），进行按路分流
        def distribute_nodes(merged_node):
            if not merged_node or merged_node.name.startswith('&'):
                return

            current_path = merged_node.path
            
            # 检查大树中的这个路径，原本属于哪个 include 文件
            belonging_include_tree = path_to_include_tree_map.get(current_path)

            if belonging_include_tree:
                # ------ 情况 A：这个节点原本就是 include 文件长出来的骨架 ------
                # 寻找或在对应的包含树中构建相同的路径节点
                inc_target_node = get_or_create_node_by_path(belonging_include_tree, current_path)
                
                # 将融合大树中的最新属性同步回包含树节点
                inc_target_node.properties = merged_node.properties.copy()
                if merged_node.label:
                    inc_target_node.label = merged_node.label
                
                # 💡 【关键重构思想】：如果大树里某些属性被修改了，且您希望主文件保留覆写痕迹
                # 您可以在这里对比 merged_node.properties 与 sub_tree 的初始快照差集（如有必要）
            else:
                # ------ 情况 B：这个路径在所有 include 文件中都从未出现过 ------
                # 说明这是主文件（main_tree）独自在根目录下开辟的全新物理物理节点
                if current_path != "/":
                    main_target_node = get_or_create_node_by_path(main_tree, current_path)
                    main_target_node.properties = merged_node.properties.copy()
                    if merged_node.label:
                        main_target_node.label = merged_node.label

            # 递归向下分流所有子孙
            for child in list(merged_node.children.values()):
                distribute_nodes(child)

        # 执行骨架分流
        distribute_nodes(root_tree)

        # 5. 【高阶提炼】：主文件覆盖块提炼（&label）
        # 在 DTS 中，主文件经常通过 `&i2c0 { status = "okay"; };` 来修改 include 里的属性。
        # 上面的分流会将最新属性同步给 include，但为了让导出的 main_tree 拥有这些覆写痕迹，
        # 我们检查大树中的属性，并为主树生成对应的 &label 覆盖块。
        for label_name, orig_phys_path in include_labels_registry.items():
            # 从融合大树中拿到最新的实时物理节点
            merged_phys_node = root_tree.find_node(label=label_name)
            if merged_phys_node:
                # 创建一个形如 &i2c0 的新临时节点挂在主树的根节点下
                ref_node_name = f"&{label_name}"
                
                # 提炼出主树在该引用块中追加或覆写的属性
                # （如果您有初始备份，可以作 Diff 差集提炼；若无，则将最新状态做引用挂载）
                ref_node = main_tree.add_child(ref_node_name)
                ref_node.properties = merged_phys_node.properties.copy()

        return main_tree

    @classmethod
    def clean_phandle(cls, root_tree: "OpenDeviceTreeNode") -> "OpenDeviceTreeNode":
        """
        核心重构算法：全局深度遍历整棵树，提取 phandle 的值赋给节点的 label，然后物理清除该 phandle 属性。
        💡 策略：
          1. 遍历 root_tree 下的所有物理节点。
          2. 如果节点拥有 phandle 属性，清洗其括号（如 <0x1> 提取为 0x1），并将其设置为该节点的最新 label。
          3. 安全移除 'phandle' 和 'linux,phandle'。
        """
        if not root_tree:
            return root_tree

        # 🚀 利用节点自带的 traverse() 一键深度优先扫描全树
        for node in root_tree.traverse():
            # 跳过临时引用节点，只处理正常的物理树节点
            if node.name.startswith('&'):
                continue
                
            # 1. 尝试寻找 phandle 的值
            phandle_val = None
            for key in ('phandle', 'linux,phandle'):
                if key in node.properties:
                    phandle_val = node.properties[key]
                    # 顺手删除该属性，完成清理工作
                    del node.properties[key]
            
            # 2. 如果找到了 phandle 的值，将其清洗并赋予 label
            if phandle_val:
                # 💡 容错清洗：去掉设备树常见的尖括号 `<...>` 以及前后的多余空格
                # 例如：将 `<0x1>` 转换为 `0x1`，将 `< 1 >` 转换为 `1`
                clean_label = re.sub(r'[<>\s]', '', str(phandle_val))
                
                if clean_label:
                    node.label = clean_label
                    print(f"DEBUG: 节点 [{node.path}] 已成功将 phandle 值转化为新 Label: {node.label}")

        return root_tree

