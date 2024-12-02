# FILE: ball_simulation.py

import sys
from PyQt5.QtWidgets import QApplication, QMainWindow
from PyQt5.QtGui import QPainter, QPen, QColor
from PyQt5.QtCore import QTimer, QPointF

class BallSimulation(QMainWindow):
    def __init__(self):
        super().__init__()
        self.ball_position = QPointF(100, 100)
        self.ball_velocity = QPointF(2, -5)
        self.gravity = 0.1
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_simulation)
        self.timer.start(16)  # 약 60fps로 업데이트

    def update_simulation(self):
        # 중력 적용
        self.ball_velocity.setY(self.ball_velocity.y() + self.gravity)
        
        # 위치 업데이트
        self.ball_position += self.ball_velocity
        
        # 바닥에 닿으면 반사
        if self.ball_position.y() > self.height() - 10:
            self.ball_position.setY(self.height() - 10)
            self.ball_velocity.setY(-self.ball_velocity.y() * 0.8)  # 반사 시 속도 감소
        
        # 벽에 닿으면 반사
        if self.ball_position.x() < 10 or self.ball_position.x() > self.width() - 10:
            self.ball_velocity.setX(-self.ball_velocity.x())
        
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        pen = QPen(QColor(0, 0, 0), 1)
        painter.setPen(pen)
        painter.setBrush(QColor(255, 0, 0))
        painter.drawEllipse(self.ball_position, 10, 10)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = BallSimulation()
    window.show()
    sys.exit(app.exec_())