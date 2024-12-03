from dataclasses import dataclass
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QPainter, QPen, QColor
from PyQt5.QtWidgets import QApplication, QMainWindow
import mediapipe as mp
import cv2
from SimpleFingerClassfication import FingerStatus
from handAction import HandAction
from ManageProcess import ManageProcess
import pyautogui

@dataclass
class WindowConfig:
    x: int
    y: int
    width: int
    height: int
    pen_color: str
    pen_size: int

class TransparentWindow(QMainWindow):
    def __init__(self, config):
        super().__init__()
        self.config = config
        self.left_hand_keypoints = []
        self.right_hand_keypoints = []
        self.connections = []
        self.initUI()

    def initUI(self):
        """UI 초기화 및 윈도우 설정"""
        self.setGeometry(
            self.config.x,
            self.config.y,
            self.config.width,
            self.config.height
        )
        self._set_window_attributes()
        self.show()

    def _set_window_attributes(self):
        """윈도우 속성 설정"""
        self.setWindowFlags(
            Qt.FramelessWindowHint |
            Qt.WindowStaysOnTopHint |
            Qt.Tool
        )
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setAttribute(Qt.WA_TransparentForMouseEvents)

    def setKeypoints(self, left_hand_keypoints, right_hand_keypoints, connections):
        """손의 키포인트 설정"""
        self.left_hand_keypoints = left_hand_keypoints
        self.right_hand_keypoints = right_hand_keypoints
        self.connections = connections
        self.update()

    def paintEvent(self, event):
        """손의 키포인트와 연결선 그리기"""
        painter = QPainter(self)
        pen = QPen(QColor(self.config.pen_color), self.config.pen_size * 4)
        painter.setPen(pen)

        for keypoints in [self.left_hand_keypoints, self.right_hand_keypoints]:
            if keypoints:
                self._draw_keypoints(painter, keypoints)
                self._draw_connections(painter, keypoints)

    def _draw_keypoints(self, painter, keypoints):
        """키포인트 그리기"""
        for point in keypoints:
            x = int(point.x * self.width())
            y = int(point.y * self.height())
            painter.drawEllipse(x - 5, y - 5, 10, 10)

    def _draw_connections(self, painter, keypoints):
        """키포인트 간 연결선 그리기"""
        for start_idx, end_idx in self.connections:
            if start_idx < len(keypoints) and end_idx < len(keypoints):
                start_point = keypoints[start_idx]
                end_point = keypoints[end_idx]
                start_x = int(start_point.x * self.width())
                start_y = int(start_point.y * self.height())
                end_x = int(end_point.x * self.width())
                end_y = int(end_point.y * self.height())
                painter.drawLine(start_x, start_y, end_x, end_y)

class HandTracker:
    def __init__(self):
        """손 추적 초기화"""
        self.mp_hands = mp.solutions.hands
        self.hands = self.mp_hands.Hands(
            max_num_hands=2,
            min_detection_confidence=0.5,
            min_tracking_confidence=0.8
        )
        self.finger_status = FingerStatus()
        self.hand_action = HandAction()

    def process_frame(self, frame):
        """프레임에서 손 감지 및 처리"""
        frame = cv2.flip(frame, 1)
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = self.hands.process(frame_rgb)
        
        if not results.multi_hand_landmarks or not results.multi_handedness:
            return None

        left_hand_keypoints = []
        right_hand_keypoints = []

        for hand_landmarks, handedness in zip(
            results.multi_hand_landmarks,
            results.multi_handedness
        ):
            self._process_hand(hand_landmarks, handedness,left_hand_keypoints, right_hand_keypoints)
        return left_hand_keypoints, right_hand_keypoints, self.mp_hands.HAND_CONNECTIONS

    def _process_hand(self, hand_landmarks, handedness, left_hand_keypoints, right_hand_keypoints):
        """각 손에 대한 처리"""
        is_left = handedness.classification[0].label == 'Left'
        if is_left:
            status = self.finger_status.get_finger_status(hand_landmarks, True)
            self.hand_action.watchGesture(
                hand_landmarks.landmark,
                self.finger_status.recognize_gesture(status),
                isLeft=True
            )
            left_hand_keypoints.extend(hand_landmarks.landmark)
        else:
            status = self.finger_status.get_finger_status(hand_landmarks, False)
            self.hand_action.watchGesture(
                hand_landmarks.landmark,
                self.finger_status.recognize_gesture(status),
                isLeft=False
            )
            right_hand_keypoints.extend(hand_landmarks.landmark)
        

def main():
    """메인 실행 함수"""
    app = QApplication([])
    screen_width, screen_height = pyautogui.size()
    
    window_config = WindowConfig(
        x=0, y=0,
        width=screen_width,
        height=screen_height,
        pen_color='green',
        pen_size=2
    )
    
    window = TransparentWindow(window_config)
    hand_tracker = HandTracker()
    manage_process = ManageProcess()
    cap = cv2.VideoCapture(0)

    def update_landmarks():
        ret, frame = cap.read()
        if not ret:
            return

        result = hand_tracker.process_frame(frame)
        if result:
            window.setKeypoints(*result)
        manage_process.ensure_python_is_frontmost()

    timer = QTimer()
    timer.timeout.connect(update_landmarks)
    timer.start(10)  # 10ms 간격으로 프레임 캡처

    try:
        app.exec_()
    finally:
        cap.release()

if __name__ == "__main__":
    main()
