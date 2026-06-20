"""CameraWidget — 摄像头预览组件。"""
from __future__ import annotations

from PySide6.QtCore import QThread, Signal, QTimer
from PySide6.QtWidgets import QLabel

from app.components import BaseWidget


class CameraThread(QThread):
    """后台线程持续读取摄像头帧。"""
    frame_ready = Signal(object)  # numpy.ndarray (BGR)

    def __init__(self, camera_id: int = 0, parent=None):
        super().__init__(parent)
        self.camera_id = camera_id
        self._running = False

    def run(self):
        import cv2
        self._running = True
        cap = cv2.VideoCapture(self.camera_id)
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
        while self._running and cap.isOpened():
            ret, frame = cap.read()
            if ret:
                self.frame_ready.emit(frame)
            self.msleep(30)
        cap.release()

    def stop(self):
        self._running = False
        self.wait()


class CameraWidget(BaseWidget):
    """摄像头画面显示控件。"""

    def __init__(self, parent=None):
        self._thread: CameraThread | None = None
        self._latest_frame = None
        super().__init__(parent)

    def setup_ui(self):
        self.view = QLabel("点击「启动摄像头」开始")
        self.view.setObjectName("cameraView")
        self.view.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.view.setFixedSize(560, 420)
        # TODO: layout

    def start(self):
        if self._thread is None:
            self._thread = CameraThread()
            self._thread.frame_ready.connect(self._update_frame)
            self._thread.start()

    def stop(self):
        if self._thread and self._thread.isRunning():
            self._thread.stop()
            self._thread = None

    def _update_frame(self, frame):
        import cv2
        from PySide6.QtGui import QImage, QPixmap
        self._latest_frame = frame.copy()
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        h, w, ch = rgb.shape
        qt_img = QImage(rgb.data, w, h, ch * w, QImage.Format.Format_RGB888)
        self.view.setPixmap(QPixmap.fromImage(qt_img).scaled(
            560, 420, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation))

    def capture_frame(self):
        """返回当前帧（numpy.ndarray）或 None。"""
        return self._latest_frame
