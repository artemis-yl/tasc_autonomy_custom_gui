from PySide6.QtWidgets import QDockWidget, QWidget, QVBoxLayout, QLabel
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
            QLabel { font-size: 13px; padding: 2px; }
        """)
        layout = QVBoxLayout(container)
        layout.setContentsMargins(12, 12, 12, 12)

        self.fps_label = QLabel("FPS: --")
        self.latency_label = QLabel("Latency: -- ms")
        self.bitrate_label = QLabel("Bitrate: -- kbps")
        self.dropped_label = QLabel("Dropped: 0")
        self.status_label = QLabel("Status: Idle")
        self.status_label.setStyleSheet("color: #4CAF50; font-weight: bold;")

        layout.addWidget(QLabel("=== Stream Stats ==="))
        layout.addWidget(self.fps_label)
        layout.addWidget(self.latency_label)
        layout.addWidget(self.bitrate_label)
        layout.addWidget(self.dropped_label)
        layout.addWidget(self.status_label)
        layout.addStretch()

        container.setLayout(layout)
        self.setWidget(container)

    def update_stats(self, fps=None, latency=None, bitrate=None, dropped=None, status=None):
        if fps is not None:
            self.fps_label.setText(f"FPS: {fps:.1f}")
        if latency is not None:
            self.latency_label.setText(f"Latency: {latency:.1f} ms")
        if bitrate is not None:
            self.bitrate_label.setText(f"Bitrate: {bitrate:.1f} kbps")
        if dropped is not None:
            self.dropped_label.setText(f"Dropped: {dropped}")
        if status is not None:
            self.status_label.setText(f"Status: {status}")
            color = "#4CAF50" if status == "Running" else "#FF9800" if status == "Buffering" else "#F44336"
            self.status_label.setStyleSheet(f"color: {color}; font-weight: bold;")