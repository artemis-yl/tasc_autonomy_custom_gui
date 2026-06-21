from PySide6.QtWidgets import QDockWidget, QWidget, QVBoxLayout, QLabel
from PySide6.QtCore import Qt

from video_widget import GStreamerVideoWidget


class CameraDock(QDockWidget):
    """Individual camera feed as a dockable panel with GStreamer video."""

    def __init__(self, title, camera_name, pipeline_str=None, parent=None):
        super().__init__(title, parent)

        self.setAllowedAreas(Qt.AllDockWidgetAreas)
        self.setFeatures(
            QDockWidget.DockWidgetFloatable |
            QDockWidget.DockWidgetMovable |
            QDockWidget.DockWidgetClosable
        )
        self.setMinimumSize(400, 300)

        self.video_widget = GStreamerVideoWidget(pipeline_str)

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

    def set_source(self, source_type, **kwargs):
        """Configure video source."""
        if source_type == "rtsp":
            self.video_widget.set_rtsp_url(kwargs.get('url'))
        elif source_type == "v4l2":
            self.video_widget.set_v4l2_device(kwargs.get('device', '/dev/video0'))
        elif source_type == "test":
            self.video_widget.set_test_source()
        self.video_widget.play()