import sys
from PySide6.QtWidgets import QApplication, QMainWindow, QSplitter
from PySide6.QtCore import Qt
import os

from gui.file_tree import CustomFileTreeView
from gui.menu_bar import CustomMenuBar
from gui.editor_area import CustomTextEditor

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("PySide6 Modular Modern Editor")
        self.resize(1100, 600)

        # Enable the status bar at the bottom
        self.statusBar()

        # Instantiate sub-components
        self.file_tree = CustomFileTreeView()
        self.text_editor = CustomTextEditor()
        
        # Assemble UI layout using QSplitter
        main_splitter = QSplitter(Qt.Orientation.Horizontal)
        main_splitter.addWidget(self.file_tree)    # Left Column
        main_splitter.addWidget(self.text_editor)  # Right Column
        main_splitter.setSizes([250, 850])         # Initial column widths
        self.setCentralWidget(main_splitter)

        # Initialize and attach the menu bar
        self.menu_manager = CustomMenuBar(self)

        # Establish cross-module signal communications
        self.file_tree.file_double_clicked.connect(self.text_editor.load_file_content)
        self.text_editor.file_loaded.connect(self.update_window_title)

    def update_window_title(self, file_path):
        file_name = os.path.basename(file_path)
        self.setWindowTitle(f"Editing: {file_name} - Modular Modern Editor")
        self.statusBar().showMessage(f"Successfully opened: {file_name}", 3000)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    main_win = MainWindow()
    main_win.show()
    sys.exit(app.exec())
