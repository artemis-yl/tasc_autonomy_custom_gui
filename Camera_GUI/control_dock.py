from PySide6.QtWidgets import (
    QDockWidget, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QSlider, QComboBox, QScrollArea, QFrame
)
from PySide6.QtCore import Qt, Signal


class CameraControlDock(QDockWidget):
    """
    Compact camera controls with only the requested settings.
    """

    settings_applied = Signal(str, dict)
    restart_requested = Signal()

    def __init__(self, parent=None):
        super().__init__("Camera Controls", parent)

        self.setAllowedAreas(Qt.AllDockWidgetAreas)
        self.setFeatures(
            QDockWidget.DockWidgetFloatable |
            QDockWidget.DockWidgetMovable |
            QDockWidget.DockWidgetClosable
        )
        self.setMinimumWidth(280)
        self.setMaximumWidth(400)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scroll.setStyleSheet("""
            QScrollArea { border: none; background: #1e1e1e; }
            QScrollBar:vertical {
                background: #2a2a2a;
                width: 12px;
                border-radius: 6px;
            }
            QScrollBar::handle:vertical {
                background: #555555;
                border-radius: 6px;
                min-height: 30px;
            }
            QScrollBar::handle:vertical:hover { background: #777777; }
        """)

        content = QWidget()
        content.setStyleSheet("""
            QWidget { background-color: #1e1e1e; color: #e0e0e0; }
            QLabel { font-size: 13px; margin-top: 8px; }
            QComboBox, QSlider {
                background-color: #2a2a2a;
                border: 1px solid #444444;
                border-radius: 4px;
                padding: 4px;
                min-height: 24px;
            }
            QComboBox::drop-down { border: none; }
            QComboBox QAbstractItemView {
                background-color: #2a2a2a;
                selection-background-color: #2196F3;
            }
        """)

        layout = QVBoxLayout(content)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(8)
        layout.setAlignment(Qt.AlignTop)

        # Camera Selection
        layout.addWidget(QLabel("Active Camera"))
        self.camera_selector = QComboBox()
        self.camera_selector.addItems([
            "Orbbec / Front",
            "WebCam / Back",
            "IP Cam / Top",
            "IR Cam / ARM",
        ])
        layout.addWidget(self.camera_selector)

        line = QFrame()
        line.setFrameShape(QFrame.HLine)
        line.setStyleSheet("color: #444444;")
        layout.addWidget(line)

        # Resolution
        layout.addWidget(QLabel("Resolution"))
        self.res_combo = QComboBox()
        self.res_combo.addItems(["640x480", "1280x720", "1920x1080"])
        layout.addWidget(self.res_combo)

        # Frame Rate
        layout.addWidget(QLabel("Frame Rate"))
        self.fps_combo = QComboBox()
        self.fps_combo.addItems(["15 fps", "30 fps", "60 fps"])
        layout.addWidget(self.fps_combo)

        # Brightness
        layout.addWidget(QLabel("Brightness"))
        self.brightness_value = QLabel("50%")
        self.brightness_value.setStyleSheet("color: #888888; font-size: 11px;")
        layout.addWidget(self.brightness_value)

        self.brightness_slider = QSlider(Qt.Horizontal)
        self.brightness_slider.setRange(0, 100)
        self.brightness_slider.setValue(50)
        layout.addWidget(self.brightness_slider)

        # Bit Rate
        layout.addWidget(QLabel("Bit Rate"))
        self.bitrate_combo = QComboBox()
        self.bitrate_combo.addItems([
            "250 kbps", "500 kbps", "1000 kbps", "1500 kbps", "2000 kbps",
            "3000 kbps", "4000 kbps", "6000 kbps", "8000 kbps", "12000 kbps",
            "16000 kbps", "24000 kbps", "32000 kbps", "50000 kbps", "Uncapped"
        ])
        self.bitrate_combo.setCurrentText("4000 kbps")
        layout.addWidget(self.bitrate_combo)

        # Flip / Mirror
        flip_layout = QHBoxLayout()
        self.flip_h = QPushButton("↔ Flip H")
        self.flip_h.setCheckable(True)
        self.flip_h.setStyleSheet("""
            QPushButton {
                background-color: #2a2a2a;
                border: 1px solid #444444;
                border-radius: 4px;
                padding: 6px;
            }
            QPushButton:checked { background-color: #2196F3; color: white; }
        """)

        self.flip_v = QPushButton("↕ Flip V")
        self.flip_v.setCheckable(True)
        self.flip_v.setStyleSheet(self.flip_h.styleSheet())

        flip_layout.addWidget(self.flip_h)
        flip_layout.addWidget(self.flip_v)
        layout.addLayout(flip_layout)

        layout.addSpacing(20)

        # Apply Button
        self.apply_btn = QPushButton("Apply Settings")
        self.apply_btn.setMinimumHeight(44)
        self.apply_btn.setStyleSheet("""
            QPushButton {
                background-color: #2196F3;
                color: white;
                border: none;
                padding: 10px;
                font-weight: bold;
                font-size: 14px;
                border-radius: 6px;
            }
            QPushButton:hover { background-color: #1976D2; }
            QPushButton:pressed { background-color: #0D47A1; }
            QPushButton:disabled { background-color: #444444; color: #888888; }
        """)
        layout.addWidget(self.apply_btn)

        # Restart Cameras Button
        self.restart_btn = QPushButton("Restart Cameras")
        self.restart_btn.setMinimumHeight(36)
        self.restart_btn.setStyleSheet("""
            QPushButton {
                background-color: #2d89ef;
                color: white;
                border: none;
                padding: 8px;
                font-weight: bold;
                font-size: 13px;
                border-radius: 6px;
            }
            QPushButton:hover { background-color: #1f6fd1; }
            QPushButton:pressed { background-color: #185aab; }
            QPushButton:disabled { background-color: #444444; color: #888888; }
        """)
        layout.addWidget(self.restart_btn)

        layout.addStretch()

        scroll.setWidget(content)
        self.setWidget(scroll)

        # Signals
        self.brightness_slider.valueChanged.connect(
            lambda v: self.brightness_value.setText(f"{v}%")
        )

        self.apply_btn.clicked.connect(self._on_apply)
        self.restart_btn.clicked.connect(self.restart_requested.emit)

    def _on_apply(self):
        """Gather all settings and emit signal."""
        settings = {
            'resolution': self.res_combo.currentText(),
            'fps': self.fps_combo.currentText(),
            'brightness': self.brightness_slider.value(),
            'bitrate': self.bitrate_combo.currentText(),
            'flip_h': self.flip_h.isChecked(),
            'flip_v': self.flip_v.isChecked(),
        }
        camera = self.camera_selector.currentText()
        print(f"[Apply] {camera} → {settings}")
        self.settings_applied.emit(camera, settings)