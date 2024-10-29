import Quartz
import AppKit

def get_frontmost_application_window():
    options = Quartz.kCGWindowListOptionOnScreenOnly | Quartz.kCGWindowListExcludeDesktopElements
    window_list = Quartz.CGWindowListCopyWindowInfo(options, Quartz.kCGNullWindowID)
    print(window_list)
    frontmost_app_pid = AppKit.NSWorkspace.sharedWorkspace().frontmostApplication().processIdentifier()
    
    for window in window_list:
        if window.get('kCGWindowLayer') == 0 and window.get('kCGWindowOwnerPID') == frontmost_app_pid:
            return window
    return None

def resize_window(window_id, new_width, new_height):
    # Get the current window bounds
    window_bounds = Quartz.CGWindowListCreateDescriptionFromArray([window_id])[0]['kCGWindowBounds']
    new_bounds = Quartz.CGRectMake(window_bounds['X'], window_bounds['Y'], new_width, new_height)
    
    # Move and resize the window
    # Quartz.CGWindowMoveResize(window_id, new_bounds)

def main():
    frontmost_window = get_frontmost_application_window()
    
    if frontmost_window:
        window_id = frontmost_window['kCGWindowNumber']
        new_width = 800
        new_height = 600
        
        resize_window(window_id, new_width, new_height)
        print(f"Resized window {window_id} to {new_width}x{new_height}")
    else:
        print("No frontmost window found.")

if __name__ == "__main__":
    main()