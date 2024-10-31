import PyXA
import time

# 맨 앞에 있는 창 확인
frontmost_app = PyXA.Application("Code")
print(frontmost_app.windows())
frontmost_window = frontmost_app.windows()[0]

if frontmost_window:
    window_name = frontmost_window.name
    window_position = frontmost_window.position

    window_size = frontmost_window.size
    frontmost_window.size = [700, 800]

    print(f"Window Name: {window_name}")
    print(f"Window Position: [{window_position[0]}, {window_position[1]}]")
    print(f"Window Size: [{window_size[0]}, {window_size[1]}]")
else:
    print("No window found for the frontmost application.")