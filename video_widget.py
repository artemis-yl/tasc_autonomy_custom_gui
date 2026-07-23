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
        self.label = QLabel("NO VIDEO SIGNAL\nWaiting for stream")
        self.label.setStyleSheet("background:#070a0d; color:#7890a2; qproperty-alignment: 'AlignCenter'; font-size: 13px; font-weight: 600;")
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.label)
        self.pipeline = None
        self.appsink = None
        self.timer = QTimer()
        self.timer.timeout.connect(self._pull_frame)

    def start(self, ip, port: int):
        print(f"[GST] Listening for SRT stream on port: {port}")

        # 7091 is back, 7092 is orbbec color
        if port == 7091 or  port == 7092:
            # use ports to change pipeline based on ip vs usb
            pipeline_str = (
                f'srtsrc uri="srt://{ip}:{port}?mode=caller" keep-listening=true ! '
                "h264parse ! "
                "avdec_h264 ! "
                "videoconvert ! "
                "video/x-raw,format=BGR ! "
                "appsink name=sink emit-signals=false sync=false max-buffers=1 drop=true"
            )
        # assume its the IP cams
        elif port == 8554:
            #gst-launch-1.0 rtspsrc location=rtspt://admin:@192.168.1.117:8554/profile1 latency=0 ! 
            # rtph265depay ! h265parse !  avdec_h265 ! autovideosink sync=false
            # both IP cameras uses port 8554
            pipeline_str = (
                f'rtspsrc location=rtspt://admin:@{ip}:{port}/profile1 latency=0 ! '
                "rtph265depay ! "
                "h265parse ! "
                "avdec_h265 ! "
                "videoconvert ! "
                "video/x-raw,format=BGR ! "
                "appsink name=sink emit-signals=false sync=false max-buffers=1 drop=true"
            )

        print(f"[GST PIPELINE] {pipeline_str}")

        try:
            self.pipeline = Gst.parse_launch(pipeline_str)
            self.appsink = self.pipeline.get_by_name("sink")

            if not self.appsink:
                self.label.setText("Pipeline Error")
                return

            ret = self.pipeline.set_state(Gst.State.PLAYING)
            print(f"[GST STATE] Port {port} PLAYING = {ret}")

            self.timer.start(30)

        except Exception as e:
            print(f"[GST CRASH] {e}")
            self.label.setText("Network Error")

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

    def stop(self):
        self.timer.stop()
        if self.pipeline:
            self.pipeline.set_state(Gst.State.NULL)
            self.pipeline = None
            self.appsink = None
        self.label.setText("Waiting for Stream...")
