 git reset --hard origin/main


 trees_devide:

输出    
@classmethod
def trees_devide(cls, main_tree, other_trees: list):
maintree 和 othertrees是OpenDeviceTreeNode按以下步骤：
 step1: main_tree从othertrees里恢复节点标签，Debug输出。
 step2: main_tree从properties中phandle或linux phandle提取值写入phandle属性，然后从properties删除phandle。添加DEBUG输出
 step3：找出有phandle值引用的属性，将对应引用值换成对应节点的标签的引用，添加DEBUG输出
 step4: main_tree 去除所有 include含有的同名节点，相同值的属性，最后将节点名改成&label引用节点。添加debug输出
 step5：将所有的十六进制值换成十进制值， 添加debug输出