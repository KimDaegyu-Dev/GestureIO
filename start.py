import sys
import cv2
import pyautogui
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import QTimer
from src.core.hand_tracker import HandTracker
from src.core.window_manager import WindowManager
from src.ui.transparent_window import TransparentWindow
from src.ui.program_selector import ProgramSelector
from src.utils.data_classes import WindowConfig
from src.network.landmark_sharing import LandmarkSharing

def run_main_application():
    app = QApplication([])
    screen_width, screen_height = pyautogui.size()
    
    window_config = WindowConfig(
        x=0, y=0,
        width=screen_width,
        height=screen_height,
        pen_color='green',
        pen_size=2
    )
    
    window = TransparentWindow(window_config)
    hand_tracker = HandTracker()
    window_manager = WindowManager()
    cap = cv2.VideoCapture(0)

    def update_landmarks():
        ret, frame = cap.read()
        if not ret:
            return

        result = hand_tracker.process_frame(frame)
        if result:
            window.setKeypoints(*result)
        window_manager.ensure_python_is_frontmost()

    timer = QTimer()
    timer.timeout.connect(update_landmarks)
    timer.start(10)  # 10ms interval for frame capture

    try:
        app.exec_()
    finally:
        cap.release()

def run_landmark_sharing():
    app = QApplication([])
    landmark_sharing = LandmarkSharing()
    landmark_sharing.show()
    try:
        app.exec_()
    finally:
        landmark_sharing.cleanup()

def main():
    app = QApplication(sys.argv)
    selector = ProgramSelector()
    selected_program = selector.get_selected_program()

    if selected_program == "main":
        run_main_application()
    elif selected_program == "landmark":
        run_landmark_sharing()
    else:
        print("No program selected. Exiting.")

if __name__ == "__main__":
    main()

