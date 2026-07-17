# tasc_autonomy_custom_gui

PySide6 dockable camera GUI for robot autonomy. Four independent camera feeds in floating/tabbed docks, a scrollable control panel, and telemetry readouts.

## Set up Pyside6 and PGobject in Windows
https://docs.google.com/document/d/1uKSwuobtI_gU1plCXWybySQjaeOVPDeHOYEN8cozPjo/edit?usp=sharing


## What's Working

- **Dock system** - drag, float, tab, hide/show, reset layout via View menu
- **Scrollable controls** - exposure, gain, WB, resolution, FPS, brightness, contrast, saturation, sharpness, zoom, flip H/V
- **Apply button** - emits `settings_applied(camera_name, settings_dict)` signal
- **Telemetry panel** - updates every second (currently simulated random data)

## Placeholders / TODO

| Item | Status | What to do |
|------|--------|------------|
| Camera video sources | Placeholder | Uncomment `set_source()` calls in `main.py`. Currently shows "No Signal". Add actual V4L2 devices, RTSP URLs, or Orbbec SDK integration. |
| Apply to hardware | Stub | `_apply_to_camera()` only prints to stdout. Wire to the camera SDK (V4L2 `ioctl`, Orbbec API, or GStreamer `pipeline.set_property()`). |
| Telemetry data | Simulated | `_update_telemetry()` generates random numbers. Replace with real GStreamer pad probes, RTCP stats, or autonomy stack metrics. |
| GStreamer direct | Optional | If Qt Multimedia handles the cameras well, remove the `gi` fallback entirely. If raw pipeline control is needed, keep it and ensure `python3-gi` is installed. |
| QML workspace | Decorative | `Main.qml` is just a dark rectangle with placeholder text. Add a robot status overlay, map view, or mission timeline later. |
| Layout persistence | Not implemented | Add `QSettings` save/restore of `saveState()`/`saveGeometry()` if layout should survive restarts. |
| Keyboard shortcuts | Not implemented | Add `QAction` shortcuts for dock toggles, emergency stop, etc. |

## Dependencies

```bash
pip install PySide6

# Optional: for direct GStreamer pipeline control
sudo apt install python3-gi gir1.2-gst-1.0 gstreamer1.0-plugins-good
```

## Run

```bash
python main.py
```

## Next Priority

1. **Activate cameras** - uncomment `set_source()` lines and verify hardware paths
2. **Wire Apply button** - connect `_apply_to_camera()` to the actual camera parameter API
3. **Real telemetry** - replace random data with stream statistics from the video pipeline
