from PySide6.QtWidgets import (
    QDockWidget, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QSlider, QComboBox, QScrollArea, QFrame
)
from PySide6.QtCore import Qt, Signal


class CameraControlDock(QDockWidget):
    """
    Scrollable camera controls with Apply button at the bottom.
    Add as many settings as you want, the scroll area handles overflow.
    """

    settings_applied = Signal(str, dict)  

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
            "IR Cam / ARM",
            "WebCam / Back",
            "IP Cam / Top"
        ])
        layout.addWidget(self.camera_selector)

        line = QFrame()
        line.setFrameShape(QFrame.HLine)
        line.setStyleSheet("color: #444444;")
        layout.addWidget(line)

        # Exposure
        layout.addWidget(QLabel("Exposure"))
        self.exposure_value = QLabel("50%")
        self.exposure_value.setStyleSheet("color: #888888; font-size: 11px;")
        layout.addWidget(self.exposure_value)

        self.exposure_slider = QSlider(Qt.Horizontal)
        self.exposure_slider.setRange(0, 100)
        self.exposure_slider.setValue(50)
        layout.addWidget(self.exposure_slider)

        # Gain
        layout.addWidget(QLabel("Gain"))
        self.gain_value = QLabel("50%")
        self.gain_value.setStyleSheet("color: #888888; font-size: 11px;")
        layout.addWidget(self.gain_value)

        self.gain_slider = QSlider(Qt.Horizontal)
        self.gain_slider.setRange(0, 100)
        self.gain_slider.setValue(50)
        layout.addWidget(self.gain_slider)

        # White Balance
        layout.addWidget(QLabel("White Balance"))
        self.wb_combo = QComboBox()
        self.wb_combo.addItems(["Auto", "Daylight", "Cloudy", "Tungsten", "Fluorescent", "Custom"])
        layout.addWidget(self.wb_combo)

        # Resolution
        layout.addWidget(QLabel("Resolution"))
        self.res_combo = QComboBox()
        self.res_combo.addItems(["640x480", "1280x720", "1920x1080", "2560x1440"])
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

        # Contrast
        layout.addWidget(QLabel("Contrast"))
        self.contrast_value = QLabel("50%")
        self.contrast_value.setStyleSheet("color: #888888; font-size: 11px;")
        layout.addWidget(self.contrast_value)

        self.contrast_slider = QSlider(Qt.Horizontal)
        self.contrast_slider.setRange(0, 100)
        self.contrast_slider.setValue(50)
        layout.addWidget(self.contrast_slider)

        # Saturation
        layout.addWidget(QLabel("Saturation"))
        self.sat_value = QLabel("50%")
        self.sat_value.setStyleSheet("color: #888888; font-size: 11px;")
        layout.addWidget(self.sat_value)

        self.sat_slider = QSlider(Qt.Horizontal)
        self.sat_slider.setRange(0, 100)
        self.sat_slider.setValue(50)
        layout.addWidget(self.sat_slider)

        # Sharpness
        layout.addWidget(QLabel("Sharpness"))
        self.sharp_value = QLabel("50%")
        self.sharp_value.setStyleSheet("color: #888888; font-size: 11px;")
        layout.addWidget(self.sharp_value)

        self.sharp_slider = QSlider(Qt.Horizontal)
        self.sharp_slider.setRange(0, 100)
        self.sharp_slider.setValue(50)
        layout.addWidget(self.sharp_slider)

        # Zoom
        layout.addWidget(QLabel("Digital Zoom"))
        self.zoom_value = QLabel("1.0x")
        self.zoom_value.setStyleSheet("color: #888888; font-size: 11px;")
        layout.addWidget(self.zoom_value)

        self.zoom_slider = QSlider(Qt.Horizontal)
        self.zoom_slider.setRange(10, 40)
        self.zoom_slider.setValue(10)
        layout.addWidget(self.zoom_slider)

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

        layout.addStretch()

        scroll.setWidget(content)
        self.setWidget(scroll)

        # Signals
        self.exposure_slider.valueChanged.connect(
            lambda v: self.exposure_value.setText(f"{v}%")
        )
        self.gain_slider.valueChanged.connect(
            lambda v: self.gain_value.setText(f"{v}%")
        )
        self.brightness_slider.valueChanged.connect(
            lambda v: self.brightness_value.setText(f"{v}%")
        )
        self.contrast_slider.valueChanged.connect(
            lambda v: self.contrast_value.setText(f"{v}%")
        )
        self.sat_slider.valueChanged.connect(
            lambda v: self.sat_value.setText(f"{v}%")
        )
        self.sharp_slider.valueChanged.connect(
            lambda v: self.sharp_value.setText(f"{v}%")
        )
        self.zoom_slider.valueChanged.connect(
            lambda v: self.zoom_value.setText(f"{v/10:.1f}x")
        )

        self.apply_btn.clicked.connect(self._on_apply)

    def _on_apply(self):
        """Gather all settings and emit signal."""
        settings = {
            'exposure': self.exposure_slider.value(),
            'gain': self.gain_slider.value(),
            'white_balance': self.wb_combo.currentText(),
            'resolution': self.res_combo.currentText(),
            'fps': self.fps_combo.currentText(),
            'brightness': self.brightness_slider.value(),
            'contrast': self.contrast_slider.value(),
            'saturation': self.sat_slider.value(),
            'sharpness': self.sharp_slider.value(),
            'zoom': self.zoom_slider.value() / 10.0,
            'flip_h': self.flip_h.isChecked(),
            'flip_v': self.flip_v.isChecked(),
        }
        camera = self.camera_selector.currentText()
        print(f"[Apply] {camera} → {settings}")
        self.settings_applied.emit(camera, settings)