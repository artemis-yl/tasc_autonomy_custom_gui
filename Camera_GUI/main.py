# This Python file uses the following encoding: utf-8
import sys
import os
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

        print("[DEBUG] MainWindow init")

        self.setWindowTitle("TASC Autonomy GUI")
        self.resize(1920, 1080)
        self.setStyleSheet("QMainWindow { background-color: #0d0d0d; }")

        self.setDockOptions(
            QMainWindow.AnimatedDocks |
            QMainWindow.AllowTabbedDocks |
            QMainWindow.AllowNestedDocks
        )
        self.setDockNestingEnabled(True)

        # Central workspace
        self._setup_central_widget()

        # Camera docks with video
        self._setup_camera_docks()

        # Control & telemetry
        self._setup_control_docks()

        # Menu
        self._setup_menu()

        # Connect Apply to all cameras
        self.control_dock.settings_applied.connect(self._apply_to_camera)

        # Telemetry updater
        self._telemetry_timer = QTimer(self)
        self._telemetry_timer.timeout.connect(self._update_telemetry)
        self._telemetry_timer.start(1000)

        
        QTimer.singleShot(0, self._start_cameras)


    def _start_cameras(self):
        print("[DEBUG] 🔥 Starting all cameras...")

        camera_list = [
            self.front_dock,
            self.back_dock,
            self.top_dock,
            self.arm_dock,
        ]

        results = []

        for dock in camera_list:
            try:
                result = dock.start()
                results.append(result)

            except Exception as e:
                results.append({
                    "name": dock.camera_name,
                    "found": False,
                    "index": None,
                    "error": str(e)
                })

    # ---------------- CENTRAL ----------------
    def _setup_central_widget(self):
        self.central_widget = QQuickWidget()
        qml_path = Path(__file__).parent / "Camera_GUI" / "Main.qml"
        self.central_widget.setSource(QUrl.fromLocalFile(str(qml_path)))
        self.central_widget.setResizeMode(QQuickWidget.SizeRootObjectToView)
        self.setCentralWidget(self.central_widget)

    # ---------------- CAMERAS ----------------
    def _setup_camera_docks(self):
        print("[DEBUG] Setting up camera docks")

        self.front_dock = CameraDock("Front Camera", "Orbbec / Front", parent=self)
        self.front_dock.setMinimumSize(640, 480)
        self.addDockWidget(Qt.LeftDockWidgetArea, self.front_dock)

        self.back_dock = CameraDock("Back Camera", "WebCam / Back", parent=self)
        self.addDockWidget(Qt.BottomDockWidgetArea, self.back_dock)

        self.top_dock = CameraDock("Top Camera", "IP Cam / Top", parent=self)
        self.addDockWidget(Qt.BottomDockWidgetArea, self.top_dock)

        self.arm_dock = CameraDock("Arm Camera", "IR Cam / ARM", parent=self)
        self.addDockWidget(Qt.BottomDockWidgetArea, self.arm_dock)

        self.tabifyDockWidget(self.back_dock, self.top_dock)
        self.tabifyDockWidget(self.back_dock, self.arm_dock)

    # ---------------- CONTROL ----------------
    def _setup_control_docks(self):
        self.control_dock = CameraControlDock(self)
        self.addDockWidget(Qt.RightDockWidgetArea, self.control_dock)

        self.telemetry_dock = TelemetryDock(self)
        self.addDockWidget(Qt.BottomDockWidgetArea, self.telemetry_dock)

    # ---------------- MENU ----------------
    def _setup_menu(self):
        view_menu = self.menuBar().addMenu("&View")

        for dock in [
            self.front_dock,
            self.back_dock,
            self.top_dock,
            self.arm_dock,
            self.control_dock,
            self.telemetry_dock,
        ]:
            view_menu.addAction(dock.toggleViewAction())

        view_menu.addSeparator()

        reset_action = QAction("Reset Layout", self)
        reset_action.triggered.connect(self._reset_layout)
        view_menu.addAction(reset_action)

    # ---------------- APPLY SETTINGS ----------------
    def _apply_to_camera(self, camera_name, settings):
        dock_map = {
            "Orbbec / Front": self.front_dock,
            "WebCam / Back": self.back_dock,
            "IP Cam / Top": self.top_dock,
            "IR Cam / ARM": self.arm_dock,
        }

        dock = dock_map.get(camera_name)
        if dock:
            print(f"[DEBUG] Applying settings to {camera_name}")
            # TODO: pass to backend

    # ---------------- TELEMETRY ----------------
    def _update_telemetry(self):
        import random
        self.telemetry_dock.update_stats(
            fps=random.uniform(28, 31),
            latency=random.uniform(15, 45),
            bitrate=random.uniform(2000, 4500),
            dropped=random.randint(0, 3),
            status="Running"
        )

    # ---------------- RESET ----------------
    def _reset_layout(self):
        self.addDockWidget(Qt.LeftDockWidgetArea, self.front_dock)
        self.addDockWidget(Qt.BottomDockWidgetArea, self.back_dock)
        self.addDockWidget(Qt.BottomDockWidgetArea, self.top_dock)
        self.addDockWidget(Qt.BottomDockWidgetArea, self.arm_dock)
        self.addDockWidget(Qt.RightDockWidgetArea, self.control_dock)
        self.addDockWidget(Qt.BottomDockWidgetArea, self.telemetry_dock)

        self.tabifyDockWidget(self.back_dock, self.top_dock)
        self.tabifyDockWidget(self.back_dock, self.arm_dock)

        for dock in [
            self.front_dock,
            self.back_dock,
            self.top_dock,
            self.arm_dock,
            self.control_dock,
            self.telemetry_dock,
        ]:
            dock.setVisible(True)
            dock.setFloating(False)



if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle("Fusion")

    print("[DEBUG] App starting")

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