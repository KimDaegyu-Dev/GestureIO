import cv2
import mediapipe as mp
from src.utils.data_classes import Point
from src.core.gesture_recognizer import GestureRecognizer
from src.core.hand_action import HandAction

class HandTracker:
    def __init__(self):
        self.mp_hands = mp.solutions.hands
        self.hands = self.mp_hands.Hands(
            max_num_hands=1,
            min_detection_confidence=0.5,
            min_tracking_confidence=0.8
        )
        self.gesture_recognizer = GestureRecognizer()
        self.hand_action = HandAction()

    def process_frame(self, frame, landmark_sharing=False):
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
            self._process_hand(hand_landmarks, handedness, left_hand_keypoints, right_hand_keypoints, landmark_sharing)
        return left_hand_keypoints, right_hand_keypoints, self.mp_hands.HAND_CONNECTIONS

    def _process_hand(self, hand_landmarks, handedness, left_hand_keypoints, right_hand_keypoints, landmark_sharing):
        is_left = handedness.classification[0].label == 'Left'
        keypoints = [Point(lm.x, lm.y, lm.z) for lm in hand_landmarks.landmark]

            # 제스처 인식
        gesture = self.gesture_recognizer.recognize_gesture(keypoints, is_left)
            
        if not landmark_sharing:
            # 제스처 액션 처리
            self.hand_action.watch_gesture(hand_landmarks.landmark, gesture, is_left)
        
        # 키포인트 저장
        if is_left:
            left_hand_keypoints.extend(keypoints)
        else:
            right_hand_keypoints.extend(keypoints)

        return gesture