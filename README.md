# TASC Autonomy Camera Console

A PySide6 desktop console for viewing and managing four robot camera feeds. The interface is built around dockable camera panels, a compact control and telemetry sidebar, and operator-focused layouts that adapt to the available display area.

## What it provides

- Four independent camera panels: Orbbec front, webcam back, top IP camera, and arm IR camera.
- Live video through GStreamer pipelines.
- A shared right-hand sidebar with camera controls above stream telemetry.
- Dockable, tabbed, and floating panels for operator-specific arrangements.
- Built-in layouts, saved shared layouts, and per-machine layouts.
- Compact dark operator-console styling with clear stream, image, and orientation controls.

The application starts in **Front Focus**, with the front camera given most of the available workspace. The window scales to the usable desktop area instead of assuming a 1920 × 1080 display.

## Requirements

- Python 3.10+ (the project is currently run with the MSYS2 MinGW Python distribution).
- PySide6
- NumPy
- PyGObject / `gi`
- GStreamer 1.0 with the H.264 and H.265 decoding elements used by the configured sources.

The GStreamer and `gi` packages must be installed in the same MSYS2/MinGW environment as the Python interpreter used to launch the app.

## Run

From the project directory:

```powershell
c:\msys64\mingw64\bin\python.exe .\main.py
```

If your environment already resolves the intended Python and dependencies, this also works:

```powershell
python .\main.py
```

## Camera configuration

Camera sources are configured in `CAMERAS` near the top of `main.py`:

| Key | Display name | Host | Port | Source type |
| --- | --- | --- | --- | --- |
| `front` | Orbbec / Front | `192.168.1.7` | `7092` | SRT / H.264 |
| `back` | WebCam / Back | `192.168.1.7` | `7091` | SRT / H.264 |
| `top` | IP Cam / Top | `192.168.1.117` | `8554` | RTSP / H.265 |
| `arm` | IR Cam / ARM | `192.168.1.116` | `8554` | RTSP / H.265 |

Update these addresses and ports to match the robot network before deployment.

## Layouts and panels

Open **Layouts** in the menu bar to select one of the built-in arrangements:

- **Quad Grid** — all four views visible in a balanced grid.
- **Front Focus** — front camera large, remaining feeds tabbed.
- **Arm Inspection** — arm camera large, remaining feeds tabbed.
- **All Tabbed** — one camera workspace with tabs for the other feeds.

Keyboard shortcuts are available from anywhere in the window:

| Shortcut | Layout |
| --- | --- |
| `Ctrl+1` | Quad Grid |
| `Ctrl+2` | Front Focus |
| `Ctrl+3` | Arm Inspection |
| `Ctrl+4` | All Tabbed |

Panels can still be dragged, floated, tabbed, hidden from **View**, or restored with **View → Reset Layout**.

### Saved layouts

Use **Layouts → Save Current Layout as Preset…** to store the current panel arrangement.

- **Shared** presets are stored in `layouts/presets.json` and can be committed or shared with the project.
- **Local** presets are stored with Qt settings on the current computer.

Load presets from **Layouts → Saved Layouts**. Remove them with **Layouts → Delete Saved Layout**; deletion requires confirmation.

## Camera controls

The Camera Controls dock always identifies the currently selected camera in its title. Controls are arranged into three sections:

- **Stream** — active camera, resolution, frame rate, and bitrate.
- **Image** — brightness.
- **Orientation** — horizontal and vertical flip.

**Apply Settings / Play Stream** and **Stop Selected Stream** build a newline-delimited JSON control message. The TCP client connects to `127.0.0.1:8080`.

For the front and back cameras, the current control payload contains:

```json
{
  "state": "play",
  "camera": "orbbec_color",
  "width": 1280,
  "height": 720,
  "fps": 30,
  "bitrate": 500
}
```

The IP-camera control path is currently a placeholder that logs the intended ONVIF action; it does not yet send an ONVIF command. Brightness and flip controls are present in the interface but are not included in the outgoing control payload yet.

## Telemetry

Telemetry refreshes twice per second and reports the state exposed by each video panel. The current video widget provides the panel state (`Running`, `Idle`, or `Error`); FPS, latency, bitrate, and dropped-frame values remain placeholders until GStreamer statistics are added.

## Project structure

| File | Purpose |
| --- | --- |
| `main.py` | Application startup, camera configuration, menus, shortcuts, and dock setup. |
| `camera_dock.py` | Dock container for each video feed. |
| `video_widget.py` | GStreamer pipeline setup and frame display. |
| `control_dock.py` | Camera control interface and TCP command construction. |
| `camera_client.py` | TCP JSON client for the local streamer service. |
| `telemetry_dock.py` | Per-camera stream-status readouts. |
| `builtin_layouts.py` | Built-in dock arrangements and sidebar sizing. |
| `layout_presets.py` / `preset_ui.py` | Shared and local layout-preset persistence. |
| `theme.py` | Application-wide visual styling. |

## Known limitations

- The UI does not currently reconnect a failed stream automatically.
- GStreamer statistics beyond pipeline state are not yet collected.
- IP-camera play/stop commands need real ONVIF implementation.
- Camera parameters are only sent when the corresponding streamer/control service is reachable.
