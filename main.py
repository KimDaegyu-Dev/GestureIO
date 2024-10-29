import cv2
import mediapipe as mp
import pyautogui

# Mediapipe 초기화
mp_hands = mp.solutions.hands
hands = mp_hands.Hands()
mp_drawing = mp.solutions.drawing_utils

# 웹캠 초기화
cap = cv2.VideoCapture(0)

# 화면 크기 가져오기
screen_width, screen_height = pyautogui.size()

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
            mp_drawing.draw_landmarks(image, hand_landmarks, mp_hands.HAND_CONNECTIONS)
            
            # 손목 좌표 가져오기
            wrist = hand_landmarks.landmark[mp_hands.HandLandmark.WRIST]
            cursor_x = int(wrist.x * screen_width)
            cursor_y = int(wrist.y * screen_height)
            
            # 마우스 커서 이동
            pyautogui.moveTo(cursor_x, cursor_y)
            
            # 제스처 인식
            gesture = detect_gesture(hand_landmarks)
            if gesture == "click":
                pyautogui.click()

    # 화면에 출력
    cv2.imshow('Hand Tracking', image)

    if cv2.waitKey(10) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()