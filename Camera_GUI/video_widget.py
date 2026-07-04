import gi
gi.require_version("Gst", "1.0")
from gi.repository import Gst

import numpy as np

from PySide6.QtWidgets import QWidget, QLabel, QVBoxLayout
from PySide6.QtGui import QImage, QPixmap
from PySide6.QtCore import QTimer

Gst.init(None)


class GStreamerVideoWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.label = QLabel("No Signal")
        self.label.setStyleSheet("background:black;")

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.label)

        self.pipeline = None
        self.appsink = None

        self.timer = QTimer()
        self.timer.timeout.connect(self._pull_frame)

    # ---------------- START ----------------
    def start(self, device_index: int):
        print(f"[GST] Starting appsink camera {device_index}")

        pipeline_str = (
            f"mfvideosrc device-index={device_index} ! "
            "videoconvert ! "
            "video/x-raw,format=BGR ! "
            "appsink name=sink emit-signals=false max-buffers=1 drop=true"
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

        self.timer.start(30)

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
            arr = np.frombuffer(map_info.data, dtype=np.uint8)

            s = caps.get_structure(0)
            w = s.get_value("width")
            h = s.get_value("height")

            frame = arr.reshape((h, w, 3))

            img = QImage(frame.data, w, h, 3 * w, QImage.Format_BGR888)
            self.label.setPixmap(QPixmap.fromImage(img))

        finally:
            buf.unmap(map_info)

    # ---------------- STOP ----------------
    def stop(self):
        if self.pipeline:
            self.pipeline.set_state(Gst.State.NULL)
            self.pipeline = None