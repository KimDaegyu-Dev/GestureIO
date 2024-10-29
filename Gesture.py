import mediapipe as mp

class Gesture:
    def __init__(self):
        self.mp_hands = mp.solutions.hands

    def detect_gesture(self, hand_landmarks):
        # 엄지와 검지의 거리 계산
        thumb_tip = hand_landmarks.landmark[self.mp_hands.HandLandmark.THUMB_TIP]
        index_tip = hand_landmarks.landmark[self.mp_hands.HandLandmark.INDEX_FINGER_TIP]
        distance = ((thumb_tip.x - index_tip.x) ** 2 + (thumb_tip.y - index_tip.y) ** 2) ** 0.5
        
        # 특정 거리 이하이면 클릭으로 간주
        if distance < 0.05:
            return "click"
        return "move"