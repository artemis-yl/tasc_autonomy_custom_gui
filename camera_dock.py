from PySide6.QtWidgets import QDockWidget, QWidget, QVBoxLayout, QLabel
from PySide6.QtCore import Qt
from video_widget import GStreamerVideoWidget

class CameraDock(QDockWidget):
    # add more paramters to set initial/minimum window size 
    def __init__(self, title, camera_name, parent=None):
        super().__init__(title, parent)
        self.camera_name = camera_name
        self.setAllowedAreas(Qt.AllDockWidgetAreas)
        self.setFeatures(
            QDockWidget.DockWidgetFloatable |
            QDockWidget.DockWidgetMovable |
            QDockWidget.DockWidgetClosable
        )
        self.setMinimumSize(400, 300)
        
        self.video_widget = GStreamerVideoWidget()
        container = QWidget()
        layout = QVBoxLayout(container)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        header = QLabel(self.camera_name)
        header.setStyleSheet("""
            QLabel {
                background-color: #2a2a2a;
                color: #ffffff;
                padding: 4px 8px;
                font-weight: bold;
                font-size: 12px;
            }
        """)
        header.setMaximumHeight(28)
        
        layout.addWidget(header)
        layout.addWidget(self.video_widget, 1)
        self.setWidget(container)

    def start(self, port: int):
        print(f"[DEBUG] CameraDock START: {self.camera_name} on Port {port}")
        try:
            self.video_widget.start(port)
        except Exception as e:
            print(f"[PIPELINE ERROR] {self.camera_name}: {e}")
