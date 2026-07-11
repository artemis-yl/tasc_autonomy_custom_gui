# TASC Camera GUI

A PySide6-based docking GUI for viewing and controlling multiple camera feeds via GStreamer, supporting both direct USB/webcam capture and remote SRT (Secure Reliable Transport) streams.

## Features

- Dockable camera panels (`CameraDock`) with live GStreamer video preview, laid out as a 2x2 grid
- Per-camera controls: resolution, frame rate, brightness, bitrate (including an **Uncapped** option), horizontal/vertical flip
- Two capture sources:
  - **USB mode**: captures directly from a local webcam via `mfvideosrc` (Windows Media Foundation)
  - **SRT mode**: receives an already-encoded H.264/MPEG-TS stream over the network via `srtsrc`
- Live telemetry dock showing FPS, latency, bitrate, dropped frames, and stream status per camera, with a fixed-width readout so value changes don't reflow neighboring docks
- Reset-able dock layout via the View menu
- Camera setup is data-driven: adding, removing, or renaming cameras only requires editing the camera list in `main.py` and the friendly-name map in `camera_manager.py`, nothing else

## Requirements

- **Windows** with [MSYS2](https://www.msys2.org/) installed
- GStreamer (mingw64) with the following plugin sets:
  - `mingw-w64-x86_64-gstreamer`
  - `mingw-w64-x86_64-gst-plugins-base`
  - `mingw-w64-x86_64-gst-plugins-good`
  - `mingw-w64-x86_64-gst-plugins-bad` (provides `srtsrc`/`srtsink`, `openh264enc`, `mfvideosrc`)
  - `mingw-w64-x86_64-gst-plugins-ugly` (provides `x264enc`, if you prefer libx264 over OpenH264)
  - `mingw-w64-x86_64-gst-python` (GObject introspection bindings for Python)
- Python (the **MSYS2 mingw64 Python**, not a separate Windows Python install, see [Environment notes](#environment-notes) below)
- Python packages: `PySide6`, `numpy`

Install the GStreamer plugin sets from an **MSYS2 MinGW64** shell:

```bash
pacman -S mingw-w64-x86_64-gstreamer \
          mingw-w64-x86_64-gst-plugins-base \
          mingw-w64-x86_64-gst-plugins-good \
          mingw-w64-x86_64-gst-plugins-bad \
          mingw-w64-x86_64-gst-plugins-ugly \
          mingw-w64-x86_64-gst-python
```

## Environment notes

This project depends on GStreamer's Python (`gi`) bindings, which must come from the **same GStreamer install** the app links against. Mixing a standalone Windows Python (e.g. `C:\Program Files\Python3xx\python.exe`) with MSYS2's GStreamer will typically fail to import `gi` at all, or silently miss plugins.

Always launch the app using the MSYS2 mingw64 Python interpreter directly, e.g.:

```powershell
& C:\msys64\mingw64\bin\python.exe C:\msys64\home\<user>\tasccams\Camera_GUI\main.py --source usb
```

Sanity-check the interpreter before debugging anything else:

```powershell
& C:\msys64\mingw64\bin\python.exe -c "import gi; gi.require_version('Gst','1.0'); from gi.repository import Gst; print('OK')"
```

If you're running `gst-launch-1.0` / `gst-inspect-1.0` from PowerShell and getting "not recognized," MSYS2's mingw64 tools aren't on PowerShell's `PATH` by default. Either use the **MSYS2 MinGW64** shell (Start Menu), or add it for the session:

```powershell
$env:Path += ";C:\msys64\mingw64\bin"
```

No `sudo`/admin elevation is required to run this app, it only opens a webcam and a couple of local UDP ports.

## Running the app

**USB mode** (default):

```powershell
python main.py --source usb
```

**SRT mode** (receive streams from a remote/local encoder, see below):

```powershell
python main.py --source srt --srt-laptop-uri srt://127.0.0.1:9000 --srt-usb-uri srt://127.0.0.1:9001
```

| Flag | Description | Default |
|---|---|---|
| `--source` | `usb` or `srt` | `usb` |
| `--srt-laptop-uri` | SRT URI for the first camera slot (currently "Orbbec / Front") | `srt://127.0.0.1:9000` |
| `--srt-usb-uri` | SRT URI for the second camera slot (currently "WebCam / Back") | `srt://127.0.0.1:9001` |

The third and fourth camera slots ("IP Cam / Top" and "IR Cam / ARM") don't currently have dedicated SRT CLI flags; in SRT mode they'll fail to start with a `[FAIL] ... (no SRT URI provided)` message until URIs are wired up for them too.

## Testing SRT streams locally

The app's `srtsrc` element connects out to the given URI as an SRT **caller** by default, so you need an SRT **listener** (sender) running first. Two example sender pipelines, one per camera, each on its own port:

```powershell
# Sender 1: first camera slot, port 9000 (OpenH264, no extra plugin install needed if gst-plugins-bad is installed)
gst-launch-1.0 -v mfvideosrc device-index=0 ! videoconvert ! video/x-raw,width=1280,height=720,framerate=30/1 ! openh264enc ! video/x-h264,profile=high ! mpegtsmux ! srtsink uri="srt://:9000" wait-for-connection=false

# Sender 2: second camera slot, port 9001 (libx264, requires gst-plugins-ugly)
gst-launch-1.0 -v mfvideosrc device-index=1 ! videoconvert ! video/x-raw,width=1280,height=720,framerate=30/1 ! x264enc tune=zerolatency bitrate=4000 speed-preset=ultrafast ! video/x-h264,profile=high ! mpegtsmux ! srtsink uri="srt://:9001" wait-for-connection=false
```

Then, in a separate terminal, start the GUI pointed at those ports:

```powershell
& C:\msys64\mingw64\bin\python.exe Camera_GUI\main.py --source srt --srt-laptop-uri srt://127.0.0.1:9000 --srt-usb-uri srt://127.0.0.1:9001
```

To debug a stream in isolation before blaming the app, verify it plays with a plain `gst-launch-1.0` receiver first:

```powershell
gst-launch-1.0 srtsrc uri="srt://127.0.0.1:9000" ! decodebin ! autovideosink
```

`x264enc` requires `gst-plugins-ugly` (`pacman -S mingw-w64-x86_64-gst-plugins-ugly`), since it's GPL-licensed and not bundled with the base/good/bad plugin sets. `openh264enc` (from `gst-plugins-bad`) is a drop-in alternative that avoids the extra install.

## Project structure

| File | Purpose |
|---|---|
| `main.py` | App entry point; sets up the main window, camera docks, menu, and telemetry polling |
| `camera_dock.py` | `CameraDock`, dockable panel wrapping a `GStreamerVideoWidget` for one camera |
| `camera_manager.py` | `CameraManager`, resolves a logical camera name (e.g. "Orbbec / Front") to a Windows device index via `Get-PnpDevice` |
| `control_dock.py` | `CameraControlDock`, resolution/FPS/brightness/bitrate/flip controls, emits `settings_applied` |
| `telemetry_dock.py` | `TelemetryDock`, live per-camera stats readout (FPS, latency, bitrate, dropped frames, status) |
| `video_widget.py` | `GStreamerVideoWidget`, builds and runs the GStreamer pipeline (USB or SRT), pulls frames via `appsink`, reports stats |

## Cameras

The GUI currently shows four camera docks, laid out as a 2x2 grid:

| Dock name | Windows friendly-name match |
|---|---|
| Orbbec / Front | `Orbbec` |
| WebCam / Back | `UVC HD Camera` |
| IP Cam / Top | `USB Camera` |
| IR Cam / ARM | `IR` |

Dock names and their SRT/USB wiring live in `_setup_camera_docks` in `main.py`. The same names must appear in `CameraManager.camera_map` in `camera_manager.py` so USB mode can resolve each one to a device index. Everything downstream, the control dock's camera selector, telemetry, and the "Apply Settings" routing, keys off these name strings and needs no other changes when swapping camera names or adding/removing entries.

## Camera name resolution (USB mode)

`CameraManager` maps the logical dock names to actual Windows device indices by matching each entry's `friendly_name` against `Get-PnpDevice -Class Camera` output. If a physical camera isn't being picked up, check that its Windows friendly name (or a distinguishing substring of it) matches the `friendly_name` value set for that camera in `camera_manager.py`.

## Known behavior / gotchas

- **Bitrate is display-only in the current pipeline.** The `bitrate_kbps` telemetry value reflects the *selected* setting, not a true measured transport bitrate; there's no encoder bitrate control wired into the local preview pipeline yet. Selecting "Uncapped" reports the bitrate field as `Uncapped` rather than a number.
- **SRT startup delay:** after `start()`, don't be surprised by a second or two of black/frozen frame until the sender's first H.264 keyframe arrives; this is normal for SRT/MPEG-TS, not a bug.
- **Telemetry label width is fixed** (`status_label.setFixedWidth(...)` in `telemetry_dock.py`) specifically to stop long stat strings (e.g. large FPS/bitrate numbers) from reflowing and shoving neighboring docks around. If you widen the stats format, bump that fixed width accordingly rather than removing it.
- **Only the first two camera slots have SRT URIs wired to CLI flags** (`--srt-laptop-uri`, `--srt-usb-uri`). The other two run with no stream URI in SRT mode and will fail to start until dedicated flags (or another config source) are added for them.