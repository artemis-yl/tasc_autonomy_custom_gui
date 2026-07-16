from __future__ import annotations

import base64
import json
from pathlib import Path

from PySide6.QtCore import QByteArray, QSettings

# Default shared-preset file: <project>/layouts/presets.json
DEFAULT_SHARED_FILE = Path(__file__).parent / "layouts" / "presets.json"


class PresetError(Exception):
    """An expected preset failure that should be shown to the user."""


class LayoutPresetStore:
    SHARED = "shared"
    LOCAL = "local"

    def __init__(self, settings: QSettings, shared_file: "str | Path | None" = None):
        self._settings = settings
        self._shared_file = Path(shared_file) if shared_file else DEFAULT_SHARED_FILE

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    @property
    def shared_file(self) -> Path:
        return self._shared_file

    def names(self, scope: str) -> list:
        """Preset names for a scope (shared: alphabetical; local: save order)."""
        self._check_scope(scope)
        if scope == self.SHARED:
            return sorted(self._read_shared())
        return self._local_names()

    def has(self, name: str, scope: str) -> bool:
        return name in self.names(scope)

    def save(self, name: str, scope: str, state) -> None:
        """Store a saveState() blob under `name` in the given scope."""
        self._check_scope(scope)
        if scope == self.SHARED:
            presets = self._read_shared()
            presets[name] = base64.b64encode(bytes(state)).decode("ascii")
            self._write_shared(presets)
        else:
            self._settings.setValue(f"layouts/{name}", state)
            names = self._local_names()
            if name not in names:
                names.append(name)
                self._set_local_names(names)

    def load(self, name: str, scope: str):
        """Return the stored saveState() blob, ready for restoreState()."""
        self._check_scope(scope)
        if scope == self.SHARED:
            encoded = self._read_shared().get(name)
            if encoded is None:
                raise PresetError(f'Could not find shared preset "{name}".')
            try:
                return QByteArray(base64.b64decode(encoded))
            except (ValueError, TypeError) as e:
                raise PresetError(f'Shared preset "{name}" is corrupt: {e}') from e
        state = self._settings.value(f"layouts/{name}")
        if state is None:
            raise PresetError(f'Could not find local preset "{name}".')
        return state

    def delete(self, name: str, scope: str) -> None:
        """Remove a preset from the given scope (no-op if absent)."""
        self._check_scope(scope)
        if scope == self.SHARED:
            presets = self._read_shared()
            if name in presets:
                del presets[name]
                self._write_shared(presets)
        else:
            self._settings.remove(f"layouts/{name}")
            names = self._local_names()
            if name in names:
                names.remove(name)
                self._set_local_names(names)

    # ------------------------------------------------------------------
    # Internals
    # ------------------------------------------------------------------

    def _check_scope(self, scope: str) -> None:
        if scope not in (self.SHARED, self.LOCAL):
            raise ValueError(f"Unknown preset scope: {scope!r}")

    def _read_shared(self) -> dict:
        """{name: base64_state}; a missing/unreadable file reads as empty."""
        if not self._shared_file.exists():
            return {}
        try:
            data = json.loads(self._shared_file.read_text(encoding="utf-8"))
            return dict(data.get("presets", {}))
        except (OSError, json.JSONDecodeError) as e:
            print(f"[WARN] Could not read shared presets ({self._shared_file}): {e}")
            return {}

    def _write_shared(self, presets: dict) -> None:
        try:
            self._shared_file.parent.mkdir(parents=True, exist_ok=True)
            payload = {"version": 1, "presets": presets}
            self._shared_file.write_text(
                json.dumps(payload, indent=2) + "\n", encoding="utf-8"
            )
        except OSError as e:
            raise PresetError(f"Could not write {self._shared_file}: {e}") from e

    def _local_names(self) -> list:
        raw = self._settings.value("layouts/_names", "")
        return raw.split("|") if raw else []

    def _set_local_names(self, names: list) -> None:
        self._settings.setValue("layouts/_names", "|".join(names))