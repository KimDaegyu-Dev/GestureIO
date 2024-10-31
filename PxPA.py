import PyXA
import time

# 맨 앞에 있는 창 확인
frontmost_app = PyXA.Application('System Events')
print(dir(frontmost_app))
frontmost_app.processes()[85].windows()[0].name
frontmost_window = frontmost_app.windows()

if frontmost_window:
    # window_position = frontmost_window.position
    window_name = frontmost_app

    # window_size = frontmost_window.size
    # frontmost_window.size = [700, 800]

    print(f"Window Name: {window_name}")
    # print(f"Window Position: [{window_position[0]}, {window_position[1]}]")
    # print(f"Window Size: [{window_size[0]}, {window_size[1]}]")
else:
    print("No window found for the frontmost application.")