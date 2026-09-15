# 导入 Zephyr 的官方 dtlib
import os
from pathlib import Path
from devicetree import dtlib

# 解析文件 (它能非常完美地处理 / 根节点)
dts_file = Path.cwd() / "devicetree/test.dts"
dt = dtlib.DT(dts_file)

# 获取根节点并打印
root_node = dt.root
print("根节点名称:", root_node.name)

# 遍历子节点
for node in root_node.nodes.values():
    print(f"子节点: {node.name}")
