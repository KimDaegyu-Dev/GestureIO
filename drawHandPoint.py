from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QPainter, QPen, QColor
from PyQt5.QtWidgets import QApplication, QMainWindow
import mediapipe as mp
import cv2
from SimpleFingerClassfication import FingerStatus
from handAction import HandAction
from ManageProcess import ManageProcess
import pyautogui
class TransparentWindow(QMainWindow):
    def __init__(self, x: int, y: int, width: int, height: int, pen_color: str, pen_size: int):
        super().__init__()
        self.highlight_x = x
        self.highlight_y = y
        self.highlight_width = width
        self.highlight_height = height
        self.pen_color = pen_color
        self.pen_size = pen_size
        self.left_hand_keypoints = []
        self.right_hand_keypoints = []
        self.connections = []
        self.initUI()

    def initUI(self):
        self.setGeometry(self.highlight_x, self.highlight_y, self.highlight_width, self.highlight_height)
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.Tool)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setAttribute(Qt.WA_TransparentForMouseEvents)  # 마우스 이벤트를 투명하게 처리
        self.show()

    def setKeypoints(self, left_hand_keypoints, right_hand_keypoints, connections):
        self.left_hand_keypoints = left_hand_keypoints
        self.right_hand_keypoints = right_hand_keypoints
        self.connections = connections
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        pen = QPen(QColor(self.pen_color), self.pen_size)
        painter.setPen(pen)

        for keypoints in [self.left_hand_keypoints, self.right_hand_keypoints]:
            if keypoints:
                for point in keypoints:
                    x = int(point.x * self.width())
                    y = int(point.y * self.height())
                    painter.drawEllipse(x - 5, y - 5, 10, 10)

                for connection in self.connections:
                    start_idx, end_idx = connection
                    if start_idx < len(keypoints) and end_idx < len(keypoints):
                        start_point = keypoints[start_idx]
                        end_point = keypoints[end_idx]
                        start_x = int(start_point.x * self.width())
                        start_y = int(start_point.y * self.height())
                        end_x = int(end_point.x * self.width())
                        end_y = int(end_point.y * self.height())
                        painter.drawLine(start_x, start_y, end_x, end_y)

def main():
    app = QApplication([])
    screen_width, screen_height = pyautogui.size()  # 화면 크기 설정
    window = TransparentWindow(0, 0, screen_width, screen_height, 'green', 2)
    hand_action = HandAction()
    finger_status = FingerStatus()
    manage_process = ManageProcess()
    mp_hands = mp.solutions.hands
    hands = mp_hands.Hands(max_num_hands=2, min_detection_confidence=0.5, min_tracking_confidence=0.9)

    cap = cv2.VideoCapture(0)

    def update_landmarks():
        ret, frame = cap.read()
        if not ret:
            return

        frame = cv2.flip(frame, 1)
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = hands.process(frame_rgb)

        left_hand_keypoints = []
        right_hand_keypoints = []
        if results.multi_hand_landmarks and results.multi_handedness:
            for hand_landmarks, handedness in zip(results.multi_hand_landmarks, results.multi_handedness):
                if handedness.classification[0].label == 'Left':
                    left_hand_keypoints = hand_landmarks.landmark
                    leftstatus = finger_status.get_left_finger_status(hand_landmarks)
                    # hand_action.print_finger_position(left_index_finger_tip)
                    hand_action.watchGesture(hand_landmarks.landmark, finger_status.recognize_gesture(leftstatus))

                    # print(process.get_process())
                elif handedness.classification[0].label == 'Right':
                    right_hand_keypoints = hand_landmarks.landmark
                    rightstatus = finger_status.get_right_finger_status(hand_landmarks)
                    hand_action.watchGesture(hand_landmarks.landmark, finger_status.recognize_gesture(rightstatus), isLeft=False)
                    # print("right: ", finger_status.recognize_gesture(rightstatus))
            window.setKeypoints(left_hand_keypoints, right_hand_keypoints, mp_hands.HAND_CONNECTIONS)
        manage_process.ensure_python_is_frontmost()

    timer = QTimer()
    timer.timeout.connect(update_landmarks)
    timer.start(10)  # 10ms 간격으로 프레임 캡처

    app.exec_()
    cap.release()

if __name__ == "__main__":
    main()
