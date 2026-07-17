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

        self._start_error = None  # last start() failure, for telemetry

    def start(self, ip: str, port: int):
        print(f"[DEBUG] CameraDock START: {self.camera_name} on Port {ip}:{port}")
        self._start_error = None
        try:
            self.video_widget.start(ip, port)
        except Exception as e:
            self._start_error = str(e)
            print(f"[PIPELINE ERROR] {self.camera_name}: {e}")

    def get_stream_stats(self):

        if self._start_error is not None:
            state = "Error"
        elif getattr(self.video_widget, "pipeline", None) is not None:
            state = "Running"
        else:
            state = "Idle"

        stats = {"state": state, "fps": None, "resolution": None}

        # Real FPS/resolution if video_widget has the (optional) stats hook
        get_stats = getattr(self.video_widget, "get_stats", None)
        if callable(get_stats):
            hook_stats = get_stats()
            if hook_stats:
                stats.update(hook_stats)

        return stats