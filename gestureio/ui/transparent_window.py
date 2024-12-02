from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QPainter, QPen, QColor, QFont
import logging

logger = logging.getLogger(__name__)

class TransparentWindow(QWidget):
    """투명한 오버레이 윈도우를 생성하는 클래스"""
    
    gesture_detected = pyqtSignal(str)  # 제스처 감지 시그널
    
    def __init__(self):
        super().__init__()
        self.initUI()
        self.current_gesture = None
        self.hand_landmarks = None
        
    def initUI(self):
        """UI 초기화"""
        # 윈도우 설정
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setWindowFlags(
            Qt.FramelessWindowHint |
            Qt.WindowStaysOnTopHint |
            Qt.Tool
        )
        
        # 레이아웃 설정
        layout = QVBoxLayout()
        self.gesture_label = QLabel()
        self.gesture_label.setStyleSheet("""
            QLabel {
                color: white;
                background-color: rgba(0, 0, 0, 150);
                padding: 5px;
                border-radius: 5px;
                font-size: 14px;
            }
        """)
        layout.addWidget(self.gesture_label)
        layout.addStretch()
        self.setLayout(layout)
        
    def update_gesture(self, gesture_name: str, landmarks=None):
        """제스처 정보 업데이트
        
        Args:
            gesture_name: 감지된 제스처 이름
            landmarks: 손 랜드마크 좌표 (선택사항)
        """
        self.current_gesture = gesture_name
        self.hand_landmarks = landmarks
        self.gesture_label.setText(f"Gesture: {gesture_name}")
        self.update()
        self.gesture_detected.emit(gesture_name)
        
    def paintEvent(self, event):
        """손 랜드마크와 제스처 시각화"""
        if self.hand_landmarks:
            painter = QPainter(self)
            painter.setRenderHint(QPainter.Antialiasing)
            
            # 랜드마크 그리기
            pen = QPen(QColor(0, 255, 0), 2)
            painter.setPen(pen)
            
            for landmark in self.hand_landmarks:
                x, y = landmark.x * self.width(), landmark.y * self.height()
                painter.drawEllipse(int(x), int(y), 5, 5)
                
    def mousePressEvent(self, event):
        """드래그를 위한 마우스 이벤트"""
        if event.button() == Qt.LeftButton:
            self.drag_position = event.globalPos() - self.frameGeometry().topLeft()
            event.accept()
            
    def mouseMoveEvent(self, event):
        """윈도우 드래그 구현"""
        if event.buttons() == Qt.LeftButton:
            self.move(event.globalPos() - self.drag_position)
            event.accept()