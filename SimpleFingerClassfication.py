from typing import List
from mediapipe.framework.formats.landmark_pb2 import NormalizedLandmarkList

class HandLandmarks:
    THUMB_TIP = 4
    THUMB_IP = 3
    INDEX_TIP = 8
    MIDDLE_TIP = 12
    RING_TIP = 16
    PINKY_TIP = 20
    INDEX_PIP = 6
    MIDDLE_PIP = 10
    RING_PIP = 14
    PINKY_PIP = 18

class GestureType:
    FIST = 'fist'
    POINT = 'point'
    STANDBY = 'standby'
    OPEN = 'open'
    TWO = 'two'
    THREE = 'three'
    FOUR = 'four'
    OKAY = 'okay'
    UNKNOWN = 'unknown'

class FingerStatus:
    def __init__(self):
        self.finger_tips = [
            HandLandmarks.INDEX_TIP,
            HandLandmarks.MIDDLE_TIP,
            HandLandmarks.RING_TIP,
            HandLandmarks.PINKY_TIP
        ]
        self.finger_pips = [
            HandLandmarks.INDEX_PIP,
            HandLandmarks.MIDDLE_PIP,
            HandLandmarks.RING_PIP,
            HandLandmarks.PINKY_PIP
        ]
        self.gesture_patterns = {
            GestureType.FIST: [0, 0, 0, 0, 0],
            GestureType.POINT: [0, 1, 0, 0, 0],
            GestureType.STANDBY: [1, 1, 0, 0, 0],
            GestureType.OPEN: [1, 1, 1, 1, 1],
            GestureType.TWO: [0, 1, 1, 0, 0],
            GestureType.THREE: [0, 1, 1, 1, 0],
            GestureType.FOUR: [0, 1, 1, 1, 1],
            GestureType.OKAY: [1, 0, 1, 1, 1]
        }

    def _is_thumb_extended(self, hand: NormalizedLandmarkList, is_right_hand: bool) -> bool:
        """엄지손가락이 펴져있는지 확인합니다."""
        thumb_tip = hand.landmark[HandLandmarks.THUMB_TIP].x
        thumb_ip = hand.landmark[HandLandmarks.THUMB_IP].x
        return (thumb_tip > thumb_ip) if is_right_hand else (thumb_tip < thumb_ip)

    def _are_fingers_extended(self, hand: NormalizedLandmarkList) -> List[bool]:
        """나머지 손가락들이 펴져있는지 확인합니다."""
        return [
            hand.landmark[tip].y < hand.landmark[pip].y
            for tip, pip in zip(self.finger_tips, self.finger_pips)
        ]

    def get_finger_status(self, hand: NormalizedLandmarkList, is_right_hand: bool) -> List[int]:
        """
        손가락의 상태(펴짐/접힘)를 확인합니다.

        Args:
            hand: 손의 랜드마크 정보
            is_right_hand: 오른손 여부

        Returns:
            List[int]: 각 손가락의 상태 (0: 접힘, 1: 펴짐)
        """
        fingers = []
        fingers.append(1 if self._is_thumb_extended(hand, is_right_hand) else 0)
        fingers.extend([1 if extended else 0 for extended in self._are_fingers_extended(hand)])
        return fingers

    def recognize_gesture(self, fingers_status: List[int]) -> str:
        """
        손가락 상태를 기반으로 제스처를 인식합니다.

        Args:
            fingers_status: 각 손가락의 상태 리스트

        Returns:
            str: 인식된 제스처 이름
        """
        for gesture, pattern in self.gesture_patterns.items():
            if fingers_status == pattern:
                return gesture
        return GestureType.UNKNOWN
            
    

