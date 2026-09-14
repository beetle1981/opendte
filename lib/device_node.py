import re
import sys

def clean_device_tree(input_file, output_file):
    with open(input_file, 'r', encoding='utf-8') as f:
        content = f.read()

    # ==========================================
    # 步骤 1: 扫描并映射所有的 phandle (支持 0x 十六进制和纯数字)
    # ==========================================
    # 匹配类似: phandle = <0x22>; 或 linux,phandle = <0x22>; 或 phandle = <34>;
    pattern_def = r'(?:linux,)?phandle\s*=\s*<(0x[0-9a-fA-F]+|\d+)>;'
    phandles = re.findall(pattern_def, content)
    
    # 建立映射表。为了代码美观，统一将数字转为标准十六进制格式标签
    phandle_map = {}
    for p in phandles:
        if p.startswith('0x'):
            val_hex = p.lower()
        else:
            val_hex = hex(int(p))
        phandle_map[p] = f"lbl_{val_hex}"

    if not phandle_map:
        print("提示: 未在 DTS 文件中检测到任何显式定义的 phandle 属性。")
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(content)
        return

    # ==========================================
    # 步骤 2: 逐行扫描，自动在节点头部插标签，并擦除 phandle 定义行
    # ==========================================
    lines = content.split('\n')
    cleaned_lines = []
    
    # 辅助变量，用于在进入节点后，一旦发现它带 phandle，就回溯到节点开头打标签
    node_stack = [] 

    for idx, line in enumerate(lines):
        stripped = line.strip()
        
        # 记录当前节点开头的行索引 (识别带有左大括号的行)
        if '{' in line and (r'@' in line or stripped.endswith('{')):
            node_stack.append({
                'line_idx': len(cleaned_lines),
                'indent': line[:line.find(line.strip())] # 保留原有缩进
            })
            
        # 发现 phandle 定义行
        match_def = re.search(pattern_def, line)
        if match_def:
            p_val = match_def.group(1)
            lbl_name = phandle_map[p_val]
            
            # 回溯并将标签打到当前大括号所在节点的正上方
            if node_stack:
                target_node = node_stack[-1]
                target_idx = target_node['line_idx']
                indent = target_node['indent']
                # 在节点名上方单独插入一行规范的标签： lbl_0x22:
                cleaned_lines.insert(target_idx, f"{indent}{lbl_name}:")
                
            # ⚡ 核心：跳过这一行，从而实现彻底抹除 "phandle = <0x...>;" 行
            continue

        if '}' in line:
            if node_stack:
                node_stack.pop()

        cleaned_lines.append(line)

    final_content = '\n'.join(cleaned_lines)

    # ==========================================
    # 步骤 3: 全局高级正则替换交叉引用 (例如将 <0x22> 替换为 <&lbl_0x22>)
    # ==========================================
    # 必须精准过滤，防止误伤含有相同数字的其他属性值
    # for orig_val, lbl_name in phandle_map.items():
    #     # 情况 A: 单个 phandle 引用，如: interrupt-parent = <0x22>;
    #     final_content = re.sub(
    #         r'<\s*' + re.escape(orig_val) + r'\s*>;', 
    #         f"<&{lbl_name}>;", 
    #         final_content
    #     )
    #     # 情况 B: 复合 phandle 引用，如: clocks = <0x22 0x01>; 或者是复合数组
    #     final_content = re.sub(
    #         r'<\s*' + re.escape(orig_val) + r'\s+', 
    #         f"<&{lbl_name} ", 
    #         final_content
    #     )
    #     final_content = re.sub(
    #         r'\s+' + re.escape(orig_val) + r'\s*>', 
    #         f" &{lbl_name}>", 
    #         final_content
    #     )
    #     final_content = re.sub(
    #         r'\s+' + re.escape(orig_val) + r'\s+', 
    #         f" &{lbl_name} ", 
    #         final_content
    #     )

    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(final_content)
    print(f"清洗成功！成功将 {len(phandle_map)} 个死数字 phandle 转换为安全的标签语法 (&lbl)。")
