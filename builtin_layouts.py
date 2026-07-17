"""Hardcoded built-in camera-dock arrangements.

Each layout is a function taking ``(window, docks)``, where ``docks``
maps short keys ("front", "back", "top", "arm", "control", "telemetry")
to QDockWidget instances. BUILTIN_LAYOUTS preserves display order.
"""

from PySide6.QtCore import Qt


def _quad_grid(w, d):
    w.addDockWidget(Qt.LeftDockWidgetArea, d["front"])
    w.splitDockWidget(d["front"], d["back"], Qt.Horizontal)
    w.splitDockWidget(d["front"], d["top"], Qt.Vertical)
    w.splitDockWidget(d["back"], d["arm"], Qt.Vertical)
    w.addDockWidget(Qt.RightDockWidgetArea, d["control"])
    w.addDockWidget(Qt.BottomDockWidgetArea, d["telemetry"])
    w.resizeDocks([d["front"], d["back"]], [1, 1], Qt.Horizontal)
    w.resizeDocks([d["front"], d["top"]], [1, 1], Qt.Vertical)


def _front_focus(w, d):
    w.addDockWidget(Qt.LeftDockWidgetArea, d["front"])
    w.splitDockWidget(d["front"], d["back"], Qt.Horizontal)
    w.tabifyDockWidget(d["back"], d["top"])
    w.tabifyDockWidget(d["back"], d["arm"])
    w.addDockWidget(Qt.RightDockWidgetArea, d["control"])
    w.addDockWidget(Qt.BottomDockWidgetArea, d["telemetry"])
    w.resizeDocks([d["front"], d["back"]], [3, 1], Qt.Horizontal)
    d["front"].raise_()


def _arm_inspection(w, d):
    w.addDockWidget(Qt.LeftDockWidgetArea, d["arm"])
    w.splitDockWidget(d["arm"], d["front"], Qt.Horizontal)
    w.tabifyDockWidget(d["front"], d["back"])
    w.tabifyDockWidget(d["front"], d["top"])
    w.addDockWidget(Qt.RightDockWidgetArea, d["control"])
    w.addDockWidget(Qt.BottomDockWidgetArea, d["telemetry"])
    w.resizeDocks([d["arm"], d["front"]], [3, 1], Qt.Horizontal)
    d["arm"].raise_()


def _all_tabbed(w, d):
    w.addDockWidget(Qt.LeftDockWidgetArea, d["front"])
    w.tabifyDockWidget(d["front"], d["back"])
    w.tabifyDockWidget(d["front"], d["top"])
    w.tabifyDockWidget(d["front"], d["arm"])
    w.addDockWidget(Qt.RightDockWidgetArea, d["control"])
    w.addDockWidget(Qt.BottomDockWidgetArea, d["telemetry"])
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