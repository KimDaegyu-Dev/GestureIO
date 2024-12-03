from src.utils.constants import HandLandmarks, GestureType

class GestureRecognizer:
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

    def _is_thumb_extended(self, hand, is_right_hand: bool) -> bool:
        thumb_tip = hand[HandLandmarks.THUMB_TIP].x
        thumb_ip = hand[HandLandmarks.THUMB_IP].x
        return (thumb_tip > thumb_ip) if is_right_hand else (thumb_tip < thumb_ip)

    def _are_fingers_extended(self, hand) -> list[bool]:
        return [
            hand[tip].y < hand[pip].y
            for tip, pip in zip(self.finger_tips, self.finger_pips)
        ]

    def get_finger_status(self, hand, is_right_hand: bool) -> list[int]:
        fingers = []
        fingers.append(1 if self._is_thumb_extended(hand, is_right_hand) else 0)
        fingers.extend([1 if extended else 0 for extended in self._are_fingers_extended(hand)])
        return fingers

    def recognize_gesture(self, hand, is_right_hand: bool) -> str:
        fingers_status = self.get_finger_status(hand, is_right_hand)
        for gesture, pattern in self.gesture_patterns.items():
            if fingers_status == pattern:
                return gesture
        return GestureType.UNKNOWN

