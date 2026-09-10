from PySide6.QtWidgets import QMenuBar, QFileDialog
from PySide6.QtGui import QAction, QKeySequence
from PySide6.QtCore import Signal, QDir

class CustomMenuBar:
    def __init__(self, main_window):
        self.main_win = main_window
        self.menu_bar = self.main_win.menuBar()
        
        self.create_file_menu()
        self.create_edit_menu()

    def create_file_menu(self):
        file_menu = self.menu_bar.addMenu("&File")

        # Open Folder Action
        open_folder_action = QAction("Open Folder...", self.main_win)
        open_folder_action.setShortcut("Ctrl+Shift+O")
        open_folder_action.setStatusTip("Select a folder to import into the file tree")
        open_folder_action.triggered.connect(self.trigger_open_folder)
        file_menu.addAction(open_folder_action)

        file_menu.addSeparator()

        # Exit Action
        exit_action = QAction("Exit", self.main_win)
        exit_action.setShortcut("Alt+F4")
        exit_action.triggered.connect(self.main_win.close)
        file_menu.addAction(exit_action)

    def create_edit_menu(self):
        edit_menu = self.menu_bar.addMenu("&Edit")

        # Undo Action
        undo_action = QAction("Undo", self.main_win)
        undo_action.setShortcut(QKeySequence.StandardKey.Undo)
        undo_action.triggered.connect(self.main_win.text_editor.undo)
        edit_menu.addAction(undo_action)

        # Redo Action
        redo_action = QAction("Redo", self.main_win)
        redo_action.setShortcut(QKeySequence.StandardKey.Redo)
        redo_action.triggered.connect(self.main_win.text_editor.redo)
        edit_menu.addAction(redo_action)

    def trigger_open_folder(self):
        selected_directory = QFileDialog.getExistingDirectory(
            self.main_win,
            "Select Folder to Open",
            QDir.currentPath(),
            QFileDialog.Option.ShowDirsOnly
        )

        if selected_directory:
            # Refresh Left Column (File Tree)
            self.main_win.file_tree.file_model.setRootPath(selected_directory)
            self.main_win.file_tree.setRootIndex(
                self.main_win.file_tree.file_model.index(selected_directory)
            )
            # Update Main Windows Properties
            self.main_win.setWindowTitle(f"Project: {selected_directory} - Modular Modern Editor")
            self.main_win.text_editor.setPlainText(
                f"Project Loaded: {selected_directory}\nDouble-click a file on the left side to start editing."
            )
            self.main_win.statusBar().showMessage(f"Current workspace: {selected_directory}", 4000)
