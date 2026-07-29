import sys

from PySide6.QtWidgets import QApplication, QMainWindow, QMessageBox
from PySide6.QtCore import Qt, QTimer, QSettings
from PySide6.QtGui import QAction, QGuiApplication, QKeySequence

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
        self.setWindowTitle("TASC Autonomy | Camera Console")
        # Start within the usable desktop area rather than assuming a 1080p panel.
        available = QGuiApplication.primaryScreen().availableGeometry()
        self.resize(
            min(1600, int(available.width() * 0.94)),
            min(960, int(available.height() * 0.90)),
        )
        self.setDockOptions(
            QMainWindow.AnimatedDocks |
            QMainWindow.AllowTabbedDocks |
            QMainWindow.AllowNestedDocks
        )
        self.setDockNestingEnabled(True)

        self.settings = QSettings("TASC", "AutonomyGUI")
        self.preset_store = LayoutPresetStore(self.settings)

        self._setup_docks()
        self._setup_toolbar()
        self._setup_menu()

        self.control_dock.settings_applied.connect(self._apply_to_camera)

        self._telemetry_timer = QTimer(self)
        self._telemetry_timer.timeout.connect(self._update_telemetry)
        self._telemetry_timer.start(500)

        QTimer.singleShot(0, self._start_cameras)
        QTimer.singleShot(0, lambda: self._apply_builtin_layout("Front Focus"))

    # ------------------------------------------------------------------
    # Setup
    # ------------------------------------------------------------------

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

        self.front_dock.setMinimumSize(480, 300)
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

    def _setup_menu(self):
        self.layout_menu = self.menuBar().addMenu("&Layouts")
        self.layout_menu.aboutToShow.connect(self._rebuild_layout_menu)
        self._layout_actions = {}
        for index, name in enumerate(BUILTIN_LAYOUT_NAMES, start=1):
            action = QAction(name, self)
            action.setShortcut(QKeySequence(f"Ctrl+{index}"))
            action.setShortcutContext(Qt.WindowShortcut)
            action.triggered.connect(
                lambda checked=False, layout_name=name: self._apply_builtin_layout(layout_name)
            )
            self.addAction(action)
            self._layout_actions[name] = action

        view_menu = self.menuBar().addMenu("&View")
        for dock in self.docks.values():
            view_menu.addAction(dock.toggleViewAction())
        view_menu.addSeparator()
        reset_action = QAction("Reset Layout", self)
        reset_action.triggered.connect(self.layout_toolbar.reset)
        view_menu.addAction(reset_action)

    def _rebuild_layout_menu(self):
        """Build a compact menu-bar home for layouts and stored presets."""
        menu = self.layout_menu
        menu.clear()

        for name in BUILTIN_LAYOUT_NAMES:
            menu.addAction(self._layout_actions[name])

        menu.addSeparator()
        saved_menu = menu.addMenu("Saved Layouts")
        found_saved = False
        for scope in (LayoutPresetStore.SHARED, LayoutPresetStore.LOCAL):
            for name in self.preset_store.names(scope):
                action = saved_menu.addAction(name)
                action.setToolTip(f"{scope.title()} saved layout")
                action.triggered.connect(
                    lambda checked=False, n=name, s=scope: self.layout_toolbar._restore(n, s)
                )
                found_saved = True
        if not found_saved:
            placeholder = saved_menu.addAction("No saved layouts")
            placeholder.setEnabled(False)

        delete_menu = menu.addMenu("Delete Saved Layout")
        found_deletable = False
        for scope in (LayoutPresetStore.SHARED, LayoutPresetStore.LOCAL):
            for name in self.preset_store.names(scope):
                action = delete_menu.addAction(name)
                action.triggered.connect(
                    lambda checked=False, n=name, s=scope: self._delete_saved_layout(n, s)
                )
                found_deletable = True
        if not found_deletable:
            placeholder = delete_menu.addAction("No saved layouts")
            placeholder.setEnabled(False)

        menu.addSeparator()
        save_action = menu.addAction("Save Current Layout as Preset...")
        save_action.triggered.connect(self.layout_toolbar._save_current)

    def _delete_saved_layout(self, name, scope):
        where = "the shared project presets" if scope == LayoutPresetStore.SHARED else "this computer"
        answer = QMessageBox.question(
            self,
            "Delete Saved Layout",
            f'Delete the saved layout "{name}" from {where}?',
            QMessageBox.Yes | QMessageBox.No,
        )
        if answer == QMessageBox.Yes:
            self.preset_store.delete(name, scope)
            self.layout_toolbar.rebuild(select=BUILTIN_LAYOUT_NAMES[0])

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
