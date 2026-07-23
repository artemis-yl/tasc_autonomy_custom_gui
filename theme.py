"""Application-wide visual language for the operator console."""

from PySide6.QtGui import QPalette, QColor


def apply_dark_theme(app):
    app.setStyle("Fusion")
    palette = QPalette()
    palette.setColor(QPalette.Window, QColor("#11161c"))
    palette.setColor(QPalette.WindowText, QColor("#e7edf4"))
    palette.setColor(QPalette.Base, QColor("#151c24"))
    palette.setColor(QPalette.AlternateBase, QColor("#1c2631"))
    palette.setColor(QPalette.ToolTipBase, QColor("#202b36"))
    palette.setColor(QPalette.ToolTipText, QColor("#edf4fb"))
    palette.setColor(QPalette.Text, QColor("#e7edf4"))
    palette.setColor(QPalette.Button, QColor("#25313d"))
    palette.setColor(QPalette.ButtonText, QColor("#e7edf4"))
    palette.setColor(QPalette.Highlight, QColor("#2b8ac6"))
    palette.setColor(QPalette.HighlightedText, QColor("#ffffff"))
    app.setPalette(palette)
    app.setStyleSheet("""
        * { font-family: "Segoe UI", Arial, sans-serif; }
        QMainWindow { background: #11161c; }
        QMenuBar { background: #151c24; color: #c8d3dd; padding: 3px 6px; border-bottom: 1px solid #273441; }
        QMenuBar::item { padding: 5px 9px; border-radius: 3px; }
        QMenuBar::item:selected, QMenu::item:selected { background: #263c4d; color: #ffffff; }
        QMenu { background: #1b252f; border: 1px solid #344352; padding: 5px; }
        QMenu::item { padding: 6px 28px 6px 12px; border-radius: 3px; }
        QToolBar { background: #151c24; border: none; border-bottom: 1px solid #273441; spacing: 7px; padding: 5px 9px; }
        QToolButton { background: transparent; border: 1px solid transparent; border-radius: 4px; padding: 6px 9px; }
        QToolButton:hover { background: #253442; border-color: #385166; }
        QDockWidget { color: #d9e4ed; font-weight: 600; }
        QDockWidget::title { text-align: left; background: #1a242e; border-bottom: 1px solid #304151; padding: 8px 10px; }
        QDockWidget::close-button, QDockWidget::float-button { margin: 4px; }
        QComboBox { background: #202c37; border: 1px solid #3a4c5c; border-radius: 4px; padding: 6px 9px; min-height: 22px; }
        QComboBox:hover, QComboBox:focus { border-color: #4e9fd0; }
        QComboBox::drop-down { border: 0; width: 24px; }
        QComboBox QAbstractItemView { background: #202c37; border: 1px solid #40576a; selection-background-color: #2b8ac6; }
        QScrollBar:vertical { background: #151c24; width: 10px; margin: 2px; }
        QScrollBar::handle:vertical { background: #405160; border-radius: 4px; min-height: 28px; }
        QSlider::groove:horizontal { height: 4px; border-radius: 2px; background: #344451; }
        QSlider::sub-page:horizontal { background: #2b8ac6; border-radius: 2px; }
        QSlider::handle:horizontal { width: 14px; margin: -5px 0; border-radius: 7px; background: #dbe8f0; }
        QStatusBar { background: #151c24; color: #aab9c5; border-top: 1px solid #273441; }
    """)
