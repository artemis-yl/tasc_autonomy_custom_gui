from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel
from PySide6.QtCore import Qt
from PySide6.QtGui import QImage, QPixmap
from PySide6.QtMultimediaWidgets import QVideoWidget

# Optional: GStreamer via gi (fallback if Qt Multimedia isn't enough)
try:
    import gi
    gi.require_version('Gst', '1.0')
    from gi.repository import Gst, GLib
    GSTREAMER_AVAILABLE = True
except ImportError:
    GSTREAMER_AVAILABLE = False


class GStreamerVideoWidget(QWidget):
    """
    Renders GStreamer video pipeline into a Qt widget.
    Uses Qt6's QVideoWidget with a custom media source,
    or falls back to appsink + QImage if needed.
    """

    def __init__(self, pipeline_str=None, parent=None):
        super().__init__(parent)

        self.pipeline_str = pipeline_str
        self._setup_ui()

        # Try Qt Multimedia first (easier, hardware accelerated)
        self._try_qt_multimedia()

        # Fallback to GStreamer direct if specified and available
        if pipeline_str and GSTREAMER_AVAILABLE and not self.has_video:
            self._setup_gstreamer_direct()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        self.placeholder = QLabel("No Signal")
        self.placeholder.setAlignment(Qt.AlignCenter)
        self.placeholder.setStyleSheet("""
            QLabel {
                background-color: #1a1a1a;
                color: #555555;
                font-size: 16px;
            }
        """)
        layout.addWidget(self.placeholder)

        self.video_widget = None
        self.has_video = False

    def _try_qt_multimedia(self):
        """Use Qt6 Multimedia (QCamera, QMediaPlayer) for standard sources."""
        try:
            from PySide6.QtMultimedia import QMediaPlayer

            self.player = QMediaPlayer(self)
            self.video_widget = QVideoWidget()

            self.player.setVideoOutput(self.video_widget)

            self.placeholder.hide()
            self.layout().addWidget(self.video_widget)
            self.has_video = True

        except Exception as e:
            print(f"Qt Multimedia init failed: {e}")

    def _setup_gstreamer_direct(self):
        """Direct GStreamer pipeline with appsink → QImage."""
        if not GSTREAMER_AVAILABLE:
            return

        Gst.init(None)

        if self.pipeline_str is None:
            self.pipeline_str = (
                "v4l2src ! videoconvert ! videoscale ! "
                "video/x-raw,format=RGB,width=640,height=480 ! "
                "appsink name=sink"
            )

        self.pipeline = Gst.parse_launch(self.pipeline_str)
        self.appsink = self.pipeline.get_by_name("sink")
        self.appsink.set_property("emit-signals", True)
        self.appsink.set_property("max-buffers", 1)
        self.appsink.set_property("drop", True)
        self.appsink.connect("new-sample", self._on_new_sample)

        self.pipeline.set_state(Gst.State.PLAYING)

        self.video_label = QLabel()
        self.video_label.setAlignment(Qt.AlignCenter)
        self.video_label.setStyleSheet("background-color: #1a1a1a;")
        self.placeholder.hide()
        self.layout().addWidget(self.video_label)
        self.has_video = True

    def _on_new_sample(self, sink):
        """Callback for GStreamer appsink new frame."""
        sample = sink.pull_sample()
        if sample is None:
            return Gst.FlowReturn.OK

        buffer = sample.get_buffer()
        caps = sample.get_caps()
        structure = caps.get_structure(0)
        width = structure.get_value("width")
        height = structure.get_value("height")

        success, mapinfo = buffer.map(Gst.MapFlags.READ)
        if success:
            image = QImage(
                mapinfo.data,
                width,
                height,
                QImage.Format_RGB888
            )
            pixmap = QPixmap.fromImage(image.copy())
            self.video_label.setPixmap(pixmap.scaled(
                self.video_label.size(),
                Qt.KeepAspectRatio,
                Qt.SmoothTransformation
            ))
            buffer.unmap(mapinfo)

        return Gst.FlowReturn.OK

    def set_rtsp_url(self, url):
        """Configure for RTSP IP camera."""
        if hasattr(self, 'player'):
            from PySide6.QtCore import QUrl
            self.player.setSource(QUrl(url))
            self.player.play()

    def set_v4l2_device(self, device="/dev/video0"):
        """Configure for USB V4L2 camera."""
        if hasattr(self, 'player'):
            pipeline = (
                f"v4l2src device={device} ! videoconvert ! "
                "video/x-raw,format=RGB,width=640,height=480 ! appsink name=sink"
            )
            self.pipeline_str = pipeline
            self._setup_gstreamer_direct()

    def set_test_source(self):
        """GStreamer test source for debugging."""
        self.pipeline_str = (
            "videotestsrc ! videoconvert ! "
            "video/x-raw,format=RGB,width=640,height=480 ! appsink name=sink"
        )
        self._setup_gstreamer_direct()

    def play(self):
        """Start playback."""
        if hasattr(self, 'player'):
            self.player.play()
        elif hasattr(self, 'pipeline'):
            self.pipeline.set_state(Gst.State.PLAYING)

    def stop(self):
        """Stop playback."""
        if hasattr(self, 'player'):
            self.player.stop()
        elif hasattr(self, 'pipeline'):
            self.pipeline.set_state(Gst.State.NULL)

    def resizeEvent(self, event):
        """Scale video on resize."""
        super().resizeEvent(event)
        if hasattr(self, 'video_label') and self.video_label.pixmap():
            self.video_label.setPixmap(self.video_label.pixmap().scaled(
                self.video_label.size(),
                Qt.KeepAspectRatio,
                Qt.SmoothTransformation
            ))