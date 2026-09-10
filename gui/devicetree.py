import os
from PySide6.QtWidgets import QTreeView, QFileSystemModel
from PySide6.QtCore import QDir, Signal

class CustomFileTreeView(QTreeView):
    # Signal emitted when a file is double-clicked, carrying the absolute file path
    file_double_clicked = Signal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        
        # Configure file system data model
        self.file_model = QFileSystemModel()
        root_path = QDir.currentPath()
        self.file_model.setRootPath(root_path)
        
        # Bind model to view
        self.setModel(self.file_model)
        self.setRootIndex(self.file_model.index(root_path))
        
        # Visual enhancements
        self.setAnimated(True)
        self.setIndentation(20)
        self.setSortingEnabled(True)
        self.setColumnWidth(0, 250)
        
        # Hide extra columns (Size, Type, Date Modified) for cleaner sidebar layout
        for i in range(1, self.file_model.columnCount()):
            self.setColumnHidden(i, True)
            
        # Connect internal double-click event to our custom handler
        self.doubleClicked.connect(self.on_double_click)

    def on_double_click(self, index):
        file_path = self.file_model.filePath(index)
        if os.path.isfile(file_path):
            # Emit signal to notify main controller
            self.file_double_clicked.emit(file_path)
