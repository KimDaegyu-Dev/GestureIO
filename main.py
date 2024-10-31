import cv2
import mediapipe as mp
import pyautogui
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import QTimer
from drawKeyPoint import TransparentWindow
from Gesture import Gesture
from Cursor import Cursor

# Mediapipe 초기화
mp_hands = mp.solutions.hands
hands = mp_hands.Hands()

# 비디오 캡처 초기화
cap = cv2.VideoCapture(0)

# 화면 크기 가져오기
screen_width, screen_height = pyautogui.size()

# PyQt5 애플리케이션 초기화
app = QApplication([])

# TransparentWindow 객체 생성
window = TransparentWindow(0, 0, screen_width, screen_height, 'green', 5)

# Gesture 및 Cursor 객체 생성
gesture_detector = Gesture()
cursor_controller = Cursor(screen_width, screen_height)

while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        break

    # 프레임을 좌우 반전
    frame = cv2.flip(frame, 1)

    # BGR 이미지를 RGB로 변환
    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    # Mediapipe로 손 추정
    results = hands.process(frame_rgb)

    # 손 키포인트 그리기 및 커서 제어
    if results.multi_hand_landmarks:
        for hand_landmarks in results.multi_hand_landmarks:
            keypoints = []
            for landmark in hand_landmarks.landmark:
                x = int(landmark.x * screen_width)
                y = int(landmark.y * screen_height)
                keypoints.append((x, y))
            window.setKeypoints(keypoints)
            
            # 검지 손가락 끝 좌표 가져오기
            index_finger_tip = hand_landmarks.landmark[mp_hands.HandLandmark.INDEX_FINGER_TIP]
            cursor_controller.move_cursor(index_finger_tip)
            
            # 제스처 인식
            gesture = gesture_detector.detect_gesture(hand_landmarks)
            if gesture == "click":
                QTimer.singleShot(0, cursor_controller.click)

    # 프레임을 표시
    cv2.imshow('Webcam', frame)

    if cv2.waitKey(10) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
app.exec_()