from dataclasses import dataclass
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QPainter, QPen, QColor
from PyQt5.QtWidgets import QApplication, QMainWindow
import mediapipe as mp
import cv2
import pyautogui
import PyXA
import Quartz
import AppKit
import numpy as np
from typing import List
from mediapipe.framework.formats.landmark_pb2 import NormalizedLandmarkList

@dataclass
class Point:
    x: float
    y: float
    z: float = 0.0

@dataclass
class WindowInfo:
    name: str
    x: float
    y: float
    height: float
    width: float

@dataclass
class WindowConfig:
    x: int
    y: int
    width: int
    height: int
    pen_color: str
    pen_size: int

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
        thumb_tip = hand.landmark[HandLandmarks.THUMB_TIP].x
        thumb_ip = hand.landmark[HandLandmarks.THUMB_IP].x
        return (thumb_tip > thumb_ip) if is_right_hand else (thumb_tip < thumb_ip)

    def _are_fingers_extended(self, hand: NormalizedLandmarkList) -> List[bool]:
        return [
            hand.landmark[tip].y < hand.landmark[pip].y
            for tip, pip in zip(self.finger_tips, self.finger_pips)
        ]

    def get_finger_status(self, hand: NormalizedLandmarkList, is_right_hand: bool) -> List[int]:
        fingers = []
        fingers.append(1 if self._is_thumb_extended(hand, is_right_hand) else 0)
        fingers.extend([1 if extended else 0 for extended in self._are_fingers_extended(hand)])
        return fingers

    def recognize_gesture(self, fingers_status: List[int]) -> str:
        for gesture, pattern in self.gesture_patterns.items():
            if fingers_status == pattern:
                return gesture
        return GestureType.UNKNOWN

class WindowManager:
    IGNORED_APPS = {'Window Server', '스크린샷', 'screencapture'}
    WINDOW_LIST_OPTIONS = Quartz.kCGWindowListOptionOnScreenOnly | Quartz.kCGWindowListExcludeDesktopElements

class ManageProcess:
    def __init__(self):
        self.python_pids = self.get_python_processes()

    def get_layer_order(self):
        window_list = Quartz.CGWindowListCopyWindowInfo(
            WindowManager.WINDOW_LIST_OPTIONS,
            Quartz.kCGNullWindowID
        )
        return [
            (window.get('kCGWindowOwnerName', 'Unknown'),
             window.get('kCGWindowOwnerPID', 'Unknown'))
            for window in window_list
        ]

    def get_frontmost_application_window(self):
        window_list = Quartz.CGWindowListCopyWindowInfo(
            WindowManager.WINDOW_LIST_OPTIONS,
            Quartz.kCGNullWindowID
        )
        frontmost_app_pid = (
            AppKit.NSWorkspace.sharedWorkspace()
            .frontmostApplication()
            .processIdentifier()
        )

        for window in window_list:
            if (window.get('kCGWindowLayer') == 0 and
                window.get('kCGWindowOwnerPID') == frontmost_app_pid):
                bounds = window.get('kCGWindowBounds')
                return [
                    window.get('kCGWindowOwnerPID'),
                    bounds['X'],
                    bounds['Y'],
                    bounds['Height'],
                    bounds['Width']
                ]
        return None

    def get_frontmost_app_pid(self):
        frontmost_app = (
            AppKit.NSWorkspace.sharedWorkspace()
            .frontmostApplication()
        )
        if frontmost_app.processIdentifier() == self.python_pids[0]:
            return self.get_next_frontmost_app_pid('Python')
        return frontmost_app.processIdentifier()

    def get_python_processes(self):
        running_apps = (
            AppKit.NSWorkspace.sharedWorkspace()
            .runningApplications()
        )
        return [
            app.processIdentifier()
            for app in running_apps
            if 'Python' in app.localizedName()
        ]

    def bring_window_to_front(self, pid):
        app = AppKit.NSRunningApplication.runningApplicationWithProcessIdentifier_(pid)
        if app:
            app.activateWithOptions_(AppKit.NSApplicationActivateIgnoringOtherApps)
            return True
        return False

    def ensure_python_is_frontmost(self):
        self.bring_window_to_front(self.python_pids[0])

    def get_next_frontmost_app_pid(self, name):
        window_order = self.get_layer_order()
        for i, (app_name, pid) in enumerate(window_order):
            if app_name == name and i + 1 < len(window_order):
                return window_order[i + 1][1]
        return None

    def get_window_at_position(self, x, y):
        window_list = Quartz.CGWindowListCopyWindowInfo(
            WindowManager.WINDOW_LIST_OPTIONS,
            Quartz.kCGNullWindowID
        )
        
        window_bounds_list = []
        for window in window_list:
            app_name = window.get('kCGWindowOwnerName', 'Unknown')
            if app_name in WindowManager.IGNORED_APPS:
                continue

            bounds = window.get('kCGWindowBounds')
            if (bounds['X'] <= x <= bounds['X'] + bounds['Width'] and
                bounds['Y'] <= y <= bounds['Y'] + bounds['Height']):
                pid = window.get('kCGWindowOwnerPID', 'Unknown')
                window_bounds_list.append((app_name, pid))
                
        return window_bounds_list

    def get_topmost_window_at_position(self, x, y):
        windows_at_position = self.get_window_at_position(x, y)
        window_order = self.get_layer_order()
        
        for app_name, pid in window_order:
            if (app_name, pid) in windows_at_position:
                if app_name == 'Python':
                    continue
                return app_name, pid
        return None

class HandAction:
    Z_THRESHOLD = 0.1
    CLICK_DISTANCE_THRESHOLD = 0.05
    MOVEMENT_THRESHOLD = 100

    def __init__(self):
        self.screen_width, self.screen_height = pyautogui.size()
        self.previous_gesture = 'unknown'
        self.previous_y = None
        self.mouse_down_executed = False
        self.cursor_x = 0
        self.cursor_y = 0
        self.manage_process = ManageProcess()
        self.prev_mid_x = None
        self.prev_mid_y = None
        self.current_position = np.array([0, 0])
        self.prev_process_pid = 0

    def get_application_window_info(self, pid):
        options = Quartz.kCGWindowListOptionOnScreenOnly | Quartz.kCGWindowListExcludeDesktopElements
        window_list = Quartz.CGWindowListCopyWindowInfo(options, Quartz.kCGNullWindowID)
        
        for window in window_list:
            if (window.get('kCGWindowLayer') == 0 and 
                window.get('kCGWindowOwnerPID') == pid):
                bounds = window.get('kCGWindowBounds')
                return WindowInfo(
                    name=window.get('kCGWindowOwnerName'),
                    x=bounds['X'],
                    y=bounds['Y'],
                    height=bounds['Height'],
                    width=bounds['Width']
                )
        return None

    def get_app_by_pid(self, pid):
        app_ref = AppKit.NSRunningApplication.runningApplicationWithProcessIdentifier_(pid)
        if app_ref:
            return PyXA.Application(app_ref.localizedName())
        return None

    def calculate_distance(self, point1, point2):
        p1 = np.array([point1.x, point1.y])
        p2 = np.array([point2.x, point2.y])
        return np.linalg.norm(p1 - p2)

    def calculate_midpoint(self, point1, point2):
        p1 = np.array([point1.x, point1.y])
        p2 = np.array([point2.x, point2.y])
        midpoint = (p1 + p2) / 2
        return midpoint[0], midpoint[1]

    def process_window_drag(self, index_finger_tip, thumb_tip):
        current_distance = self.calculate_distance(index_finger_tip, thumb_tip)
        if current_distance < self.CLICK_DISTANCE_THRESHOLD:
            self.update_window_position(index_finger_tip, thumb_tip)

    def update_window_position(self, index_finger_tip, thumb_tip):
        mid_x, mid_y = self.calculate_midpoint(index_finger_tip, thumb_tip)
        new_position = np.array([int(mid_x * self.screen_width), int(mid_y * self.screen_height)])
        
        window_info = self.manage_process.get_topmost_window_at_position(new_position[0], new_position[1])
        if not window_info:
            return

        (app_name, pid) = window_info
        if pid != self.prev_process_pid:
            self._handle_new_window(pid)

        self._update_window_position(new_position, pid)
        self.prev_process_pid = pid
        self.prev_mid_x, self.prev_mid_y = new_position

    def _handle_new_window(self, pid):
        self.prev_mid_x, self.prev_mid_y = None, None
        window_info = self.get_application_window_info(pid)
        if window_info:
            self.current_position = [window_info.x, window_info.y]

    def _update_window_position(self, new_position, pid):
        if self.prev_mid_x is None or self.prev_mid_y is None:
            return

        move_vector = new_position - np.array([self.prev_mid_x, self.prev_mid_y])

        if np.any(np.abs(move_vector) > self.MOVEMENT_THRESHOLD):
            return

        app = self.get_app_by_pid(pid)
        if app and app.windows():
            new_position = self.current_position + move_vector
            app.windows()[0].position = new_position.tolist()
            self.current_position = new_position

    def process_mouse_movement(self, index_finger_tip):
        self.cursor_x = int(index_finger_tip.x * self.screen_width)
        self.cursor_y = int(index_finger_tip.y * self.screen_height) - 5
        pyautogui.moveTo(self.cursor_x, self.cursor_y)

    def process_scroll(self, index_finger_tip, scroll_up=True):
        if self.previous_y is not None:
            current_y = int(index_finger_tip.y * self.screen_height)
            delta_y = current_y - self.previous_y
            if (scroll_up and delta_y > 0) or (not scroll_up and delta_y < 0):
                pyautogui.scroll(delta_y / 20)
        self.previous_y = int(index_finger_tip.y * self.screen_height)

    def watchGesture(self, hand_landmark, current_gesture, isLeft=True):
        index_finger_tip = hand_landmark[8]
        thumb_tip = hand_landmark[4]

        if self.previous_gesture == 'okay' and current_gesture == 'okay':
            self.process_window_drag(index_finger_tip, thumb_tip)

        elif self.previous_gesture == 'point' and current_gesture == 'point':
            self.process_mouse_movement(index_finger_tip)

        elif self.previous_gesture == 'point' and current_gesture == 'standby':
            pyautogui.click(self.cursor_x, self.cursor_y)

        if isLeft:
            if current_gesture == 'two' and self.previous_gesture == 'two':
                self.process_scroll(index_finger_tip, True)
            elif current_gesture == 'three' and self.previous_gesture == 'three':
                self.process_scroll(index_finger_tip, False)
        else:
            self._handle_right_hand_gestures(current_gesture, index_finger_tip)

        self.previous_gesture = current_gesture

    def _handle_right_hand_gestures(self, current_gesture, index_finger_tip):
        if current_gesture == 'two':
            if not self.mouse_down_executed:
                pyautogui.mouseDown()
                self.mouse_down_executed = True
            self.process_mouse_movement(index_finger_tip)
        else:
            self.mouse_down_executed = False

        if current_gesture == 'three':
            pyautogui.mouseUp()
        elif self.previous_gesture == 'three' and current_gesture == 'fist':
            pyautogui.rightClick()

class TransparentWindow(QMainWindow):
    def __init__(self, config):
        super().__init__()
        self.config = config
        self.left_hand_keypoints = []
        self.right_hand_keypoints = []
        self.connections = []
        self.initUI()

    def initUI(self):
        self.setGeometry(
            self.config.x,
            self.config.y,
            self.config.width,
            self.config.height
        )
        self._set_window_attributes()
        self.show()

    def _set_window_attributes(self):
        self.setWindowFlags(
            Qt.FramelessWindowHint |
            Qt.WindowStaysOnTopHint |
            Qt.Tool
        )
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setAttribute(Qt.WA_TransparentForMouseEvents)

    def setKeypoints(self, left_hand_keypoints, right_hand_keypoints, connections):
        self.left_hand_keypoints = left_hand_keypoints
        self.right_hand_keypoints = right_hand_keypoints
        self.connections = connections
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        pen = QPen(QColor(self.config.pen_color), self.config.pen_size * 4)
        painter.setPen(pen)

        for keypoints in [self.left_hand_keypoints, self.right_hand_keypoints]:
            if keypoints:
                self._draw_keypoints(painter, keypoints)
                self._draw_connections(painter, keypoints)

    def _draw_keypoints(self, painter, keypoints):
        for point in keypoints:
            x = int(point.x * self.width())
            y = int(point.y * self.height())
            painter.drawEllipse(x - 5, y - 5, 10, 10)

    def _draw_connections(self, painter, keypoints):
        for start_idx, end_idx in self.connections:
            if start_idx < len(keypoints) and end_idx < len(keypoints):
                start_point = keypoints[start_idx]
                end_point = keypoints[end_idx]
                start_x = int(start_point.x * self.width())
                start_y = int(start_point.y * self.height())
                end_x = int(end_point.x * self.width())
                end_y = int(end_point.y * self.height())
                painter.drawLine(start_x, start_y, end_x, end_y)

class HandTracker:
    def __init__(self):
        self.mp_hands = mp.solutions.hands
        self.hands = self.mp_hands.Hands(
            max_num_hands=2,
            min_detection_confidence=0.5,
            min_tracking_confidence=0.8
        )
        self.finger_status = FingerStatus()
        self.hand_action = HandAction()

    def process_frame(self, frame):
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
            self._process_hand(hand_landmarks, handedness, left_hand_keypoints, right_hand_keypoints)
        return left_hand_keypoints, right_hand_keypoints, self.mp_hands.HAND_CONNECTIONS

    def _process_hand(self, hand_landmarks, handedness, left_hand_keypoints, right_hand_keypoints):
        is_left = handedness.classification[0].label == 'Left'
        if is_left:
            status = self.finger_status.get_finger_status(hand_landmarks, True)
            self.hand_action.watchGesture(
                hand_landmarks.landmark,
                self.finger_status.recognize_gesture(status),
                isLeft=True
            )
            left_hand_keypoints.extend(hand_landmarks.landmark)
        else:
            status = self.finger_status.get_finger_status(hand_landmarks, False)
            self.hand_action.watchGesture(
                hand_landmarks.landmark,
                self.finger_status.recognize_gesture(status),
                isLeft=False
            )
            right_hand_keypoints.extend(hand_landmarks.landmark)

def main():
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
    manage_process = ManageProcess()
    cap = cv2.VideoCapture(0)

    def update_landmarks():
        ret, frame = cap.read()
        if not ret:
            return

        result = hand_tracker.process_frame(frame)
        if result:
            window.setKeypoints(*result)
        manage_process.ensure_python_is_frontmost()

    timer = QTimer()
    timer.timeout.connect(update_landmarks)
    timer.start(10)  # 10ms 간격으로 프레임 캡처

    try:
        app.exec_()
    finally:
        cap.release()

if __name__ == "__main__":
    main()