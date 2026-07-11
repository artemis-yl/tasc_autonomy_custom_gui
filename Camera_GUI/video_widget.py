import gi
gi.require_version("Gst", "1.0")
from gi.repository import Gst

import numpy as np
import time
from collections import deque

from PySide6.QtWidgets import QWidget, QLabel, QVBoxLayout, QSizePolicy
from PySide6.QtGui import QImage, QPixmap
from PySide6.QtCore import QTimer, Qt

Gst.init(None)

class GStreamerVideoWidget(QWidget):
    def __init__(self, parent=None, stats_callback=None):
        super().__init__(parent)

        self._stats_callback = stats_callback
        self._settings = {
            "resolution": "1280x720",
            "fps": "30 fps",
            "brightness": 50,
            "bitrate": "4000 kbps",
            "flip_h": False,
            "flip_v": False,
        }
        self._frame_times = deque(maxlen=60)
        self._last_recv_time = None
        self._estimated_dropped = 0
        self._last_stats = {
            "fps": None,
            "latency_ms": None,
            "bitrate_kbps": None,
            "dropped": 0,
            "status": "Idle",
            "frames": 0,
        }

        self.label = QLabel("No Signal")
        self.label.setStyleSheet("background:black;")
        self.label.setAlignment(Qt.AlignCenter)
        self.label.setScaledContents(True)
        self.label.setMinimumSize(320, 240)
        self.label.setMaximumSize(800, 450)
        self.label.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.label)

        self.setMinimumSize(320, 240)
        self.setMaximumSize(800, 450)
        self.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)

        self.pipeline = None
        self.appsink = None

        self.timer = QTimer()
        self.timer.timeout.connect(self._pull_frame)

    def set_stats_callback(self, callback):
        self._stats_callback = callback

    def _emit_stats(self):
        if self._stats_callback:
            self._stats_callback(dict(self._last_stats))

    def _parse_resolution(self, value):
        try:
            width, height = value.lower().split("x", 1)
            return int(width), int(height)
        except Exception:
            return 1280, 720

    def _parse_fps(self, value):
        try:
            return int(str(value).split()[0])
        except Exception:
            return 30

    def _parse_bitrate(self, value):
            try:
                text = str(value).strip()
                if text.lower() == "uncapped":
                    return None
                return int(text.split()[0])
            except Exception:
                return 4000

    def _brightness_for_gst(self):
        value = self._settings.get("brightness", 50)
        try:
            value = float(value)
        except Exception:
            value = 50.0
        return max(-1.0, min(1.0, (value - 50.0) / 50.0))

    def _flip_method(self):
        flip_h = bool(self._settings.get("flip_h", False))
        flip_v = bool(self._settings.get("flip_v", False))
        if flip_h and flip_v:
            return "rotate-180"
        if flip_h:
            return "horizontal-flip"
        if flip_v:
            return "vertical-flip"
        return "none"

    def _extract_fps_from_caps(self, caps):
        try:
            structure = caps.get_structure(0)
            framerate = structure.get_value("framerate")
        except Exception:
            return None

        if framerate is None:
            return None

        numerator = getattr(framerate, "numerator", getattr(framerate, "num", None))
        denominator = getattr(framerate, "denominator", getattr(framerate, "denom", None))

        if numerator and denominator:
            return float(numerator) / float(denominator)

        return None

    def _calculate_latency_ms(self, buffer):
        try:
            if not self.pipeline:
                return None

            pts = buffer.pts
            if pts == Gst.CLOCK_TIME_NONE:
                return None

            clock = self.pipeline.get_clock()
            base_time = self.pipeline.get_base_time()
            if not clock or base_time == Gst.CLOCK_TIME_NONE:
                return None

            running_time_ns = clock.get_time() - base_time
            latency_ns = running_time_ns - pts
            if latency_ns < 0:
                return None

            return latency_ns / 1_000_000.0
        except Exception:
            return None

    def get_stats(self):
        return dict(self._last_stats)

    def _reset_stats(self):
        self._frame_times.clear()
        self._last_recv_time = None
        self._estimated_dropped = 0
        self._last_stats.update({
            "fps": None,
            "latency_ms": None,
            "bitrate_kbps": None,
            "dropped": 0,
            "status": "Running",
            "frames": 0,
        })
        self._emit_stats()

    def _build_pipeline_str(self, device_index: int = None, source_mode: str = "usb", stream_uri: str = None):
        width, height = self._parse_resolution(self._settings.get("resolution", "1280x720"))
        brightness = self._brightness_for_gst()
        flip_method = self._flip_method()

        if source_mode == "srt" and stream_uri:
            return (
                f'uridecodebin uri="{stream_uri}" name=src ! '
                "queue max-size-buffers=2 leaky=downstream ! "
                f"videoflip method={flip_method} ! "
                f"videobalance brightness={brightness:.3f} ! "
                "videoscale ! "
                f"video/x-raw,width={width},height={height} ! "
                "videoconvert ! "
                "video/x-raw,format=BGR ! "
                "appsink name=sink emit-signals=false max-buffers=1 drop=true sync=false"
            )

        return (
            f"mfvideosrc device-index={device_index} ! "
            "queue max-size-buffers=2 leaky=downstream ! "
            f"video/x-raw,width={width},height={height} ! "
            f"videoflip method={flip_method} ! "
            f"videobalance brightness={brightness:.3f} ! "
            "videoconvert ! "
            "video/x-raw,format=BGR ! "
            "appsink name=sink emit-signals=false max-buffers=1 drop=true sync=false"
        )

    # ---------------- START ----------------
    def start(self, device_index: int = None, settings=None, source_mode: str = "usb", stream_uri: str = None):
        if source_mode == "srt":
            print(f"[GST] Starting SRT stream {stream_uri}")
        else:
            print(f"[GST] Starting appsink camera {device_index}")
        if settings:
            self._settings.update(settings)
        self._reset_stats()

        pipeline_str = self._build_pipeline_str(
            device_index=device_index,
            source_mode=source_mode,
            stream_uri=stream_uri,
        )

        print("[GST PIPELINE]")
        print(pipeline_str)

        self.pipeline = Gst.parse_launch(pipeline_str)
        self.appsink = self.pipeline.get_by_name("sink")

        if not self.appsink:
            print("[GST ERROR] appsink not found")
            return

        ret = self.pipeline.set_state(Gst.State.PLAYING)
        print(f"[GST STATE] PLAYING = {ret}")

        target_fps = self._parse_fps(self._settings.get("fps", "30 fps"))
        poll_interval_ms = max(5, int(1000 / max(1, target_fps)))
        self.timer.start(poll_interval_ms)

    # ---------------- FRAME GRAB ----------------
    def _pull_frame(self):
        if not self.appsink:
            return

        sample = self.appsink.emit("try-pull-sample", 0)
        if not sample:
            return

        buf = sample.get_buffer()
        caps = sample.get_caps()

        ok, map_info = buf.map(Gst.MapFlags.READ)
        if not ok:
            return

        try:
            recv_time = time.monotonic()
            arr = np.frombuffer(map_info.data, dtype=np.uint8)

            s = caps.get_structure(0)
            w = s.get_value("width")
            h = s.get_value("height")

            self._frame_times.append(recv_time)
            if len(self._frame_times) >= 2:
                elapsed = self._frame_times[-1] - self._frame_times[0]
                fps = (len(self._frame_times) - 1) / elapsed if elapsed > 0 else None
            else:
                fps = None

            caps_fps = self._extract_fps_from_caps(caps)
            if fps is not None and caps_fps is not None and self._last_recv_time is not None:
                expected_interval = 1.0 / caps_fps if caps_fps > 0 else None
                if expected_interval:
                    gap = recv_time - self._last_recv_time
                    if gap > expected_interval * 1.5:
                        missed = max(0, int(round(gap / expected_interval)) - 1)
                        self._estimated_dropped += missed

            latency_ms = self._calculate_latency_ms(buf)
            # For local preview pipelines there is no true transport bitrate.
            # Use selected target bitrate so control changes are reflected.
            bitrate_kbps = self._parse_bitrate(self._settings.get("bitrate", "4000 kbps"))

            frame = arr.reshape((h, w, 3))

            img = QImage(frame.data, w, h, 3 * w, QImage.Format_BGR888)
            self.label.setPixmap(QPixmap.fromImage(img))

            self._last_recv_time = recv_time
            self._last_stats.update({
                "fps": fps,
                "latency_ms": latency_ms,
                "bitrate_kbps": bitrate_kbps,
                "dropped": self._estimated_dropped,
                "status": "Running",
                "frames": self._last_stats.get("frames", 0) + 1,
            })
            self._emit_stats()

        finally:
            buf.unmap(map_info)

    # ---------------- STOP ----------------
    def stop(self):
        self.timer.stop()
        if self.pipeline:
            self.pipeline.set_state(Gst.State.NULL)
            self.pipeline = None
        self._last_stats.update({"status": "Idle"})
        self._emit_stats()