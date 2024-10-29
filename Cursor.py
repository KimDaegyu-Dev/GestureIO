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

    def move_cursor(self, wrist):
        cursor_x = int(wrist.x * self.screen_width)
        cursor_y = int(wrist.y * self.screen_height)
        
        current_time = time.time()
        if current_time - self.last_move_time > self.debounce_time:
            move_x = cursor_x - self.prev_cursor_x
            move_y = cursor_y - self.prev_cursor_y
            pyautogui.move(move_x, move_y)
            
            self.prev_cursor_x, self.prev_cursor_y = cursor_x, cursor_y
            self.last_move_time = current_time

    def click(self):
        pyautogui.click()