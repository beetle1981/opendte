# # utils.py
# from PySide6.QtWidgets import QApplication
# from PySide6.QtGui import QPalette, QColor

# def apply_dark_theme():
#     """动态注入暗黑科技感配色（完美修复菜单栏隐形字）"""
#     app = QApplication.instance()
#     if not app: return
    
#     # 1. 深度配置底层 QPalette
#     palette = QPalette()
#     palette.setColor(QPalette.Window, QColor(30, 30, 30))          # 窗口背景
#     palette.setColor(QPalette.WindowText, QColor(220, 220, 220))   # 文字：浅白
#     palette.setColor(QPalette.Base, QColor(24, 24, 24))            # 树/表格背景
#     palette.setColor(QPalette.AlternateBase, QColor(30, 30, 30))
#     palette.setColor(QPalette.Text, QColor(220, 220, 220))
#     palette.setColor(QPalette.Button, QColor(45, 45, 45))          # 按钮背景
#     palette.setColor(QPalette.ButtonText, QColor(220, 220, 220))
#     palette.setColor(QPalette.Highlight, QColor(0, 120, 215))      # 激活蓝色
#     palette.setColor(QPalette.HighlightedText, QColor(255, 255, 255))
#     app.setPalette(palette)

#     # 2. 深度配置全局 QSS（通过选择器强行打破操作系统的黑色菜单字保护）
#     dark_qss = """
#     /* 🚀【核心修复】：强行让顶层菜单栏及其子菜单的文字变为浅白/亮灰色 */
#     QMenuBar {
#         background-color: #1e1e1e;
#         color: #dcdfe6;             /* 顶层菜单栏文字颜色 */
#         border-bottom: 1px solid #3a3a3a;
#     }
    
#     QMenuBar::item {
#         background: transparent;
#         padding: 4px 10px;
#         color: #dcdfe6;
#     }
    
#     QMenuBar::item:selected {
#         background-color: #333333; /* 鼠标悬停在顶层菜单时的背景 */
#         color: #ffffff;
#     }

#     QMenu {
#         background-color: #1e1e1e;  /* 下拉菜单背景 */
#         color: #dcdfe6;             /* 下拉菜单文字颜色 */
#         border: 1px solid #3a3a3a;
#         padding: 5px;
#     }

#     QMenu::item {
#         padding: 6px 24px 6px 20px;
#         background: transparent;
#         color: #dcdfe6;
#     }

#     QMenu::item:selected {
#         background-color: #0078d7;  /* 鼠标悬停在菜单项上的背景 */
#         color: #ffffff;             /* 悬停时的文字变为纯白 */
#     }
    
#     QMenu::separator {
#         height: 1px;
#         background: #3a3a3a;        /* 菜单分割线 */
#         margin: 4px 0px;
#     }

#     /* 以下为您原有的基础组件深色样式，保持不变 */
#     QScrollBar:vertical { border: none; background: #1e1e1e; width: 10px; margin: 0px; }
#     QScrollBar::handle:vertical { background: #424242; min-height: 20px; border-radius: 5px; }
#     QScrollBar::handle:vertical:hover { background: #4f4f4f; }
#     QScrollBar:horizontal { border: none; background: #1e1e1e; height: 10px; margin: 0px; }
#     QScrollBar::handle:horizontal { background: #424242; min-width: 20px; border-radius: 5px; }
#     QSplitter::handle { background-color: #3a3a3a; }
#     QSplitter::handle:horizontal { width: 2px; }
#     QSplitter::handle:vertical { height: 2px; }
#     QTreeView, QTableView, QTextEdit { border: 1px solid #3a3a3a; gridline-color: #2d2d2d; }
#     QTabBar::tab {
#         background-color: #242424; color: #aaaaaa; padding: 6px 14px; 
#         border: 1px solid #3a3a3a; border-bottom: none; border-top-left-radius: 4px; border-top-right-radius: 4px;
#     }
#     QTabBar::tab:selected { background-color: #0078d7; color: #ffffff; border-color: #0078d7; font-weight: bold; }
#     QTabBar::tab:hover:!selected { background-color: #2d2d2d; color: #ffffff; }
#     QHeaderView::section { background-color: #242424; color: #dcdfe6; border: 1px solid #3a3a3a; padding: 4px; qproperty-alignment: AlignCenter; }
#     """
#     app.setStyleSheet(dark_qss)


# def apply_light_theme():
#     """动态注入极简浅色工业级配色"""
#     app = QApplication.instance()
#     if not app: return
    
#     palette = QPalette()
#     palette.setColor(QPalette.Window, QColor(246, 248, 250))       # 窗口背景
#     palette.setColor(QPalette.WindowText, QColor(36, 41, 46))        # 主文字
#     palette.setColor(QPalette.Base, QColor(255, 255, 255))          # 树/表格背景
#     palette.setColor(QPalette.AlternateBase, QColor(246, 248, 250))
#     palette.setColor(QPalette.Text, QColor(36, 41, 46))
#     palette.setColor(QPalette.Button, QColor(243, 244, 246))
#     palette.setColor(QPalette.ButtonText, QColor(36, 41, 46))
#     palette.setColor(QPalette.Highlight, QColor(3, 102, 214))       # 激活明亮蓝
#     palette.setColor(QPalette.HighlightedText, QColor(255, 255, 255))
#     app.setPalette(palette)

#     light_qss = """
#     QScrollBar:vertical { border: none; background: #f6f8fa; width: 10px; }
#     QScrollBar::handle:vertical { background: #d1d5da; border-radius: 5px; }
#     QScrollBar::handle:vertical:hover { background: #959da5; }
#     QSplitter::handle { background-color: #e1e4e8; }
#     QSplitter::handle:horizontal { width: 2px; }
#     QTreeView, QTableView, QTextEdit { border: 1px solid #e1e4e8; gridline-color: #f6f8fa; }
#     QTabBar::tab {
#         background-color: #e1e4e8; color: #586069; padding: 6px 14px; 
#         border: 1px solid #e1e4e8; border-bottom: none; border-top-left-radius: 4px; border-top-right-radius: 4px;
#     }
#     QTabBar::tab:selected { background-color: #0366d6; color: #ffffff; border-color: #0366d6; font-weight: bold; }
#     QTabBar::tab:hover:!selected { background-color: #f1f8ff; color: #0366d6; }
#     QHeaderView::section { background-color: #f6f8fa; color: #24292e; border: 1px solid #e1e4e8; padding: 4px; qproperty-alignment: AlignCenter; }
#     """
#     app.setStyleSheet(light_qss)

# utils.py
from PySide6.QtWidgets import QApplication
from PySide6.QtGui import QPalette, QColor

def apply_gold_theme():
    """动态注入独家定制：黑金奢华科技主题 (Gold Theme)"""
    app = QApplication.instance()
    if not app: return
    
    # 1. 深度配置黑金底层调色板
    palette = QPalette()
    palette.setColor(QPalette.Window, QColor(25, 25, 25))          # 窗口背景：深曜石黑
    palette.setColor(QPalette.WindowText, QColor(230, 210, 180))   # 文字：香槟淡金
    palette.setColor(QPalette.Base, QColor(18, 18, 18))            # 内容区背景：极深黑
    palette.setColor(QPalette.AlternateBase, QColor(25, 25, 25))
    palette.setColor(QPalette.Text, QColor(230, 210, 180))
    palette.setColor(QPalette.Button, QColor(40, 36, 30))          # 按钮带有微微古铜色暗影
    palette.setColor(QPalette.ButtonText, QColor(212, 175, 55))    # 按钮文字：黄金色
    palette.setColor(QPalette.Highlight, QColor(212, 175, 55))      # 🌟 激活高亮色：奢华沙滩金 (#D4AF37)
    palette.setColor(QPalette.HighlightedText, QColor(18, 18, 18))  # 选中时文字反色为极深黑
    app.setPalette(palette)

    # 2. 注入黑金语义化全局 QSS 样式表
    gold_qss = """
    QMainWindow, QStatusBar { background-color: #191919; color: #E6D2B4; }
    QSplitter::handle { background-color: #332F28; }
    QSplitter::handle:horizontal { width: 2px; }
    QSplitter::handle:vertical { height: 2px; }
    
    QTreeView, QTableView, QTextEdit { 
        background-color: #121212; color: #E6D2B4; border: 1px solid #332F28; gridline-color: #22201C; 
    }
    /* 单击聚焦时保持黑金边框，不出现蓝色框 */
    QTreeView:focus, QTableView:focus, QTextEdit:focus { 
        border: 1px solid #332F28; 
        outline: none;
    }
    
    /* 表头高亮黄金色文字 */
    QHeaderView::section { background-color: #22201C; color: #D4AF37; border: 1px solid #332F28; padding: 5px; qproperty-alignment: AlignCenter; }
    
    /* MDI 子窗体标题栏黑金高亮 */
    QMdiSubWindow { border: 1px solid #332F28; }
    QMdiSubWindow:active { qproperty-windowTitleBackgroundColor: #544634; qproperty-windowTitleTextColor: #D4AF37; }
    QMdiSubWindow:!active { qproperty-windowTitleBackgroundColor: #22201C; qproperty-windowTitleTextColor: #888070; }
    
    /* 选项卡高亮 */
    QTabBar::tab { background-color: #22201C; color: #888070; padding: 6px 14px; border: 1px solid #332F28; border-bottom: none; border-top-left-radius: 4px; border-top-right-radius: 4px; }
    QTabBar::tab:selected { background-color: #D4AF37; color: #121212; border-color: #D4AF37; font-weight: bold; }
    QTabBar::tab:hover:!selected { background-color: #332F28; color: #D4AF37; }
    
    /* 顶层菜单栏与下拉菜单黑金质感 */
    QMenuBar { background-color: #191919; color: #E6D2B4; border-bottom: 1px solid #332F28; }
    QMenuBar::item { background: transparent; padding: 4px 10px; color: #E6D2B4; }
    QMenuBar::item:selected { background-color: #2A2620; color: #D4AF37; }
    QMenu { background-color: #191919; color: #E6D2B4; border: 1px solid #332F28; padding: 4px; }
    QMenu::item:selected { background-color: #D4AF37; color: #121212; }
    QMenu::separator { height: 1px; background-color: #332F28; margin: 4px 0px; }
    
    QScrollBar:vertical { border: none; background: #191919; width: 8px; }
    QScrollBar::handle:vertical { background: #4F473A; border-radius: 4px; }
    QScrollBar::handle:vertical:hover { background: #6E6351; }
    """
    app.setStyleSheet(gold_qss)


def apply_dark_theme():
    """动态注入暗黑科技感配色"""
    app = QApplication.instance()
    if not app: return
    palette = QPalette()
    palette.setColor(QPalette.Window, QColor(30, 30, 30))
    palette.setColor(QPalette.WindowText, QColor(220, 220, 220))
    palette.setColor(QPalette.Base, QColor(24, 24, 24))
    palette.setColor(QPalette.AlternateBase, QColor(30, 30, 30))
    palette.setColor(QPalette.Text, QColor(220, 220, 220))
    palette.setColor(QPalette.Button, QColor(45, 45, 45))
    palette.setColor(QPalette.ButtonText, QColor(220, 220, 220))
    palette.setColor(QPalette.Highlight, QColor(0, 120, 215))
    palette.setColor(QPalette.HighlightedText, QColor(255, 255, 255))
    app.setPalette(palette)
    dark_qss = """
    QMainWindow, QStatusBar { background-color: #1E1E1E; color: #DCDFE6; }
    QSplitter::handle { background-color: #3A3A3A; }
    QSplitter::handle:horizontal { width: 2px; }
    QSplitter::handle:vertical { height: 2px; }
    QTreeView, QTableView, QTextEdit { background-color: #181818; color: #DCDFE6; border: 1px solid #3A3A3A; gridline-color: #2D2D2D; }
    QTreeView:focus, QTableView:focus, QTextEdit:focus { border: 1px solid #3A3A3A; outline: none; }
    QHeaderView::section { background-color: #242424; color: #888888; border: 1px solid #3A3A3A; padding: 5px; qproperty-alignment: AlignCenter; }
    QMdiSubWindow { border: 1px solid #3A3A3A; }
    QMdiSubWindow:active { qproperty-windowTitleBackgroundColor: #005a9e; qproperty-windowTitleTextColor: #ffffff; }
    QMdiSubWindow:!active { qproperty-windowTitleBackgroundColor: #2d2d2d; qproperty-windowTitleTextColor: #888888; }
    QTabBar::tab { background-color: #242424; color: #AAAAAA; padding: 6px 14px; border: 1px solid #3A3A3A; border-bottom: none; border-top-left-radius: 4px; border-top-right-radius: 4px; }
    QTabBar::tab:selected { background-color: #0078D7; color: #FFFFFF; border-color: #0078D7; font-weight: bold; }
    QTabBar::tab:hover:!selected { background-color: #2D2D2D; color: #FFFFFF; }
    QMenuBar { background-color: #1E1E1E; color: #DCDFE6; border-bottom: 1px solid #3A3A3A; }
    QMenuBar::item { background: transparent; padding: 4px 10px; color: #DCDFE6; }
    QMenuBar::item:selected { background-color: #333333; }
    QMenu { background-color: #1E1E1E; color: #DCDFE6; border: 1px solid #3A3A3A; padding: 4px; }
    QMenu::item:selected { background-color: #0078D7; color: #FFFFFF; }
    QMenu::separator { height: 1px; background-color: #3A3A3A; margin: 4px 0px; }
    QScrollBar:vertical { border: none; background: #1E1E1E; width: 8px; }
    QScrollBar::handle:vertical { background: #424242; border-radius: 4px; }
    QScrollBar::handle:vertical:hover { background: #4F4F4F; }
    """
    app.setStyleSheet(dark_qss)

def apply_light_theme():
    """动态注入极简浅色主题"""
    app = QApplication.instance()
    if not app: return
    palette = QPalette()
    palette.setColor(QPalette.Window, QColor(246, 248, 250))
    palette.setColor(QPalette.WindowText, QColor(36, 41, 46))
    palette.setColor(QPalette.Base, QColor(255, 255, 255))
    palette.setColor(QPalette.AlternateBase, QColor(246, 248, 250))
    palette.setColor(QPalette.Text, QColor(36, 41, 46))
    palette.setColor(QPalette.Button, QColor(243, 244, 246))
    palette.setColor(QPalette.ButtonText, QColor(36, 41, 46))
    palette.setColor(QPalette.Highlight, QColor(3, 102, 214))
    palette.setColor(QPalette.HighlightedText, QColor(255, 255, 255))
    app.setPalette(palette)
    light_qss = """
    QMainWindow, QStatusBar { background-color: #F6F8FA; color: #24292E; }
    QSplitter::handle { background-color: #E1E4E8; }
    QSplitter::handle:horizontal { width: 2px; }
    QSplitter::handle:vertical { height: 2px; }
    QTreeView, QTableView, QTextEdit { background-color: #FFFFFF; color: #24292E; border: 1px solid #E1E4E8; gridline-color: #F6F8FA; }
    QTreeView:focus, QTableView:focus, QTextEdit:focus { border: 1px solid #E1E4E8; outline: none; }
    QHeaderView::section { background-color: #F6F8FA; color: #586069; border: 1px solid #E1E4E8; padding: 5px; qproperty-alignment: AlignCenter; }
    QMdiSubWindow { border: 1px solid #E1E4E8; }
    QMdiSubWindow:active { qproperty-windowTitleBackgroundColor: #0366D6; qproperty-windowTitleTextColor: #ffffff; }
    QMdiSubWindow:!active { qproperty-windowTitleBackgroundColor: #e1e4e8; qproperty-windowTitleTextColor: #586069; }
    QTabBar::tab { background-color: #E1E4E8; color: #586069; padding: 6px 14px; border: 1px solid #E1E4E8; border-bottom: none; border-top-left-radius: 4px; border-top-right-radius: 4px; }
    QTabBar::tab:selected { background-color: #0366D6; color: #FFFFFF; border-color: #0366D6; font-weight: bold; }
    QTabBar::tab:hover:!selected { background-color: #F1F8FF; color: #0366D6; }
    QMenuBar { background-color: #F6F8FA; color: #24292E; border-bottom: 1px solid #E1E4E8; }
    QMenuBar::item:selected { background-color: #E1E4E8; }
    QMenu { background-color: #FFFFFF; color: #24292E; border: 1px solid #E1E4E8; padding: 4px; }
    QMenu::item:selected { background-color: #0366D6; color: #FFFFFF; }
    QMenu::separator { height: 1px; background-color: #E1E4E8; margin: 4px 0px; }
    QScrollBar:vertical { border: none; background: #F6F8FA; width: 8px; }
    QScrollBar::handle:vertical { background: #D1D5DA; border-radius: 4px; }
    QScrollBar::handle:vertical:hover { background: #959DA5; }
    """
    app.setStyleSheet(light_qss)