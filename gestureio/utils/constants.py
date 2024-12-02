from enum import Enum

class GestureType(Enum):
    UNKNOWN = "unknown"
    FIST = "fist"
    POINT = "point"
    STANDBY = "standby"
    OPEN = "open"
    TWO = "two"
    THREE = "three"
    FOUR = "four"
    OKAY = "okay"

# 미디어파이프 설정
MEDIAPIPE_CONFIG = {
    "max_num_hands": 2,
    "min_detection_confidence": 0.5,
    "min_tracking_confidence": 0.8
}

# 손가락 랜드마크 인덱스
FINGER_TIPS = [4, 8, 12, 16, 20]  # 엄지부터 새끼손가락까지의 끝점
FINGER_PIPS = [3, 6, 10, 14, 18]  # 각 손가락의 중간 관절