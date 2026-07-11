# This Python file uses the following encoding: utf-8
import sys
import os
import argparse
from pathlib import Path

from PySide6.QtWidgets import QApplication, QMainWindow
from PySide6.QtQuickWidgets import QQuickWidget
from PySide6.QtCore import Qt, QUrl, QTimer
from PySide6.QtGui import QAction, QPalette, QColor

from camera_dock import CameraDock
from control_dock import CameraControlDock
from telemetry_dock import TelemetryDock


class MainWindow(QMainWindow):
    def __init__(self, source_mode="usb", srt_laptop_uri=None, srt_usb_uri=None):
        super().__init__()

        self.source_mode = source_mode
        self.srt_laptop_uri = srt_laptop_uri
        self.srt_usb_uri = srt_usb_uri

        print("[DEBUG] MainWindow init")
        print(f"[DEBUG] Source mode: {self.source_mode}")

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

        # Restart cameras button
        self.control_dock.restart_requested.connect(self._restart_all_cameras)

        # Telemetry updater
        self._telemetry_timer = QTimer(self)
        self._telemetry_timer.timeout.connect(self._update_telemetry)
        self._telemetry_timer.start(500)

        QTimer.singleShot(0, self._start_cameras)

    def _start_cameras(self):
        print("[DEBUG] 🔥 Starting available cameras...")

        for name, dock in self.camera_docks.items():
            try:
                dock.start()
            except Exception as e:
                print(f"[PIPELINE ERROR] {name}: {e}")

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

        # (dock title / logical camera name, stream_uri).
        # Only the first two have SRT URIs wired to CLI args for now — the
        # other two run in whatever --source mode was passed with no URI,
        # which CameraDock.start() already handles gracefully (prints a
        # [FAIL] message rather than crashing) if source_mode is "srt".
        camera_specs = [
            ("Orbbec / Front", self.srt_laptop_uri),
            ("WebCam / Back", self.srt_usb_uri),
            ("IP Cam / Top", None),
            ("IR Cam / ARM", None),
        ]

        self.camera_docks = {}
        docks = []
        for title, stream_uri in camera_specs:
            dock = CameraDock(
                title,
                title,
                parent=self,
                source_mode=self.source_mode,
                stream_uri=stream_uri,
            )
            self.camera_docks[title] = dock
            docks.append(dock)

        # 2x2 grid:
        #   [0] [1]
        #   [2] [3]
        self.addDockWidget(Qt.LeftDockWidgetArea, docks[0])
        self.addDockWidget(Qt.LeftDockWidgetArea, docks[1])
        self.splitDockWidget(docks[0], docks[1], Qt.Horizontal)

        self.addDockWidget(Qt.LeftDockWidgetArea, docks[2])
        self.splitDockWidget(docks[0], docks[2], Qt.Vertical)

        self.addDockWidget(Qt.LeftDockWidgetArea, docks[3])
        self.splitDockWidget(docks[1], docks[3], Qt.Vertical)

    # ---------------- CONTROL ----------------
    def _setup_control_docks(self):
        self.control_dock = CameraControlDock(self)
        self.addDockWidget(Qt.RightDockWidgetArea, self.control_dock)

        self.telemetry_dock = TelemetryDock(self)
        self.addDockWidget(Qt.BottomDockWidgetArea, self.telemetry_dock)

    # ---------------- MENU ----------------
    def _setup_menu(self):
        view_menu = self.menuBar().addMenu("&View")

        for dock in list(self.camera_docks.values()) + [self.control_dock, self.telemetry_dock]:
            view_menu.addAction(dock.toggleViewAction())

        view_menu.addSeparator()

        reset_action = QAction("Reset Layout", self)
        reset_action.triggered.connect(self._reset_layout)
        view_menu.addAction(reset_action)

    # ---------------- APPLY SETTINGS ----------------
    def _apply_to_camera(self, camera_name, settings):
        dock = self.camera_docks.get(camera_name)
        if dock:
            print(f"[DEBUG] Applying settings to {camera_name}")
            dock.apply_settings(settings)
        else:
            print(f"[WARN] No dock found for camera: {camera_name}")

    # ---------------- TELEMETRY ----------------
    def _update_telemetry(self):
        for name, dock in self.camera_docks.items():
            self.telemetry_dock.update_camera_stats(name, dock.get_stream_stats())

    def _restart_all_cameras(self):
        print("[DEBUG] Restarting all camera connections...")
        self.control_dock.restart_btn.setEnabled(False)

        for dock in self.camera_docks.values():
            dock.stop()

        def _start_again():
            self._start_cameras()
            self.control_dock.restart_btn.setEnabled(True)

        QTimer.singleShot(300, _start_again)

    # ---------------- RESET ----------------
    def _reset_layout(self):
        docks = list(self.camera_docks.values())

        self.addDockWidget(Qt.LeftDockWidgetArea, docks[0])
        self.addDockWidget(Qt.LeftDockWidgetArea, docks[1])
        self.splitDockWidget(docks[0], docks[1], Qt.Horizontal)

        self.addDockWidget(Qt.LeftDockWidgetArea, docks[2])
        self.splitDockWidget(docks[0], docks[2], Qt.Vertical)

        self.addDockWidget(Qt.LeftDockWidgetArea, docks[3])
        self.splitDockWidget(docks[1], docks[3], Qt.Vertical)

        self.addDockWidget(Qt.RightDockWidgetArea, self.control_dock)
        self.addDockWidget(Qt.BottomDockWidgetArea, self.telemetry_dock)

        for dock in docks + [self.control_dock, self.telemetry_dock]:
            dock.setVisible(True)
            dock.setFloating(False)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="TASC camera GUI")
    parser.add_argument("--source", choices=["usb", "srt"], default="usb", help="Camera source type")
    parser.add_argument("--srt-laptop-uri", default="srt://127.0.0.1:9000", help="SRT URI for the first camera slot")
    parser.add_argument("--srt-usb-uri", default="srt://127.0.0.1:9001", help="SRT URI for the second camera slot")
    args = parser.parse_args()

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

    window = MainWindow(
        source_mode=args.source,
        srt_laptop_uri=args.srt_laptop_uri,
        srt_usb_uri=args.srt_usb_uri,
    )
    window.show()

    sys.exit(app.exec())