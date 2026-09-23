import os
import re, tempfile
from devicetree import dtlib
from pathlib import Path
from lib.odtlib import OpenDeviceTree
from lib.dmanager import OpenDeviceTreeManager

if __name__ == "__main__":
    # dts_file_path = Path.cwd() / "devicetree/rk3399-eaidk-610.dts"
    # dts_file_path = Path.cwd() / "devicetree/rk3399.dtsi"
    # dts_file_path = Path.cwd() / "devicetree/test.dts"
    dts_file_path = Path.cwd() / "devicetree/xl.dts"
    include_folders = None 
    dt = OpenDeviceTreeManager(dts_file_path)
    print(f"DTS File Path: {dt.file_path}\nKernel Path: {dt.kernelpath}")
    try:
        # base_dir = dt.base_dir
        # raw_includes = dt.all_raw_includes
        # header_paths = dt.dts_headers
        # for key, val in dt.dts_defines.items():
        #     print(f"Alias: {key} -> {val}")

        print(f"DTS has Phandle/linux, phandle: {dt.main_tree_has_phandle}")

        root = dt.new_tree
        print(root.to_dts_file)
        # print(f"Base DIR: {base_dir};\nRAW Includes: {raw_includes};\nDTSi Includes: {dt.dts_includes};\nDTS Headers: {dt.dts_headers}")

        # test main_tree
        # for node in dt.main_tree.nodes:
        #     print(f"Name: {node.name}; Label: {node.label}; Property: {len(node.properties)} as follow: {node.properties}")
        # node = dt.main_tree.find_node("aliases")
        # for key, val in node.properties.items():
        #     print(f"Property: {key} = {val}")

        #test phandle
        # print(f"Main Tree: {len(dt.main_tree.nodes)} nodes; Root Tree: {len(dt.root_tree.nodes)} nodes; Gap: {len(dt.root_tree.nodes) - len(dt.main_tree.nodes)}")

    except Exception as e:
        print(f"❌ 运行失败: {e}")




