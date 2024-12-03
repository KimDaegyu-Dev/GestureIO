from dataclasses import dataclass
import pyautogui
import PyXA
import Quartz
import AppKit
import numpy as np
from src.core.window_manager import WindowManager
from src.utils.data_classes import Point, WindowInfo

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
        self.window_manager = WindowManager()
        self.prev_mid_x = None
        self.prev_mid_y = None
        self.current_position = np.array([0, 0])
        self.prev_process_pid = 0

    def get_application_window_info(self, pid):
        """특정 PID를 가진 애플리케이션 창의 정보를 가져옵니다."""
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
        """PID로 애플리케이션 객체를 가져옵니다."""
        app_ref = AppKit.NSRunningApplication.runningApplicationWithProcessIdentifier_(pid)
        if app_ref:
            return PyXA.Application(app_ref.localizedName())
        return None

    def calculate_distance(self, point1, point2):
        """두 점 사이의 유클리드 거리를 계산합니다."""
        p1 = np.array([point1.x, point1.y])
        p2 = np.array([point2.x, point2.y])
        return np.linalg.norm(p1 - p2)

    def calculate_midpoint(self, point1, point2):
        """두 점의 중점을 계산합니다."""
        p1 = np.array([point1.x, point1.y])
        p2 = np.array([point2.x, point2.y])
        midpoint = (p1 + p2) / 2
        return midpoint[0], midpoint[1]

    def process_window_drag(self, index_finger_tip, thumb_tip):
        """창 드래그 동작을 처리합니다."""
        current_distance = self.calculate_distance(index_finger_tip, thumb_tip)
        if current_distance < self.CLICK_DISTANCE_THRESHOLD:
            self.update_window_position(index_finger_tip, thumb_tip)

    def update_window_position(self, index_finger_tip, thumb_tip):
        """창의 위치를 업데이트합니다."""
        mid_x, mid_y = self.calculate_midpoint(index_finger_tip, thumb_tip)
        new_position = np.array([int(mid_x * self.screen_width), int(mid_y * self.screen_height)])
        
        window_info = self.window_manager.get_topmost_window_at_position(new_position[0], new_position[1])
        if not window_info:
            return

        (app_name, pid) = window_info
        if pid != self.prev_process_pid:
            self._handle_new_window(pid)

        self._update_window_position(new_position, pid)
        self.prev_process_pid = pid
        self.prev_mid_x, self.prev_mid_y = new_position

    def _handle_new_window(self, pid):
        """새로운 창을 처리합니다."""
        self.prev_mid_x, self.prev_mid_y = None, None
        window_info = self.get_application_window_info(pid)
        if window_info:
            self.current_position = np.array([window_info.x, window_info.y])

    def _update_window_position(self, new_position, pid):
        """창의 새로운 위치를 적용합니다."""
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
        """마우스 이동을 처리합니다."""
        self.cursor_x = int(index_finger_tip.x * self.screen_width)
        self.cursor_y = int(index_finger_tip.y * self.screen_height) - 5
        pyautogui.moveTo(self.cursor_x, self.cursor_y)

    def process_scroll(self, index_finger_tip, scroll_up=True):
        """스크롤 동작을 처리합니다."""
        if self.previous_y is not None:
            current_y = int(index_finger_tip.y * self.screen_height)
            delta_y = current_y - self.previous_y
            if (scroll_up and delta_y > 0) or (not scroll_up and delta_y < 0):
                pyautogui.scroll(delta_y / 20)
        self.previous_y = int(index_finger_tip.y * self.screen_height)

    def watch_gesture(self, hand_landmark, current_gesture, is_left=True):
        """손동작을 감지하고 처리합니다."""
        index_finger_tip = hand_landmark[8]
        thumb_tip = hand_landmark[4]

        if self.previous_gesture == 'okay' and current_gesture == 'okay':
            self.process_window_drag(index_finger_tip, thumb_tip)
        elif self.previous_gesture == 'point' and current_gesture == 'point':
            self.process_mouse_movement(index_finger_tip)
        elif self.previous_gesture == 'point' and current_gesture == 'standby':
            pyautogui.click(self.cursor_x, self.cursor_y)

        if is_left:
            if current_gesture == 'two' and self.previous_gesture == 'two':
                self.process_scroll(index_finger_tip, True)
            elif current_gesture == 'three' and self.previous_gesture == 'three':
                self.process_scroll(index_finger_tip, False)
        else:
            self._handle_right_hand_gestures(current_gesture, index_finger_tip)

        self.previous_gesture = current_gesture

    def _handle_right_hand_gestures(self, current_gesture, index_finger_tip):
        """오른손 제스처를 처리합니다."""
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