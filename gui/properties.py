from PySide6.QtGui import QStandardItemModel, QStandardItem
from PySide6.QtWidgets import QTableView
from lib.dnode import OpenDeviceTreeNode

table_view = QTableView()
model = QStandardItemModel(4, 3) # 初始化 4 行 3 列
model.setHorizontalHeaderLabels(["属性名", "值", "描述"])
table_view.setModel(model)
