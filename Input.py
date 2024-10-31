import cv2
import mediapipe as mp
import time
from PyQt5.QtWidgets import QApplication
import PyXA
import pyautogui
class InputHandler:
    def __init__(self, threshold):
        self.threshold = threshold
        self.prev_distance = None
        self.prev_time = None

    def calculate_distance(self, point1, point2):
        return ((point1.x - point2.x) ** 2 + (point1.y - point2.y) ** 2) ** 0.5

    def calculate_midpoint(self, point1, point2):
        mid_x = (point1.x + point2.x) / 2
        mid_y = (point1.y + point2.y) / 2
        return mid_x, mid_y

    def process_landmarks(self, left_index_finger_tip, right_index_finger_tip):
        current_time = time.time()
        current_distance = self.calculate_distance(left_index_finger_tip, right_index_finger_tip)

        if self.prev_distance is not None and self.prev_time is not None:
            distance_change = self.prev_distance - current_distance
            time_change = current_time - self.prev_time
            speed = distance_change / time_change

            if speed > self.threshold:
                self.update_window_position(left_index_finger_tip, right_index_finger_tip)

        self.prev_distance = current_distance
        self.prev_time = current_time

    def update_window_position(self, left_index_finger_tip, right_index_finger_tip):
        mid_x, mid_y = self.calculate_midpoint(left_index_finger_tip, right_index_finger_tip)
        screen_width, screen_height = pyautogui.size()
        new_x = int(mid_x * screen_width)
        new_y = int(mid_y * screen_height)

        frontmost_app = PyXA.Application("Code")
        frontmost_window = frontmost_app.windows()[0]
        if frontmost_window:
            frontmost_window.position = [new_x, new_y]

def main():
    mp_hands = mp.solutions.hands
    hands = mp_hands.Hands()
    cap = cv2.VideoCapture(0)
    app = QApplication([])

    input_handler = InputHandler(threshold=0.01)  # 속도 임계값 설정

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        frame = cv2.flip(frame, 1)
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = hands.process(frame_rgb)

        if results.multi_hand_landmarks and results.multi_handedness:
            left_index_finger_tip = None
            right_index_finger_tip = None

            for hand_landmarks, handedness in zip(results.multi_hand_landmarks, results.multi_handedness):
                if handedness.classification[0].label == 'Left':
                    left_index_finger_tip = hand_landmarks.landmark[mp_hands.HandLandmark.INDEX_FINGER_TIP]
                elif handedness.classification[0].label == 'Right':
                    right_index_finger_tip = hand_landmarks.landmark[mp_hands.HandLandmark.INDEX_FINGER_TIP]

            if left_index_finger_tip and right_index_finger_tip:
                input_handler.process_landmarks(left_index_finger_tip, right_index_finger_tip)

        cv2.imshow('Webcam', frame)
        if cv2.waitKey(10) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()
    app.exec_()

if __name__ == "__main__":
    main()