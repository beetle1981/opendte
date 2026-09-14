import sys
from PySide6.QtWidgets import QApplication, QMainWindow, QSplitter
from PySide6.QtCore import Qt
import os

from gui.file_tree import CustomFileTreeView
from gui.menu_bar import CustomMenuBar
from gui.mdi_area import MdiManagerArea
from gui.device_tree import CustomDeviceTreeView

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Open Device Tree Editor")
        self.resize(1100, 600)

        # Enable the status bar at the bottom
        self.statusBar()

        # Instantiate sub-components
        self.file_tree = CustomFileTreeView()
        self.device_tree = CustomDeviceTreeView()
        self.mdi_manager = MdiManagerArea()
        
        # Assemble UI layout using QSplitter
        main_splitter = QSplitter(Qt.Orientation.Horizontal)
        main_splitter.addWidget(self.file_tree)    # Left Column
        main_splitter.addWidget(self.device_tree)    # Center Column
        main_splitter.addWidget(self.mdi_manager)  # Right Column
        main_splitter.setSizes([250, 250, 600])         # Initial column widths
        self.setCentralWidget(main_splitter)

        # Initialize and attach the menu bar
        self.menu_manager = CustomMenuBar(self)

        # Establish cross-module signal communications
        self.file_tree.file_double_clicked.connect(self.mdi_manager.load_file_content)
        self.file_tree.file_double_clicked.connect(self.device_tree.load_dts_file)
        self.mdi_manager.file_loaded.connect(self.update_window_title)

    def update_window_title(self, file_path):
        file_name = os.path.basename(file_path)
        self.setWindowTitle(f"Editing: {file_name} - Open Device Tree Editor")
        self.statusBar().showMessage(f"Successfully opened: {file_name}", 3000)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    main_win = MainWindow()
    main_win.show()
    sys.exit(app.exec())
