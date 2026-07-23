"""UI layer for layout presets: the save dialog and the toolbar.

All persistence is delegated to a LayoutPresetStore; window-state access
(saveState/restoreState) and built-in layout application are injected as
callables, so this module stays decoupled from MainWindow internals.
"""

from PySide6.QtWidgets import (
    QToolBar, QComboBox, QLabel, QDialog, QDialogButtonBox,
    QFormLayout, QLineEdit, QMessageBox, QVBoxLayout
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QAction, QActionGroup

from layout_presets import LayoutPresetStore, PresetError

# Tooltips shown when hovering entries in the layout dropdown
BUILTIN_TOOLTIP = "Built-in layout (hardcoded)"
SHARED_TOOLTIP = "Shared preset - stored in layouts/presets.json"
LOCAL_TOOLTIP = "Local preset - stored on this machine only (QSettings)"


class SavePresetDialog(QDialog):
    """Asks for a preset name and where to store it: shared or local (QSettings)."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Save Layout Preset")
        self.setMinimumWidth(460)

        layout = QVBoxLayout(self)
        form = QFormLayout()

        self.name_edit = QLineEdit()
        self.name_edit.setPlaceholderText("e.g. Docking Run")
        form.addRow("Preset name:", self.name_edit)

        self.scope_combo = QComboBox()
        self.scope_combo.addItem(
            "Shared - layouts/presets.json",
            LayoutPresetStore.SHARED
        )
        self.scope_combo.addItem(
            "Local - this machine only",
            LayoutPresetStore.LOCAL
        )
        form.addRow("Save as:", self.scope_combo)

        layout.addLayout(form)

        buttons = QDialogButtonBox(QDialogButtonBox.Save | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

        self.name_edit.setFocus()

    def values(self):
        """-> (name, scope) where scope is LayoutPresetStore.SHARED or .LOCAL."""
        return self.name_edit.text().strip(), self.scope_combo.currentData()


class LayoutPresetToolBar(QToolBar):
    """Layout selector dropdown plus save/delete preset actions.

    Injected callables:
      get_state()      -> current window state blob (QMainWindow.saveState)
      restore_state(s) -> apply a state blob        (QMainWindow.restoreState)
      apply_builtin(n) -> arrange docks for built-in layout `n`
    """

    def __init__(self, parent, *, store, builtin_names,
                 get_state, restore_state, apply_builtin):
        super().__init__("Layouts", parent)
        self._store = store
        self._builtin_names = list(builtin_names)
        self._get_state = get_state
        self._restore_state = restore_state
        self._apply_builtin = apply_builtin

        self.setMovable(False)
        self.setToolButtonStyle(Qt.ToolButtonTextOnly)
        self.addWidget(QLabel("  LAYOUTS  "))

        self._builtin_actions = QActionGroup(self)
        self._builtin_actions.setExclusive(True)
        for name in self._builtin_names:
            action = QAction(name, self)
            action.setCheckable(True)
            action.setToolTip(BUILTIN_TOOLTIP)
            action.triggered.connect(lambda checked=False, n=name: self._select_builtin(n))
            self._builtin_actions.addAction(action)
            self.addAction(action)

        self.addSeparator()
        self.addWidget(QLabel("Saved: "))

        self.selector = QComboBox()
        self.selector.setMinimumWidth(150)
        self.selector.currentIndexChanged.connect(self._on_selected)
        self.addWidget(self.selector)

        self.addSeparator()

        save_action = QAction("Save Current as Preset...", self)
        save_action.triggered.connect(self._save_current)
        self.addAction(save_action)

        delete_action = QAction("🗑 Delete Preset", self)
        delete_action.triggered.connect(self._delete_current)
        self.addAction(delete_action)

        self.rebuild(select=self._builtin_names[0])

    # ------------------------------------------------------------------
    # Public
    # ------------------------------------------------------------------

    def reset(self):
        """Select and apply the first built-in layout."""
        self.selector.blockSignals(True)
        self.selector.setCurrentIndex(-1)
        self.selector.blockSignals(False)
        self._builtin_actions.actions()[0].setChecked(True)
        self._apply_builtin(self._builtin_names[0])
        self._sync_tooltip()

    def rebuild(self, select=None):
        """Refill the dropdown: built-ins, then shared presets, then local presets."""
        sel = self.selector
        sel.blockSignals(True)
        sel.clear()

        shared_names = self._store.names(LayoutPresetStore.SHARED)
        if shared_names:
            sel.insertSeparator(sel.count())
            for name in shared_names:
                row = sel.count()
                sel.addItem(name, LayoutPresetStore.SHARED)
                sel.setItemData(row, SHARED_TOOLTIP, Qt.ToolTipRole)

        local_names = self._store.names(LayoutPresetStore.LOCAL)
        if local_names:
            sel.insertSeparator(sel.count())
            for name in local_names:
                row = sel.count()
                sel.addItem(name, LayoutPresetStore.LOCAL)
                sel.setItemData(row, LOCAL_TOOLTIP, Qt.ToolTipRole)

        if select is not None:
            row = sel.findText(select)
            if row != -1:
                sel.setCurrentIndex(row)
            elif select in self._builtin_names:
                self._builtin_actions.actions()[self._builtin_names.index(select)].setChecked(True)
        sel.blockSignals(False)

        self._sync_tooltip()

    # ------------------------------------------------------------------
    # Selection / restore
    # ------------------------------------------------------------------

    def _on_selected(self, index):
        if index < 0:
            return
        scope = self.selector.itemData(index, Qt.UserRole)
        name = self.selector.itemText(index)
        self._restore(name, scope)
        self._sync_tooltip()

    def _restore(self, name, scope):
        try:
            state = self._store.load(name, scope)
        except PresetError as e:
            QMessageBox.warning(self, "Preset Unavailable", str(e))
            return
        self._restore_state(state)

    def _sync_tooltip(self):
        """Mirror the current item's tooltip onto the closed combo box."""
        index = self.selector.currentIndex()
        tip = self.selector.itemData(index, Qt.ToolTipRole) if index >= 0 else None
        self.selector.setToolTip(tip or "")

    # ------------------------------------------------------------------
    # Save / delete
    # ------------------------------------------------------------------

    def _save_current(self):
        dialog = SavePresetDialog(self)
        if dialog.exec() != QDialog.Accepted:
            return
        name, scope = dialog.values()
        if not name:
            return

        if name in self._builtin_names:
            QMessageBox.warning(
                self, "Name Reserved",
                f'"{name}" is a built-in layout name. Please choose a different name.'
            )
            return

        # Keep each name in exactly one store so the dropdown stays unambiguous
        other_scope = (LayoutPresetStore.LOCAL if scope == LayoutPresetStore.SHARED
                       else LayoutPresetStore.SHARED)
        if self._store.has(name, other_scope):
            QMessageBox.warning(
                self, "Name In Use",
                f'"{name}" already exists as a {other_scope} preset. '
                "Pick another name, or delete that one first."
            )
            return

        if self._store.has(name, scope):
            confirm = QMessageBox.question(
                self, "Overwrite Preset",
                f'A {scope} preset named "{name}" already exists. Overwrite it?',
                QMessageBox.Yes | QMessageBox.No
            )
            if confirm != QMessageBox.Yes:
                return

        try:
            self._store.save(name, scope, self._get_state())
        except PresetError as e:
            QMessageBox.critical(self, "Save Failed", str(e))
            return

        if scope == LayoutPresetStore.SHARED:
            where = f"{self._store.shared_file}"
        else:
            where = "your local settings (this machine only)"

        self.rebuild(select=name)
        QMessageBox.information(self, "Preset Saved", f'Layout saved as "{name}" to {where}.')

    def _delete_current(self):
        index = self.selector.currentIndex()
        if index < 0:
            return
        scope = self.selector.itemData(index, Qt.UserRole)
        name = self.selector.itemText(index)

        if scope == "builtin":
            QMessageBox.warning(self, "Cannot Delete", "Built-in layouts can't be deleted.")
            return

        if scope == LayoutPresetStore.SHARED:
            detail = ("\n\nThis removes it from layouts/presets.json")
        else:
            detail = "\n\nThis removes it from your local settings on this machine only."

        confirm = QMessageBox.question(
            self, "Delete Preset", f'Delete preset "{name}"?{detail}',
            QMessageBox.Yes | QMessageBox.No
        )
        if confirm != QMessageBox.Yes:
            return

        try:
            self._store.delete(name, scope)
        except PresetError as e:
            QMessageBox.critical(self, "Delete Failed", str(e))
            return

        self.rebuild(select=self._builtin_names[0])

    def _select_builtin(self, name):
        """Apply a visible toolbar layout button."""
        self.selector.blockSignals(True)
        self.selector.setCurrentIndex(-1)
        self.selector.blockSignals(False)
        self._apply_builtin(name)
