"""Hardcoded built-in camera-dock arrangements.

Each layout is a function taking ``(window, docks)``, where ``docks``
maps short keys ("front", "back", "top", "arm", "control", "telemetry")
to QDockWidget instances. BUILTIN_LAYOUTS preserves display order.
"""

from PySide6.QtCore import Qt


def _add_right_sidebar(w, d):
    """Dock controls and telemetry as one consistently sized right sidebar."""
    w.addDockWidget(Qt.RightDockWidgetArea, d["control"])
    w.splitDockWidget(d["control"], d["telemetry"], Qt.Vertical)
    # Keep telemetry compact and make both sidebar panels share one width.
    w.resizeDocks([d["control"], d["telemetry"]], [70, 30], Qt.Vertical)


def _quad_grid(w, d):
    w.addDockWidget(Qt.LeftDockWidgetArea, d["front"])
    w.splitDockWidget(d["front"], d["back"], Qt.Horizontal)
    w.splitDockWidget(d["front"], d["top"], Qt.Vertical)
    w.splitDockWidget(d["back"], d["arm"], Qt.Vertical)
    _add_right_sidebar(w, d)
    w.resizeDocks([d["front"], d["back"]], [58, 42], Qt.Horizontal)
    w.resizeDocks([d["front"], d["top"]], [62, 38], Qt.Vertical)
    w.resizeDocks([d["control"], d["front"]], [18, 82], Qt.Horizontal)


def _front_focus(w, d):
    w.addDockWidget(Qt.LeftDockWidgetArea, d["front"])
    w.splitDockWidget(d["front"], d["back"], Qt.Horizontal)
    w.tabifyDockWidget(d["back"], d["top"])
    w.tabifyDockWidget(d["back"], d["arm"])
    _add_right_sidebar(w, d)
    # The front feed stays dominant while the secondary feeds remain usable.
    w.resizeDocks([d["front"], d["back"]], [72, 28], Qt.Horizontal)
    w.resizeDocks([d["control"], d["front"]], [18, 82], Qt.Horizontal)
    d["front"].raise_()


def _arm_inspection(w, d):
    w.addDockWidget(Qt.LeftDockWidgetArea, d["arm"])
    w.splitDockWidget(d["arm"], d["front"], Qt.Horizontal)
    w.tabifyDockWidget(d["front"], d["back"])
    w.tabifyDockWidget(d["front"], d["top"])
    _add_right_sidebar(w, d)
    w.resizeDocks([d["arm"], d["front"]], [72, 28], Qt.Horizontal)
    w.resizeDocks([d["control"], d["arm"]], [18, 82], Qt.Horizontal)
    d["arm"].raise_()


def _all_tabbed(w, d):
    w.addDockWidget(Qt.LeftDockWidgetArea, d["front"])
    w.tabifyDockWidget(d["front"], d["back"])
    w.tabifyDockWidget(d["front"], d["top"])
    w.tabifyDockWidget(d["front"], d["arm"])
    _add_right_sidebar(w, d)
    w.resizeDocks([d["control"], d["front"]], [18, 82], Qt.Horizontal)
    d["front"].raise_()


BUILTIN_LAYOUTS = {
    "Quad Grid": _quad_grid,
    "Front Focus": _front_focus,
    "Arm Inspection": _arm_inspection,
    "All Tabbed": _all_tabbed,
}

BUILTIN_LAYOUT_NAMES = list(BUILTIN_LAYOUTS)


def apply_builtin_layout(window, docks, name):
    """Reset every dock to a visible, docked state, then apply `name`."""
    for dock in docks.values():
        dock.setFloating(False)
        dock.setVisible(True)
    BUILTIN_LAYOUTS[name](window, docks)
