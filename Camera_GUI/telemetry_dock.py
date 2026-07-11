from PySide6.QtWidgets import QDockWidget, QWidget, QVBoxLayout, QLabel, QFrame
from PySide6.QtCore import Qt


class TelemetryDock(QDockWidget):
    """Telemetry / status readouts."""

    def __init__(self, parent=None):
        super().__init__("Telemetry", parent)

        self.setAllowedAreas(
            Qt.LeftDockWidgetArea |
            Qt.RightDockWidgetArea |
            Qt.BottomDockWidgetArea
        )
        self.setMinimumHeight(140)

        container = QWidget()
        container.setStyleSheet("""
            QWidget { background-color: #1e1e1e; color: #e0e0e0; }
            QLabel { font-size: 12px; padding: 1px; }
        """)
        self._layout = QVBoxLayout(container)
        self._layout.setContentsMargins(10, 10, 10, 10)
        self._layout.setSpacing(6)

        self._sections = {}

        self.summary_label = QLabel("Live stream stats")
        self.summary_label.setStyleSheet("font-weight: bold; font-size: 13px;")
        self._layout.addWidget(self.summary_label)
        self._layout.addStretch()

        self.setWidget(container)

    def _ensure_camera_section(self, camera_name):
        if camera_name in self._sections:
            return self._sections[camera_name]

        frame = QFrame()
        frame.setFrameShape(QFrame.StyledPanel)
        frame.setStyleSheet("QFrame { border: 1px solid #333333; border-radius: 5px; padding: 4px; }")
        section_layout = QVBoxLayout(frame)
        section_layout.setContentsMargins(6, 6, 6, 6)
        section_layout.setSpacing(2)

        title = QLabel(camera_name)
        title.setStyleSheet("font-weight: bold; font-size: 12px;")

        status_label = QLabel("FPS: -- | Lat: -- ms | Bit: -- kbps | Drop: 0 | Idle")
        status_label.setStyleSheet("color: #FF9800; font-size: 10px;")
        status_label.setFixedWidth(220)  # hard cap so long values can't push neighboring docks
        status_label.setWordWrap(True)

        section_layout.addWidget(title)
        section_layout.addWidget(status_label)

        self._layout.insertWidget(self._layout.count() - 1, frame)
        section = {
            "frame": frame,
            "status_label": status_label,
        }
        self._sections[camera_name] = section
        return section

    def update_camera_stats(self, camera_name, stats):
        section = self._ensure_camera_section(camera_name)

        fps = stats.get("fps")
        latency = stats.get("latency_ms")
        bitrate = stats.get("bitrate_kbps")
        dropped = stats.get("dropped")
        status = stats.get("status")

        section["status_label"].setText(
            (
                f"FPS: {fps:.1f}" if fps is not None else "FPS: --"
            ) + (
                f" | Lat: {latency:.1f} ms" if latency is not None else " | Lat: -- ms"
            ) + (
                f" | Bit: {bitrate:.1f} kbps" if bitrate is not None
                else " | Bit: Uncapped" if bitrate is None and stats.get("bitrate_kbps", "unset") is None
                else " | Bit: -- kbps"
            ) + (
                f" | Drop: {dropped if dropped is not None else 0}"
            ) + (
                f" | {status or 'Idle'}"
            )
        )
        color = "#4CAF50" if status == "Running" else "#FF9800" if status == "Buffering" else "#F44336"
        section["status_label"].setStyleSheet(f"color: {color}; font-weight: bold; font-size: 10px;")

    def update_stats(self, fps=None, latency=None, bitrate=None, dropped=None, status=None):
        self.update_camera_stats("Stream", {
            "fps": fps,
            "latency_ms": latency,
            "bitrate_kbps": bitrate,
            "dropped": dropped,
            "status": status,
        })