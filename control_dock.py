from PySide6.QtWidgets import (
    QDockWidget, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QSlider, QComboBox, QScrollArea, QFrame
)
from PySide6.QtCore import Qt, Signal


class CameraControlDock(QDockWidget):
    """
    Compact camera controls with only the requested settings.
    """

    settings_applied = Signal(dict)
    stop_requested = Signal(dict)

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
            "Webcam / Back",
            "IP Cam / Top",
            "IP Cam 2 / ARM",
        ])
        layout.addWidget(self.camera_selector)

        line = QFrame()
        line.setFrameShape(QFrame.HLine)
        line.setStyleSheet("color: #444444;")
        layout.addWidget(line)

        # Resolution
        layout.addWidget(QLabel("Resolution"))
        self.res_combo = QComboBox()
        self.res_combo.addItems(["640 x 360", "640 x 480", "1280 x 720"])
        layout.addWidget(self.res_combo)

        # Frame Rate
        layout.addWidget(QLabel("Frame Rate (FPS)"))
        self.fps_combo = QComboBox()
        self.fps_combo.addItems(["10", "25", "30"])
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
        layout.addWidget(QLabel("Bit Rate (kbps"))
        self.bitrate_combo = QComboBox()
        self.bitrate_combo.addItems([
            "250", "500", "1000", #"1500", "2000",
        ])
        self.bitrate_combo.setCurrentText("500 kbps")
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
        self.apply_btn = QPushButton("Apply Settings / Play Stream")
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

        # Stop Cameras Button
        self.stop_btn = QPushButton("Stop Camera Stream")
        self.stop_btn.setMinimumHeight(36)
        self.stop_btn.setStyleSheet("""
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
        layout.addWidget(self.stop_btn)

        layout.addStretch()

        scroll.setWidget(content)
        self.setWidget(scroll)

        # Signals
        self.brightness_slider.valueChanged.connect(
            lambda v: self.brightness_value.setText(f"{v}%")
        )

        self.apply_btn.clicked.connect(self._on_apply)
        self.stop_btn.clicked.connect(self.stop_requested)
        
        
    # Both buttons end up sending a JSON message, it is just that their command differs
    def _on_apply(self):
        """Gather all settings and emit signal."""
        self.send_message('play')
        
        # do we need to emit???
        #self._on_apply.emit(camera, settings)
        
    def stop_requested(self):
        self.send_message('stop')
        
        # do we need to emit???
        #self.stop_requested.emit(camera, settings)
        
    def send_message(self, command):
        # convert camera_select names to static names, as needed
        camera_name_convert = {
            "Orbbec / Front" : "orbbec_color_cam",
            "Webcam / Back" : "back_web_cam",
            "IP Cam / Top" : "top",
            "IP Cam 2 / ARM" : "arm"
        }
            
        # extract width and height from resolution -ex) 1280 x 720
        resolution_split = self.res_combo.currentText().split()
        width = int(resolution_split[0])
        height = int(resolution_split[2])

        # even if command = 'stop' doesn't need the rest, it's fine to have
        settings = {
            'state': command,
            'camera': camera_name_convert.get( self.camera_selector.currentText() ),
            'width': width,
            'height': height,
            'fps': int(self.fps_combo.currentText()),
            'bitrate': int(self.bitrate_combo.currentText()),
        #    'brightness': self.brightness_slider.value(),
        #    'flip_h': self.flip_h.isChecked(),
        #    'flip_v': self.flip_v.isChecked(),
        }
        print(f"[{command}] {settings['camera']} → {settings}")

        
