import pyautogui
import time

class Cursor:
    def __init__(self, screen_width, screen_height):
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.prev_cursor_x = screen_width // 2
        self.prev_cursor_y = screen_height // 2
        self.debounce_time = 0.1  # 100ms
        self.last_move_time = time.time()
        self.prev_finger_x = None
        self.prev_finger_y = None

    def move_cursor(self, index_finger_tip):
        cursor_x = int(index_finger_tip.x * self.screen_width)
        cursor_y = int(index_finger_tip.y * self.screen_height)
        
        if self.prev_finger_x is not None and self.prev_finger_y is not None:
            move_x = cursor_x - self.prev_finger_x
            move_y = cursor_y - self.prev_finger_y
            
            current_time = time.time()
            if current_time - self.last_move_time > self.debounce_time:
                pyautogui.move(move_x, move_y)
                self.last_move_time = current_time

        self.prev_finger_x, self.prev_finger_y = cursor_x, cursor_y

    def click(self):
        pyautogui.click()