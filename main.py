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

    # BGR 이미지를 RGB로 변환
    image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    image.flags.writeable = False

    # Mediapipe로 손 키포인트 추출
    results = hands.process(image)

    # BGR로 다시 변환
    image.flags.writeable = True
    image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)

    # 손 키포인트 그리기 및 커서 제어
    if results.multi_hand_landmarks:
        for hand_landmarks in results.multi_hand_landmarks:
            keypoints = []
            for landmark in hand_landmarks.landmark:
                x = int(landmark.x * screen_width)
                y = int(landmark.y * screen_height)
                keypoints.append((x, y))
            window.setKeypoints(keypoints)
            
            # 손목 좌표 가져오기
            wrist = hand_landmarks.landmark[mp_hands.HandLandmark.WRIST]
            cursor_controller.move_cursor(wrist)
            
            # 제스처 인식
            gesture = gesture_detector.detect_gesture(hand_landmarks)
            if gesture == "click":
                QTimer.singleShot(0, cursor_controller.click)

    # 화면에 출력
    cv2.imshow('Hand Tracking', image)

    if cv2.waitKey(10) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
app.exec_()