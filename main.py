import sys
from pathlib import Path

from PySide6.QtWidgets import QApplication, QMainWindow
from PySide6.QtQuickWidgets import QQuickWidget
from PySide6.QtCore import Qt, QUrl, QTimer, QSettings
from PySide6.QtGui import QAction

from camera_dock import CameraDock
from control_dock import CameraControlDock
from telemetry_dock import TelemetryDock
from layout_presets import LayoutPresetStore
from preset_ui import LayoutPresetToolBar
from builtin_layouts import BUILTIN_LAYOUT_NAMES, apply_builtin_layout
from theme import apply_dark_theme

# (key, camera name, stream port)
CAMERAS = [
    ("front", "Orbbec / Front", "192.168.1.7",   7092),
    ("back",  "WebCam / Back",  "192.168.1.7",   7091),
    ("top",   "IP Cam / Top",   "192.168.1.117", 8554),
    ("arm",   "IR Cam / ARM",   "192.168.1.116", 8554),
]


class MainWindow(QMainWindow):

    def __init__(self):
        super().__init__()
        self.setObjectName("MainWindow")  # required for saveState()/restoreState()
        self.setWindowTitle("TASC Autonomy GUI")
        self.resize(1920, 1080)
        self.setStyleSheet("QMainWindow { background-color: #0d0d0d; }")
        self.setDockOptions(
            QMainWindow.AnimatedDocks |
            QMainWindow.AllowTabbedDocks |
            QMainWindow.AllowNestedDocks
        )
        self.setDockNestingEnabled(True)

        self.settings = QSettings("TASC", "AutonomyGUI")
        self.preset_store = LayoutPresetStore(self.settings)

        self._setup_central_widget()
        self._setup_docks()
        self._setup_toolbar()
        self._setup_menu()

        self.control_dock.settings_applied.connect(self._apply_to_camera)

        self._telemetry_timer = QTimer(self)
        self._telemetry_timer.timeout.connect(self._update_telemetry)
        self._telemetry_timer.start(500)

        QTimer.singleShot(0, self._start_cameras)

    # ------------------------------------------------------------------
    # Setup
    # ------------------------------------------------------------------

    def _setup_central_widget(self):
        self.central_widget = QQuickWidget()
        qml_path = Path(__file__).parent / "Camera_GUI" / "Main.qml"
        self.central_widget.setSource(QUrl.fromLocalFile(str(qml_path)))
        self.central_widget.setResizeMode(QQuickWidget.SizeRootObjectToView)
        self.setCentralWidget(self.central_widget)

    def _setup_docks(self):
        self.camera_docks = {}
        for key, name, ip, _port in CAMERAS:
            dock = CameraDock(name, name, parent=self)
            dock.setObjectName(f"{key}_dock")
            self.camera_docks[key] = dock

        # Attribute aliases so existing references keep working
        self.front_dock = self.camera_docks["front"]
        self.back_dock = self.camera_docks["back"]
        self.top_dock = self.camera_docks["top"]
        self.arm_dock = self.camera_docks["arm"]

        self.front_dock.setMinimumSize(640, 480)
        self.addDockWidget(Qt.LeftDockWidgetArea, self.front_dock)
        for key in ("back", "top", "arm"):
            self.addDockWidget(Qt.BottomDockWidgetArea, self.camera_docks[key])
        self.tabifyDockWidget(self.back_dock, self.top_dock)
        self.tabifyDockWidget(self.back_dock, self.arm_dock)

        self.control_dock = CameraControlDock(self)
        self.control_dock.setObjectName("control_dock")
        self.addDockWidget(Qt.RightDockWidgetArea, self.control_dock)

        self.telemetry_dock = TelemetryDock(self)
        self.telemetry_dock.setObjectName("telemetry_dock")
        self.addDockWidget(Qt.BottomDockWidgetArea, self.telemetry_dock)

        # One registry for layouts, the View menu, and reset
        self.docks = {
            **self.camera_docks,
            "control": self.control_dock,
            "telemetry": self.telemetry_dock,
        }

    def _setup_toolbar(self):
        self.layout_toolbar = LayoutPresetToolBar(
            self,
            store=self.preset_store,
            builtin_names=BUILTIN_LAYOUT_NAMES,
            get_state=self.saveState,
            restore_state=self.restoreState,
            apply_builtin=self._apply_builtin_layout,
        )
        self.addToolBar(self.layout_toolbar)

    def _setup_menu(self):
        view_menu = self.menuBar().addMenu("&View")
        for dock in self.docks.values():
            view_menu.addAction(dock.toggleViewAction())
        view_menu.addSeparator()
        reset_action = QAction("Reset Layout", self)
        reset_action.triggered.connect(self.layout_toolbar.reset)
        view_menu.addAction(reset_action)

    # ------------------------------------------------------------------
    # Layouts
    # ------------------------------------------------------------------

    def _apply_builtin_layout(self, name):
        apply_builtin_layout(self, self.docks, name)

    # ------------------------------------------------------------------
    # Cameras
    # ------------------------------------------------------------------

    def _start_cameras(self):
        print("[DEBUG] 🔥 Starting available cameras...")
        for key, _name, ip, port in CAMERAS:
            self.camera_docks[key].start(ip, port)

    def _apply_to_camera(self, camera_name, settings):
        print(f"[DEBUG] Applying settings to {camera_name}")

    # ------------------------------------------------------------------
    # Telemetry
    # ------------------------------------------------------------------

    def _update_telemetry(self):
        for key, name, ip, _port in CAMERAS:
            self.telemetry_dock.update_camera_stats(
                name, self.camera_docks[key].get_stream_stats()
            )


if __name__ == "__main__":
    app = QApplication(sys.argv)
    apply_dark_theme(app)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
