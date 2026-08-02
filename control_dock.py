from PySide6.QtWidgets import (
    QDockWidget, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QSlider, QComboBox, QScrollArea, QFrame,
    QPushButton, QCheckBox
)
from PySide6.QtCore import Qt, Signal
from control_tcp_client import CameraTcpClient
from control_onvif import ONVIFCameraSettings
import constants as const 


class CameraControlDock(QDockWidget):
    """
    Compact camera controls with only the requested settings.
    """

    settings_applied = Signal(dict)
    stop_requested = Signal(dict)

    def __init__(self, parent=None, tcp_host: str ="127.0.0.1", tcp_port: int = 8080):
        super().__init__("Camera Controls", parent)
    
        self.setAllowedAreas(Qt.AllDockWidgetAreas)
        self.setFeatures(
            QDockWidget.DockWidgetFloatable |
            QDockWidget.DockWidgetMovable |
            QDockWidget.DockWidgetClosable
        )
        self.setMinimumWidth(225)
        self.setMaximumWidth(320)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scroll.setStyleSheet("""
            QScrollArea { border: none; background: #151c24; }
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
            QWidget { background-color: #151c24; color: #dce6ee; }
            QLabel { font-size: 12px; margin-top: 10px; color: #aebfcb; font-weight: 600; }
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
        
        # Controls for USB/TCP and IP/ONVIF ======================================
        self.tcp_host = tcp_host
        self.tcp_port = tcp_port
        self.tcp_client = CameraTcpClient(self)
        
        self.top_onvif_controllers = None
        self.arm_onvif_controllers = None

        # one to connect/disconnect TCP client
        self.tcp_checkbox = QCheckBox(text="USB / TCP")
        layout.addWidget(self.tcp_checkbox)
        self.tcp_checkbox.stateChanged.connect(self.onStateChanged_tcp)
        # one to connect/disconnect onvif top
        self.arm_checkbox = QCheckBox(text="ARM ONVIF")
        layout.addWidget(self.arm_checkbox)
        self.arm_checkbox.stateChanged.connect(self.onStateChanged_arm)
        # one to connect/disconnect onvif top
        self.top_checkbox = QCheckBox(text="TOP ONVIF")
        layout.addWidget(self.top_checkbox)
        self.top_checkbox.stateChanged.connect(self.onStateChanged_top)
        # =========================================================================
        
        
        # Stream
        layout.addWidget(self._section_heading("Stream"))
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
        line.setStyleSheet("color: #314150;")
        layout.addWidget(line)

        # Resolution
        layout.addWidget(QLabel("Resolution"))
        self.res_combo = QComboBox()
        self.res_combo.addItems(["640 x 360", "640 x 480", "1280 x 720", "352 x 288", "720 x 480",])
        layout.addWidget(self.res_combo)

        # Frame Rate
        layout.addWidget(QLabel("Frame Rate (FPS)"))
        self.fps_combo = QComboBox()
        self.fps_combo.addItems(["10", "25", "30"])
        layout.addWidget(self.fps_combo)

        layout.addWidget(QLabel("Bit Rate (kbps)"))
        self.bitrate_combo = QComboBox()
        self.bitrate_combo.addItems([
            "250", "500", "1000", #"1500", "2000",
        ])
        self.bitrate_combo.setCurrentText("500")
        layout.addWidget(self.bitrate_combo)        

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
        self.stop_btn = QPushButton("Stop Selected Stream")
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
        
        self.camera_selector.currentTextChanged.connect(self._update_title)
        self._update_title(self.camera_selector.currentText())

        self.apply_btn.clicked.connect(self._on_apply)
        self.stop_btn.clicked.connect(self.stop_requested)
        
    def onStateChanged_tcp(self):
        if self.tcp_checkbox.isChecked():
            self.tcp_checkbox.setText("USB / TCP - Connected")
            self.tcp_client.connect_to_server(self.tcp_host, self.tcp_port)
        else:
            self.tcp_checkbox.setText("USB / TCP - Disconnected")
            self.tcp_client.disconnect_from_server()
            
    def onStateChanged_arm(self):
        print(">>onStateChanged_arm called")
        if self.arm_checkbox.isChecked():
            self.arm_checkbox.setText("ARM / ONVIF - Connected")
            self.arm_onvif_controllers = ONVIFCameraSettings(
                camera_ip = const.CAMERA_INFO["IP Cam 2 / ARM"]["ip"], 
                onvif_port = const.IP_ONVIF_PORT, 
                username = const.ONVIF_USERNAME, 
                password = const.ONVIF_PASSWORD, 
                profile_index = const.ONVIF_PROFILE
            )
            print(f">>Connected to ARM ONVIF camera at {self.arm_onvif_controllers}")
        else:
            self.arm_checkbox.setText("ARM / ONVIF - Disconnected")
            self.arm_onvif_controllers = None

            
    def onStateChanged_top(self):
        print(">>onStateChanged_top called")
        if self.top_checkbox.isChecked():
            self.top_checkbox.setText("TOP / ONVIF - Connected")
            self.top_onvif_controllers = ONVIFCameraSettings(
                camera_ip = const.CAMERA_INFO["IP Cam / Top"]["ip"], 
                onvif_port = const.IP_ONVIF_PORT, 
                username = const.ONVIF_USERNAME, 
                password = const.ONVIF_PASSWORD, 
                profile_index = const.ONVIF_PROFILE
            )
            print(f">>Connected to TOP ONVIF camera at {self.top_onvif_controllers}")
        else:
            self.top_checkbox.setText("TOP / ONVIF - Disconnected")
            self.top_onvif_controllers = None

    
    def onStateChanged_autoExposure(self):
        if self.autoExposure_checkbox.isChecked():
            self.autoExposure_checkbox.setText("Auto Exposure On")
            self.exposureAutoOn = True
        else:
            self.autoExposure_checkbox.setText("Manual Exposure")
            self.exposureAutoOn = False

    def _section_heading(self, text):
        label = QLabel(text.upper())
        label.setStyleSheet(
            "color: #6fa8c8; font-size: 10px; font-weight: 700; "
            "letter-spacing: 0.8px; margin-top: 14px;"
        )
        return label

    def _update_title(self, camera_name):
        self.setWindowTitle(f"Camera Controls — {camera_name}")

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
            "Orbbec / Front" : "orbbec_color",
            "Webcam / Back" : "back",
            "IP Cam / Top" : "top",
            "IP Cam 2 / ARM" : "arm"
        }
            
        # extract all settings from the GUI
        camera_name = camera_name_convert.get(self.camera_selector.currentText())
        resolution_split = self.res_combo.currentText().split()
        width = int(resolution_split[0])
        height = int(resolution_split[2])
        fps = int(self.fps_combo.currentText())
        bitrate = int(self.bitrate_combo.currentText())
        #max_exposure = self.maxExposureTime_slider.value()
        #min_exposure = self.minExposureTime_slider.value()

        
        # even if command = 'stop' doesn't need the rest, it's fine to have
        if (camera_name) == "orbbec_color" or  (camera_name) == "back":
            settings = {
                'state': command,
                'camera': camera_name,
                'width': width,
                'height': height,
                'fps': fps,
                'bitrate': bitrate,
            
            #    'max_exposure': max_exposure,
            #    'min_exposure': min_exposure,
            #    'flip_h': self.flip_h.isChecked(),
            #    'flip_v': self.flip_v.isChecked(),
            }
            sent_packet = self.tcp_client.send_json(settings)
            if sent_packet:
                print(f"Sent TCP Packet: [{command}] {settings['camera']} → {settings}")
            else:
                print(f"Could not send TCP packet for {camera_name_convert.get( self.camera_selector.currentText())} "
                      f"(socket not connected) → {settings}")

        else:            

            if (camera_name) == "top":
                # onvifmethod.ashdajjas()
                #onvif_camera = self.onvif_controllers["top"]
                self.top_onvif_controllers.change_resolution(width, height)
                self.top_onvif_controllers.change_fps(fps)
                self.top_onvif_controllers.change_bitrate(bitrate)
            elif (camera_name) == "arm":
                self.arm_onvif_controllers.change_resolution(width, height)
                self.arm_onvif_controllers.change_fps(fps)
                self.arm_onvif_controllers.change_bitrate(bitrate)

            #if self.exposureAutoOn:
            #    onvif_camera.set_auto_exposure(min_exposure, max_exposure)
            #else:
            #    onvif_camera.set_manual_exposure(max_exposure)
            print(f"Sent ONVIF Packet to {camera_name}: [{command}] → {{'width': {width}, 'height': {height}, 'fps': {fps}, 'bitrate': {bitrate}}}")



        
