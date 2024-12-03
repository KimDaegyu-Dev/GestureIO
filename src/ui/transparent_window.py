from PyQt5.QtWidgets import QMainWindow
from PyQt5.QtGui import QPainter, QPen, QColor
from PyQt5.QtCore import Qt
from src.utils.data_classes import WindowConfig

class TransparentWindow(QMainWindow):
    def __init__(self, config: WindowConfig):
        super().__init__()
        self.config = config
        self.left_hand_keypoints = []
        self.right_hand_keypoints = []
        self.connections = []
        self.initUI()

    def initUI(self):
        self.setGeometry(
            self.config.x,
            self.config.y,
            self.config.width,
            self.config.height
        )
        self._set_window_attributes()
        self.show()

    def _set_window_attributes(self):
        self.setWindowFlags(
            Qt.FramelessWindowHint |
            Qt.WindowStaysOnTopHint |
            Qt.Tool
        )
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setAttribute(Qt.WA_TransparentForMouseEvents)

    def setKeypoints(self, left_hand_keypoints, right_hand_keypoints, connections):
        self.left_hand_keypoints = left_hand_keypoints
        self.right_hand_keypoints = right_hand_keypoints
        self.connections = connections
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        pen = QPen(QColor(self.config.pen_color), self.config.pen_size * 4)
        painter.setPen(pen)

        for keypoints in [self.left_hand_keypoints, self.right_hand_keypoints]:
            if keypoints:
                self._draw_keypoints(painter, keypoints)
                self._draw_connections(painter, keypoints)

    def _draw_keypoints(self, painter, keypoints):
        for point in keypoints:
            x = int(point.x * self.width())
            y = int(point.y * self.height())
            painter.drawEllipse(x - 5, y - 5, 10, 10)

    def _draw_connections(self, painter, keypoints):
        for start_idx, end_idx in self.connections:
            if start_idx < len(keypoints) and end_idx < len(keypoints):
                start_point = keypoints[start_idx]
                end_point = keypoints[end_idx]
                start_x = int(start_point.x * self.width())
                start_y = int(start_point.y * self.height())
                end_x = int(end_point.x * self.width())
                end_y = int(end_point.y * self.height())
                painter.drawLine(start_x, start_y, end_x, end_y)

