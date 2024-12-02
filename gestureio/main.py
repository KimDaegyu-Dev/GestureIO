# main.py에 추가
from ui.transparent_window import TransparentWindow
from ui.visualization import HandVisualizer

class GestureIOApp:
    def __init__(self):
        # ... 기존 초기화 코드 ...
        self.overlay = TransparentWindow()
        self.visualizer = HandVisualizer()
        
    def process_frame(self):
        ret, frame = self.cap.read()
        if not ret:
            return
            
        results = self.hands.process(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
        
        # 시각화
        frame = self.visualizer.draw_landmarks(frame, results)
        if results.multi_hand_landmarks:
            gesture = self.gesture_recognizer.recognize_gesture(...)
            frame = self.visualizer.draw_gesture_info(frame, gesture, (10, 30))
            self.overlay.update_gesture(gesture, results.multi_hand_landmarks[0])
            
        # UI 업데이트
        self.overlay.show()