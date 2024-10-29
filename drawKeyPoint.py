from PyQt5.QtWidgets import QMainWindow, QApplication
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPainter, QPen, QColor

class TransparentWindow(QMainWindow):
    def __init__(self, x: int, y: int, width: int, height: int, pen_color: str, pen_size: int):
        super().__init__()
        self.highlight_x = x
        self.highlight_y = y
        self.highlight_width = width
        self.highlight_height = height
        self.pen_color = pen_color
        self.pen_size = pen_size
        self.keypoints = []
        self.initUI()

    def initUI(self):
        self.setGeometry(self.highlight_x, self.highlight_y, self.highlight_width, self.highlight_height)
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.Tool)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setAttribute(Qt.WA_TransparentForMouseEvents)  # 마우스 이벤트를 투명하게 처리
        self.show()

    def setKeypoints(self, keypoints):
        self.keypoints = keypoints
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        pen = QPen(QColor(self.pen_color), self.pen_size)
        painter.setPen(pen)
        for point in self.keypoints:
            painter.drawPoint(point[0], point[1])