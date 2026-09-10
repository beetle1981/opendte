from PySide6.QtWidgets import QTextEdit, QMessageBox
from PySide6.QtCore import Signal
import os

class CustomTextEditor(QTextEdit):
    # Signal emitted when a text file is successfully loaded, carrying the file path
    file_loaded = Signal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setPlainText("Welcome! Please go to [File] -> [Open Folder...] to load your projectWorkspace.")
        self.setStyleSheet("font-size: 14px; font-family: 'Consolas', 'Segoe UI', monospace;")

    def load_file_content(self, file_path):
        """Reads file data safely and updates the editor layout."""
        if os.path.isfile(file_path):
            try:
                # Attempt to open and read with standard UTF-8 encoding
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    self.setPlainText(content)
                
                # Emit signal to notify main script for window title modifications
                self.file_loaded.emit(file_path)
                
            except Exception as e:
                QMessageBox.critical(
                    self, 
                    "Read Error", 
                    f"Could not open this file (it might not be a valid text format).\nReason: {str(e)}"
                )
