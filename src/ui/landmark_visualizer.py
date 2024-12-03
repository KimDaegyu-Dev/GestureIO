from PyQt5.QtWidgets import QWidget, QVBoxLayout, QPushButton, QLineEdit, QListWidget
from PyQt5.QtGui import QPainter, QPen, QColor, QFont
from PyQt5.QtCore import QRectF, Qt

class LandmarkVisualizerWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('Landmark Visualizer')
        self.setGeometry(100, 100, 800, 600)
        self.landmarks = []
        self.received_landmarks = []
        self.winner = None

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        # Draw own landmarks (mirrored)
        self.draw_landmarks(painter, self.landmarks, Qt.green)

        # Draw received landmarks
        self.draw_landmarks(painter, self.received_landmarks, Qt.blue)

        # Draw winner text if applicable
        if self.winner:
            painter.setFont(QFont('Arial', 20))
            painter.setPen(Qt.red)
            if self.winner == 'self':
                text_rect = QRectF(10, self.height() - 40, self.width() - 20, 30)
                painter.drawText(text_rect, Qt.AlignLeft | Qt.AlignBottom, "You won!")
            elif self.winner == 'opponent':
                text_rect = QRectF(10, 10, self.width() - 20, 30)
                painter.drawText(text_rect, Qt.AlignRight | Qt.AlignTop, "Opponent won!")

    def draw_landmarks(self, painter, landmarks, color):
        if not landmarks:
            return

        pen = QPen(color, 2)
        painter.setPen(pen)

        for landmark in landmarks:
            x = int(landmark['x'] * self.width())
            y = int(landmark['y'] * self.height())
            painter.drawEllipse(x - 5, y - 5, 10, 10)

        connections = [
            (0, 1), (1, 2), (2, 3), (3, 4),  # Thumb
            (0, 5), (5, 6), (6, 7), (7, 8),  # Index finger
            (0, 9), (9, 10), (10, 11), (11, 12),  # Middle finger
            (0, 13), (13, 14), (14, 15), (15, 16),  # Ring finger
            (0, 17), (17, 18), (18, 19), (19, 20)  # Pinky
        ]

        for connection in connections:
            start_point = (int(landmarks[connection[0]]['x'] * self.width()),
                           int(landmarks[connection[0]]['y'] * self.height()))
            end_point = (int(landmarks[connection[1]]['x'] * self.width()),
                         int(landmarks[connection[1]]['y'] * self.height()))
            painter.drawLine(start_point[0], start_point[1], end_point[0], end_point[1])

    def update_landmarks(self, landmarks, received=False):
        if received:
            self.received_landmarks = landmarks
        else:
            self.landmarks = landmarks
        self.update()

    def set_winner(self, winner):
        self.winner = winner
        self.update()

