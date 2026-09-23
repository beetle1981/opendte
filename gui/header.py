import sys
from PySide6.QtCore import QSortFilterProxyModel, Qt, Signal
from PySide6.QtGui import QStandardItem, QStandardItemModel
from PySide6.QtWidgets import (
    QApplication,
    QLineEdit,
    QMainWindow,
    QTableView,
    QVBoxLayout,
    QWidget,
)
from lib.odtlib import OpenDeviceTree


class CustomTableView(QWidget):
    """自定义组合表格组件（自带实时搜索与过滤功能）"""
    file_loaded = Signal(str)

    def __init__(self, dts_file_path=None, parent=None):
        super().__init__(parent)
        self.filepath = dts_file_path

        # 1. 初始化界面控件
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("🔍 输入关键字实时搜索...")
        self.search_input.setClearButtonEnabled(True)  # 右侧自带一键清空按钮

        self.table_view = QTableView()
        self.table_view.horizontalHeader().setStretchLastSection(True)

        # 2. 初始化核心过滤代理模型
        self.proxy_model = QSortFilterProxyModel(self)
        self.proxy_model.setFilterCaseSensitivity(
            Qt.CaseSensitivity.CaseInsensitive
        )  # 忽略大小写
        self.proxy_model.setFilterKeyColumn(
            -1
        )  # 默认设为 -1 代表全局全列搜索。若只想搜第0列，可改为 0

        # 将视图绑定到代理模型
        self.table_view.setModel(self.proxy_model)

        # 3. 布局组装
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)  # 移除边距，完美嵌入 Splitter 分栏
        layout.addWidget(self.search_input)
        layout.addWidget(self.table_view)

        # 4. 信号绑定：输入框文本改变时，自动触发代理模型的过滤逻辑
        self.search_input.textChanged.connect(self.proxy_model.setFilterFixedString)

    def convert_defines_dict_to_model(self, defines_dict: dict) -> QStandardItemModel:
        """
        🚀【工具函数】：将提取出来的 #define 字典转化为 QStandardItemModel
        :param defines_dict: 你的类生成的 {宏名称: 数值} 字典
        """
        # 1. 初始化标准模型并设定 2 列的表头
        model = QStandardItemModel()
        model.setHorizontalHeaderLabels(["Alias (宏名称)", "Value (数值)"])
        
        # 如果输入的字典为空，直接返回带表头的空模型，防止界面崩溃
        if not defines_dict:
            return model

        # 2. 🚀【核心机制】：遍历字典的 items() 进行解包填充
        for key, val in defines_dict.items():
            key_item = QStandardItem(str(key))
            val_item = QStandardItem(str(val))
            
            # 💡 安全保护：设定单元格为只读，禁止用户双击直接修改文本
            key_item.setFlags(key_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
            val_item.setFlags(val_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
            
            # 将创建好的两列作为一个整体行追加进数据模型
            model.appendRow([key_item, val_item])
            
        return model

    def refresh_view(self, file_path):
        """
        【核心接口】：为主视图挂载原始数据模型
        :param source_model: 传入 QStandardItemModel 实例
        """
        self.filepath = file_path
        # 1. 重新从虚拟属性获取最新的 Model 实例
        
        self.model = self.convert_defines_dict_to_model(OpenDeviceTree(file_path).dts_defines) if file_path else QStandardItemModel()
        # 代理模型接管原始数据模型
        self.proxy_model.setSourceModel(self.model)
        # 自动优化列宽
        self.table_view.resizeColumnsToContents()

        self.file_loaded.emit(file_path)

    def get_selected_raw_data(self):
        """
        【进阶接口】：获取当前选中行在【原始数据源】中的文本内容
        常用于用户过滤后双击或点击某一行，安全映射回原始模型取值
        """
        indexes = self.table_view.selectionModel().selectedRows()
        if not indexes:
            return None

        # 取选中的第一行（在代理模型中的索引）
        proxy_index = indexes[0]
        # 🚀 关键：利用 mapToSource 将滤镜后的索引转换为原始模型的真实索引
        source_index = self.proxy_model.mapToSource(proxy_index)
        row = source_index.row()

        # 获取原始模型
        source_model = self.proxy_model.sourceModel()
        if not source_model:
            return None

        # 将这一整行所有列的数据提取出来存入列表返回
        row_data = [
            source_model.item(row, col).text()
            for col in range(source_model.columnCount())
        ]
        return row_data
