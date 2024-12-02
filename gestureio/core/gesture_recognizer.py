from dataclasses import dataclass
from typing import List, Optional
import numpy as np
import mediapipe as mp
from ..utils.constants import GestureType, FINGER_TIPS, FINGER_PIPS

@dataclass
class HandLandmark:
    x: float
    y: float
    z: float

class GestureRecognizer:
    def __init__(self):
        self.mp_hands = mp.solutions.hands
        self.previous_gesture = GestureType.UNKNOWN
        
    def get_finger_status(self, hand_landmarks: List[HandLandmark], is_left: bool = True) -> List[int]:
        """손가락의 펼침/접힘 상태를 확인합니다.

        Args:
            hand_landmarks: 손의 랜드마크 좌표 리스트
            is_left: 왼손 여부

        Returns:
            List[int]: 각 손가락의 상태 (0: 접힘, 1: 펼침)
        """
        fingers = []
        
        # 엄지 손가락 확인
        thumb_tip = hand_landmarks[FINGER_TIPS[0]]
        thumb_pip = hand_landmarks[FINGER_PIPS[0]]
        fingers.append(1 if (thumb_tip.x > thumb_pip.x) == is_left else 0)
        
        # 나머지 손가락 확인
        for tip, pip in zip(FINGER_TIPS[1:], FINGER_PIPS[1:]):
            fingers.append(1 if hand_landmarks[tip].y < hand_landmarks[pip].y else 0)
            
        return fingers

    def recognize_gesture(self, finger_status: List[int]) -> GestureType:
        """손가락 상태를 기반으로 제스처를 인식합니다.

        Args:
            finger_status: 손가락 상태 리스트

        Returns:
            GestureType: 인식된 제스처 타입
        """
        gesture_map = {
            (0, 0, 0, 0, 0): GestureType.FIST,
            (0, 1, 0, 0, 0): GestureType.POINT,
            (1, 1, 1, 1, 1): GestureType.OPEN,
            (0, 1, 1, 0, 0): GestureType.TWO,
            (1, 1, 0, 0, 0): GestureType.OKAY
        }
        return gesture_map.get(tuple(finger_status), GestureType.UNKNOWN)