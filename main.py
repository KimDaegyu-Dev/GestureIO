import cv2
import mediapipe as mp
import pyautogui
import time
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import QTimer
from drawKeyPoint import TransparentWindow

# Mediapipe 초기화
mp_hands = mp.solutions.hands
mp_drawing = mp.solutions.drawing_utils
hands = mp_hands.Hands()

# 비디오 캡처 초기화
cap = cv2.VideoCapture(0)

# 화면 크기 가져오기
screen_width, screen_height = pyautogui.size()

# 이전 커서 위치 초기화
prev_cursor_x, prev_cursor_y = screen_width // 2, screen_height // 2

# 디바운싱을 위한 변수 초기화
debounce_time = 0.1  # 100ms
last_move_time = time.time()

# PyQt5 애플리케이션 초기화
app = QApplication([])

# TransparentWindow 객체 생성
window = TransparentWindow(0, 0, screen_width, screen_height, 'green', 5)

def detect_gesture(hand_landmarks):
    # 엄지와 검지의 거리 계산
    thumb_tip = hand_landmarks.landmark[mp_hands.HandLandmark.THUMB_TIP]
    index_tip = hand_landmarks.landmark[mp_hands.HandLandmark.INDEX_FINGER_TIP]
    distance = ((thumb_tip.x - index_tip.x) ** 2 + (thumb_tip.y - index_tip.y) ** 2) ** 0.5
    
    # 특정 거리 이하이면 클릭으로 간주
    if distance < 0.05:
        return "click"
    return "move"

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
            cursor_x = int(wrist.x * screen_width)
            cursor_y = int(wrist.y * screen_height)
            
            # 디바운싱: 일정 시간 간격으로만 커서 이동
            current_time = time.time()
            if current_time - last_move_time > debounce_time:
                move_x = cursor_x - prev_cursor_x
                move_y = cursor_y - prev_cursor_y
                pyautogui.move(move_x, move_y)
                
                # 이전 커서 위치 업데이트
                prev_cursor_x, prev_cursor_y = cursor_x, cursor_y
                last_move_time = current_time
            
            # 제스처 인식
            gesture = detect_gesture(hand_landmarks)
            if gesture == "click":
                # PyQt5를 통해 클릭 이벤트 처리
                QTimer.singleShot(0, lambda: pyautogui.click())

    # 화면에 출력
    cv2.imshow('Hand Tracking', image)

    if cv2.waitKey(10) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
app.exec_()