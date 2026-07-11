from PySide6.QtWidgets import QDockWidget, QWidget, QVBoxLayout, QLabel, QSizePolicy
from PySide6.QtCore import Qt

from video_widget import GStreamerVideoWidget
from camera_manager import CameraManager


class CameraDock(QDockWidget):
    """Individual camera feed as a dockable panel with GStreamer video."""

    def __init__(self, title, camera_name, parent=None, source_mode="usb", stream_uri=None):
        super().__init__(title, parent)

        self.camera_name = camera_name
        self.source_mode = source_mode
        self.stream_uri = stream_uri
        self.camera_manager = CameraManager()
        self._latest_stats = {
            "fps": None,
            "latency_ms": None,
            "bitrate_kbps": None,
            "dropped": 0,
            "status": "Idle",
            "frames": 0,
        }

        self.setAllowedAreas(Qt.AllDockWidgetAreas)
        self.setFeatures(
            QDockWidget.DockWidgetFloatable |
            QDockWidget.DockWidgetMovable |
            QDockWidget.DockWidgetClosable
        )
        self.setMinimumSize(320, 240)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        # Video widget
        self.video_widget = GStreamerVideoWidget(stats_callback=self._on_stats_update)
        self.video_widget.setMinimumSize(320, 240)
        self.video_widget.setMaximumSize(800, 450)
        self.video_widget.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)

        container = QWidget()
        layout = QVBoxLayout(container)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        layout.setAlignment(Qt.AlignCenter)

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

    def _on_stats_update(self, stats):
        self._latest_stats = stats

    def get_stream_stats(self):
        return dict(self._latest_stats)

    def stop(self):
        self.video_widget.stop()

    def apply_settings(self, settings):
        self._current_settings = dict(settings)
        can_restart_usb = hasattr(self, "_device_index") and self._device_index is not None
        can_restart_srt = self.source_mode == "srt" and bool(self.stream_uri)
        if can_restart_usb or can_restart_srt:
            self.video_widget.stop()
            self.video_widget.start(
                device_index=getattr(self, "_device_index", None),
                settings=self._current_settings,
                source_mode=self.source_mode,
                stream_uri=self.stream_uri,
            )


    def start(self):
        print(f"[DEBUG] CameraDock START: {self.camera_name}")

        if self.source_mode == "srt":
            if not self.stream_uri:
                print(f"[FAIL] {self.camera_name} (no SRT URI provided)")
                return

            print(f"[DEBUG] {self.camera_name} → SRT URI {self.stream_uri}")
            try:
                current_settings = getattr(self, "_current_settings", None)
                self.video_widget.start(
                    device_index=None,
                    settings=current_settings,
                    source_mode="srt",
                    stream_uri=self.stream_uri,
                )
                print(f"[SUCCESS] Video widget started for {self.camera_name}")
            except Exception as e:
                print(f"[PIPELINE ERROR] {self.camera_name}: {e}")
            return

        device_index = self.camera_manager.resolve_index(self.camera_name)
        self._device_index = device_index

        if device_index is None:
            print(f"[FAIL] {self.camera_name} (no device index resolved)")
            return

        print(f"[DEBUG] {self.camera_name} → device index {device_index}")

        try:
            current_settings = getattr(self, "_current_settings", None)
            self.video_widget.start(
                device_index=device_index,
                settings=current_settings,
                source_mode="usb",
                stream_uri=None,
            )
            print(f"[SUCCESS] Video widget started for {self.camera_name}")
        except Exception as e:
            print(f"[PIPELINE ERROR] {self.camera_name}: {e}")