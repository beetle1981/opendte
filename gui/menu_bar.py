from PySide6.QtWidgets import QMenuBar, QFileDialog, QMdiArea
from PySide6.QtGui import QAction, QKeySequence, QActionGroup
from PySide6.QtCore import Signal, QDir, Qt
from gui.theme import apply_dark_theme, apply_light_theme, apply_gold_theme
from gui.settings import CustomSettingsManager

class CustomMenuBar:
    def __init__(self, main_window):
        self.main_win = main_window
        self.main_win.mdi_manager.setViewMode(QMdiArea.ViewMode.TabbedView)
        self.menu_bar = self.main_win.menuBar()
        
        # 存储需要动态修改状态的实例引用
        self.windows_menu = None
        self.tab_mode_action = None
        self.sub_mode_action = None
        self.cascade_action = None
        self.tile_action = None
        
        # 按顺序初始化所有顶层菜单项
        self.create_file_menu()
        self.create_edit_menu()
        self.create_view_menu()
        self.create_window_menu()
        self.create_theme_menu()
        self.create_tools_menu()

        # 统一配置启动时的默认选中与显隐状态
        self.init_default_state()

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

        # 保存动作
        save_action = QAction("Save", self.main_win)
        save_action.setShortcut("Ctrl+S")
        save_action.triggered.connect(self.main_win.mdi_manager.save_active_doc)
        file_menu.addAction(save_action)

        # 另存为动作
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
            self.main_win.statusBar().showMessage(f"Current workspace: {selected_directory}", 4000)

    def create_view_menu(self):
        view_menu = self.menu_bar.addMenu("View Mode")
        
        mode_group = QActionGroup(self.main_win)
        mode_group.setExclusive(True)

        # 选项卡模式动作
        self.tab_mode_action = QAction("Tabbed View (选项卡模式)", self.main_win)
        self.tab_mode_action.setCheckable(True)
        self.tab_mode_action.triggered.connect(self.switch_to_tabbed_view)
        view_menu.addAction(self.tab_mode_action)
        mode_group.addAction(self.tab_mode_action)

        # 多窗口模式动作
        self.sub_mode_action = QAction("Window View (多窗口模式)", self.main_win)
        self.sub_mode_action.setCheckable(True)
        self.sub_mode_action.triggered.connect(self.switch_to_subwindow_view)
        view_menu.addAction(self.sub_mode_action)
        mode_group.addAction(self.sub_mode_action)

    def create_window_menu(self):
        """创建 Windows 菜单"""
        self.windows_menu = self.menu_bar.addMenu("Windows")

        # 🚀 创建一个排他的动作组，用于控制层叠和平铺的单选状态
        arrange_group = QActionGroup(self.main_win)
        arrange_group.setExclusive(True)

        # 层叠动作
        self.cascade_action = QAction("Cascade（层叠）", self.main_win)
        self.cascade_action.setCheckable(True)  # 🌟 设为可勾选
        self.cascade_action.triggered.connect(self.trigger_cascade)
        self.windows_menu.addAction(self.cascade_action)
        arrange_group.addAction(self.cascade_action)

        # 平铺动作
        self.tile_action = QAction("Tile（平铺）", self.main_win)
        self.tile_action.setCheckable(True)  # 🌟 设为可勾选
        self.tile_action.triggered.connect(self.trigger_tile)
        self.windows_menu.addAction(self.tile_action)
        arrange_group.addAction(self.tile_action)

    def create_theme_menu(self):
        """核心实现：创建 Theme 菜单并实现打勾互斥三选一"""
        theme_menu = self.menu_bar.addMenu("Theme")
        
        # 创建排他动作组，让三套主题只能单选打勾
        theme_group = QActionGroup(self.main_win)
        theme_group.setExclusive(True)

        # 1. 浅色模式菜单项
        self.light_theme_action = QAction("Light (浅色模式)", self.main_win)
        self.light_theme_action.setCheckable(True)
        self.light_theme_action.triggered.connect(apply_light_theme)
        theme_menu.addAction(self.light_theme_action)
        theme_group.addAction(self.light_theme_action)

        # 2. 深色模式菜单项
        self.dark_theme_action = QAction("Dark (深色模式)", self.main_win)
        self.dark_theme_action.setCheckable(True)
        self.dark_theme_action.triggered.connect(apply_dark_theme)
        theme_menu.addAction(self.dark_theme_action)
        theme_group.addAction(self.dark_theme_action)

        # 3. 🚀【新增】：金色奢华模式菜单项
        self.gold_theme_action = QAction("Gold (金色奢华)", self.main_win)
        self.gold_theme_action.setCheckable(True)
        self.gold_theme_action.triggered.connect(apply_gold_theme)
        theme_menu.addAction(self.gold_theme_action)
        theme_group.addAction(self.gold_theme_action)

    def init_default_state(self):
        """🌟 升级：配置软件启动时的所有默认视觉状态"""
        # 1. 选项卡视图模式默认打勾
        if self.tab_mode_action:
            self.tab_mode_action.setChecked(True)
            
        # 2. Windows 菜单里的“层叠（Cascade）”默认打勾
        if self.cascade_action:
            self.cascade_action.setChecked(True)
            
        # 3. 🚀【核心修改】：让 Theme 菜单里的“Light (浅色模式)”默认打勾并生效
        if self.light_theme_action:
            self.light_theme_action.setChecked(True)
        apply_light_theme()  # 启动时立马渲染浅色主题

        # 4. 确保 MDI 底层设置为选项卡模式
        self.main_win.mdi_manager.setViewMode(QMdiArea.ViewMode.TabbedView)
        
        # 5. 默认隐藏顶层的 Windows 菜单
        if self.windows_menu:
            self.windows_menu.menuAction().setVisible(False)

    # ==========================================================
    # 🚀 状态切换与排列联动逻辑
    # ==========================================================
    def switch_to_tabbed_view(self):
        """切换至选项卡模式状态"""
        self.main_win.mdi_manager.setViewMode(QMdiArea.ViewMode.TabbedView)
        if self.windows_menu:
            self.windows_menu.menuAction().setVisible(False)

    def switch_to_subwindow_view(self):
        """切换至多窗口模式状态"""
        self.main_win.mdi_manager.setViewMode(QMdiArea.ViewMode.SubWindowView)
        if self.windows_menu:
            self.windows_menu.menuAction().setVisible(True)
            
        # 🌟 检查当前的勾选状态，动态执行对应的排列动作
        if self.tile_action and self.tile_action.isChecked():
            self.main_win.mdi_manager.tileSubWindows()
        else:
            # 默认或勾选层叠时，执行层叠排列
            if self.cascade_action:
                self.cascade_action.setChecked(True)
            self.main_win.mdi_manager.cascadeSubWindows()

    def trigger_cascade(self):
        """执行层叠并保持状态"""
        self.main_win.mdi_manager.cascadeSubWindows()

    def trigger_tile(self):
        """执行平铺并保持状态"""
        self.main_win.mdi_manager.tileSubWindows()

    def create_tools_menu(self):
        tools_menu = self.menu_bar.addMenu("&Tools")

        # Undo Action
        config_action = QAction("Conf（设置）", self.main_win)
        config_action.setShortcut(QKeySequence(Qt.Modifier.CTRL | Qt.Modifier.SHIFT | Qt.Key.Key_S))
        config_action.triggered.connect(self.main_win.settings_manager.open_settings_dialog)
        tools_menu.addAction(config_action)

        