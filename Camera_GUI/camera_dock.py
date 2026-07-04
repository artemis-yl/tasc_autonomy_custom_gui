from PySide6.QtWidgets import QDockWidget, QWidget, QVBoxLayout, QLabel
from PySide6.QtCore import Qt

from video_widget import GStreamerVideoWidget
from camera_manager import CameraManager


class CameraDock(QDockWidget):
    """Individual camera feed as a dockable panel with GStreamer video."""

    def __init__(self, title, camera_name, parent=None):
        super().__init__(title, parent)

        self.camera_name = camera_name
        self.camera_manager = CameraManager()

        self.setAllowedAreas(Qt.AllDockWidgetAreas)
        self.setFeatures(
            QDockWidget.DockWidgetFloatable |
            QDockWidget.DockWidgetMovable |
            QDockWidget.DockWidgetClosable
        )
        self.setMinimumSize(400, 300)

        # Video widget
        self.video_widget = GStreamerVideoWidget()

        container = QWidget()
        layout = QVBoxLayout(container)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        header = QLabel(camera_name)
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


    def start(self):
        print(f"[DEBUG] CameraDock START: {self.camera_name}")

        device_index = self.camera_manager.resolve_index(self.camera_name)

        if device_index is None:
            print(f"[FAIL] {self.camera_name} (no device index resolved)")
            return

        print(f"[DEBUG] {self.camera_name} → device index {device_index}")

        try:
        
            self.video_widget.start(device_index)
            print(f"[SUCCESS] Video widget started for {self.camera_name}")
        except Exception as e:
            print(f"[PIPELINE ERROR] {self.camera_name}: {e}")