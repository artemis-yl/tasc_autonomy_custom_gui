import sys
from pathlib import Path
from PySide6.QtWidgets import QApplication, QMainWindow
from PySide6.QtQuickWidgets import QQuickWidget
from PySide6.QtCore import Qt, QUrl, QTimer
from PySide6.QtGui import QAction, QPalette, QColor
from camera_dock import CameraDock
from control_dock import CameraControlDock
from telemetry_dock import TelemetryDock

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("TASC Autonomy GUI")
        self.resize(1920, 1080)
        self.setStyleSheet("QMainWindow { background-color: #0d0d0d; }")
        self.setDockOptions(
            QMainWindow.AnimatedDocks |
            QMainWindow.AllowTabbedDocks |
            QMainWindow.AllowNestedDocks
        )
        self.setDockNestingEnabled(True)
        
        self._setup_central_widget()
        self._setup_camera_docks()
        self._setup_control_docks()
        self._setup_menu()
        
        self.control_dock.settings_applied.connect(self._apply_to_camera)
        
        self._telemetry_timer = QTimer(self)
        self._telemetry_timer.timeout.connect(self._update_telemetry)
        self._telemetry_timer.start(1000)
        
        QTimer.singleShot(0, self._start_cameras)

    def _start_cameras(self):
        print("[DEBUG] 🔥 Subscribing to network video streams...")
        self.front_dock.start(ip="192.168.1.7", port=7092) # usb cam on jetson
        self.back_dock.start(ip="192.168.1.7", port=7091) # usb cam on jetson
        self.top_dock.start(ip="192.168.1.117", port=8554) # ip cam w/ its own IP
        self.arm_dock.start(ip="192.168.1.116", port=8554) # ip cam w/ its own IP

    def _setup_central_widget(self):
        self.central_widget = QQuickWidget()
        qml_path = Path(__file__).parent / "Camera_GUI" / "Main.qml"
        self.central_widget.setSource(QUrl.fromLocalFile(str(qml_path)))
        self.central_widget.setResizeMode(QQuickWidget.SizeRootObjectToView)
        self.setCentralWidget(self.central_widget)

    def _setup_camera_docks(self):
        self.front_dock = CameraDock("Front Camera", "Orbbec / Front (Port 5001)", parent=self)
        self.front_dock.setMinimumSize(640, 480)
        self.addDockWidget(Qt.LeftDockWidgetArea, self.front_dock)
        
        self.back_dock = CameraDock("Back Camera", "WebCam / Back (Port 5002)", parent=self)
        self.addDockWidget(Qt.BottomDockWidgetArea, self.back_dock)
        
        self.top_dock = CameraDock("Top Camera", "IP Cam / Top (Port 5003)", parent=self)
        self.addDockWidget(Qt.BottomDockWidgetArea, self.top_dock)
        
        self.arm_dock = CameraDock("Arm Camera", "IR Cam / ARM (Port 5004)", parent=self)
        self.addDockWidget(Qt.BottomDockWidgetArea, self.arm_dock)
        
        self.tabifyDockWidget(self.back_dock, self.top_dock)
        self.tabifyDockWidget(self.back_dock, self.arm_dock)

    def _setup_control_docks(self):
        self.control_dock = CameraControlDock(self)
        self.addDockWidget(Qt.RightDockWidgetArea, self.control_dock)
        self.telemetry_dock = TelemetryDock(self)
        self.addDockWidget(Qt.BottomDockWidgetArea, self.telemetry_dock)

    def _setup_menu(self):
        view_menu = self.menuBar().addMenu("&View")
        for dock in [self.front_dock, self.back_dock, self.top_dock, self.arm_dock, self.control_dock, self.telemetry_dock]:
            view_menu.addAction(dock.toggleViewAction())
        view_menu.addSeparator()
        reset_action = QAction("Reset Layout", self)
        reset_action.triggered.connect(self._reset_layout)
        view_menu.addAction(reset_action)

    def _apply_to_camera(self, camera_name, settings):
        print(f"[DEBUG] Applying settings to {camera_name}")

    def _update_telemetry(self):
        import random
        self.telemetry_dock.update_stats(
            fps=random.uniform(28, 31),
            latency=random.uniform(15, 45),
            bitrate=random.uniform(2000, 4500),
            dropped=random.randint(0, 3),
            status="Running"
        )

    def _reset_layout(self):
        self.addDockWidget(Qt.LeftDockWidgetArea, self.front_dock)
        self.addDockWidget(Qt.BottomDockWidgetArea, self.back_dock)
        self.addDockWidget(Qt.BottomDockWidgetArea, self.top_dock)
        self.addDockWidget(Qt.BottomDockWidgetArea, self.arm_dock)
        self.addDockWidget(Qt.RightDockWidgetArea, self.control_dock)
        self.addDockWidget(Qt.BottomDockWidgetArea, self.telemetry_dock)
        self.tabifyDockWidget(self.back_dock, self.top_dock)
        self.tabifyDockWidget(self.back_dock, self.arm_dock)
        for dock in [self.front_dock, self.back_dock, self.top_dock, self.arm_dock, self.control_dock, self.telemetry_dock]:
            dock.setVisible(True)
            dock.setFloating(False)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    palette = QPalette()
    palette.setColor(QPalette.Window, QColor("#0d0d0d"))
    palette.setColor(QPalette.WindowText, QColor("#e0e0e0"))
    palette.setColor(QPalette.Base, QColor("#1e1e1e"))
    palette.setColor(QPalette.AlternateBase, QColor("#2a2a2a"))
    palette.setColor(QPalette.ToolTipBase, QColor("#0d0d0d"))
    palette.setColor(QPalette.ToolTipText, QColor("#e0e0e0"))
    palette.setColor(QPalette.Text, QColor("#e0e0e0"))
    palette.setColor(QPalette.Button, QColor("#2a2a2a"))
    palette.setColor(QPalette.ButtonText, QColor("#e0e0e0"))
    palette.setColor(QPalette.Highlight, QColor("#2196F3"))
    palette.setColor(QPalette.HighlightedText, QColor("#ffffff"))
    app.setPalette(palette)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
