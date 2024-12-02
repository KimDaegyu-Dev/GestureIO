import cv2
import numpy as np
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QImage, QPixmap
import mediapipe as mp
from typing import List, Tuple
import logging

logger = logging.getLogger(__name__)

class HandVisualizer:
    """손 동작 시각화를 위한 클래스"""
    
    def __init__(self):
        self.mp_drawing = mp.solutions.drawing_utils
        self.mp_hands = mp.solutions.hands
        self.drawing_styles = mp.solutions.drawing_styles
        
        # 시각화 스타일 설정
        self.landmark_style = self.mp_drawing.DrawingSpec(
            color=(0, 255, 0),
            thickness=2,
            circle_radius=2
        )
        self.connection_style = self.mp_drawing.DrawingSpec(
            color=(255, 255, 255),
            thickness=1
        )
        
    def draw_landmarks(self, image: np.ndarray, results) -> np.ndarray:
        """손 랜드마크를 이미지에 그립니다.
        
        Args:
            image: 원본 이미지
            results: mediapipe 손 인식 결과
            
        Returns:
            np.ndarray: 랜드마크가 그려진 이미지
        """
        if results.multi_hand_landmarks:
            for hand_landmarks in results.multi_hand_landmarks:
                self.mp_drawing.draw_landmarks(
                    image,
                    hand_landmarks,
                    self.mp_hands.HAND_CONNECTIONS,
                    self.landmark_style,
                    self.connection_style
                )
        return image
        
    def draw_gesture_info(self, image: np.ndarray, gesture: str, 
                         position: Tuple[int, int]) -> np.ndarray:
        """제스처 정보를 이미지에 표시합니다.
        
        Args:
            image: 원본 이미지
            gesture: 감지된 제스처 이름
            position: 텍스트 표시 위치 (x, y)
            
        Returns:
            np.ndarray: 정보가 추가된 이미지
        """
        font = cv2.FONT_HERSHEY_SIMPLEX
        cv2.putText(
            image,
            f"Gesture: {gesture}",
            position,
            font,
            1,
            (255, 255, 255),
            2,
            cv2.LINE_AA
        )
        return image
        
    def draw_finger_angles(self, image: np.ndarray, 
                          landmarks: List[mp.framework.formats.landmark_pb2.NormalizedLandmark]
                          ) -> np.ndarray:
        """손가락 각도를 시각화합니다.
        
        Args:
            image: 원본 이미지
            landmarks: 손 랜드마크 목록
            
        Returns:
            np.ndarray: 각도가 표시된 이미지
        """
        h, w, _ = image.shape
        
        # 각 손가락의 주요 포인트
        finger_points = [
            [4, 3, 2],  # 엄지
            [8, 7, 6],  # 검지
            [12, 11, 10],  # 중지
            [16, 15, 14],  # 약지
            [20, 19, 18]   # 소지
        ]
        
        for points in finger_points:
            # 각도 계산
            angle = self._calculate_angle(
                (landmarks[points[0]].x * w, landmarks[points[0]].y * h),
                (landmarks[points[1]].x * w, landmarks[points[1]].y * h),
                (landmarks[points[2]].x * w, landmarks[points[2]].y * h)
            )
            
            # 각도 표시
            pos = (int(landmarks[points[1]].x * w), int(landmarks[points[1]].y * h))
            cv2.putText(
                image,
                f"{angle:.1f}°",
                pos,
                cv2.FONT_HERSHEY_SIMPLEX,
                0.5,
                (255, 255, 0),
                1,
                cv2.LINE_AA
            )
            
        return image
        
    def _calculate_angle(self, p1: Tuple[float, float], 
                        p2: Tuple[float, float], 
                        p3: Tuple[float, float]) -> float:
        """세 점 사이의 각도를 계산합니다.
        
        Args:
            p1: 첫 번째 점 좌표
            p2: 두 번째 점 좌표 (각도의 정점)
            p3: 세 번째 점 좌표
            
        Returns:
            float: 각도 (도)
        """
        v1 = np.array([p1[0] - p2[0], p1[1] - p2[1]])
        v2 = np.array([p3[0] - p2[0], p3[1] - p2[1]])
        
        cosine = np.dot(v1, v2) / (np.linalg.norm(v1) * np.linalg.norm(v2))
        angle = np.arccos(np.clip(cosine, -1.0, 1.0))
        
        return np.degrees(angle)
        
    def convert_to_qimage(self, image: np.ndarray) -> QImage:
        """OpenCV 이미지를 QImage로 변환합니다.
        
        Args:
            image: OpenCV 이미지
            
        Returns:
            QImage: 변환된 이미지
        """
        height, width, channel = image.shape
        bytes_per_line = 3 * width
        return QImage(
            image.data,
            width,
            height,
            bytes_per_line,
            QImage.Format_RGB888
        ).rgbSwapped()