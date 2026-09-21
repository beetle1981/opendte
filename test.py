import os
import re, tempfile
from devicetree import dtlib
from pathlib import Path
from lib.odtlib import OpenDeviceTree

if __name__ == "__main__":
    dts_file_path = Path.cwd() / "devicetree/rk3399-eaidk-610.dts"
    # dts_file_path = Path.cwd() / "../devicetree/rk3399.dtsi"
    # dts_file_path = Path.cwd() / "../devicetree/test.dts"
    # dts_file_path = Path.cwd() / "../devicetree/xl.dts"
    include_folders = None 
    print(dts_file_path)
    dt = OpenDeviceTree(dts_file_path)
    try:
        # test main_tree
        # for node in dt.main_tree.nodes:
        #     print(f"Name: {node.name}; Label: {node.label}; Property: {len(node.properties)} as follow: {node.properties}")
        # node = dt.main_tree.find_node("aliases")
        # for key, val in node.properties.items():
        #     print(f"Property: {key} = {val}")

        #test phandle
        dt.main_tree

    except Exception as e:
        print(f"❌ 运行失败: {e}")




