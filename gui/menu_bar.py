from PySide6.QtWidgets import QMenuBar, QFileDialog
from PySide6.QtGui import QAction, QKeySequence
from PySide6.QtCore import Signal, QDir

class CustomMenuBar:
    def __init__(self, main_window):
        self.main_win = main_window
        self.menu_bar = self.main_win.menuBar()
        
        self.create_file_menu()
        self.create_edit_menu()
        self.create_view_menu()

    def create_file_menu(self):
        file_menu = self.menu_bar.addMenu("&File")

        # 新建文档动作
        new_action = QAction("New File...", self.main_win)
        new_action.setShortcut("Ctrl+N")
        new_action.triggered.connect(self.main_win.mdi_manager.create_new_document)
        file_menu.addAction(new_action)

        file_menu.addSeparator()

        # Open Folder Action
        open_folder_action = QAction("Open Folder...", self.main_win)
        open_folder_action.setShortcut("Ctrl+Shift+O")
        open_folder_action.setStatusTip("Select a folder to import into the file tree")
        open_folder_action.triggered.connect(self.trigger_open_folder)
        file_menu.addAction(open_folder_action)

        file_menu.addSeparator()

        # 新增：保存动作
        save_action = QAction("Save", self.main_win)
        save_action.setShortcut("Ctrl+S")
        save_action.triggered.connect(self.main_win.mdi_manager.save_active_doc)
        file_menu.addAction(save_action)

        # 新增：另存为动作
        save_as_action = QAction("Save As...", self.main_win)
        save_as_action.setShortcut("Ctrl+Shift+S")
        save_as_action.triggered.connect(self.main_win.mdi_manager.save_as_active_doc)
        file_menu.addAction(save_as_action)        

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
        undo_action.triggered.connect(self.main_win.mdi_manager.undo_active_doc)
        edit_menu.addAction(undo_action)

        # Redo Action
        redo_action = QAction("Redo", self.main_win)
        redo_action.setShortcut(QKeySequence.StandardKey.Redo)
        redo_action.triggered.connect(self.main_win.mdi_manager.redo_active_doc)
        edit_menu.addAction(redo_action)

    # 窗口排列菜单
    def create_view_menu(self):
        window_menu = self.menu_bar.addMenu("Window")

        cascade_action = QAction("Cascade", self.main_win)
        cascade_action.triggered.connect(self.main_win.mdi_manager.cascadeSubWindows)
        window_menu.addAction(cascade_action)

        tile_action = QAction("Tile", self.main_win)
        tile_action.triggered.connect(self.main_win.mdi_manager.tileSubWindows)
        window_menu.addAction(tile_action)

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
            # self.main_win.mdi_area.setPlainText(
            #     f"Project Loaded: {selected_directory}\nDouble-click a file on the left side to start editing."
            # )
            self.main_win.statusBar().showMessage(f"Current workspace: {selected_directory}", 4000)
