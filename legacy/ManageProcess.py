import Quartz
import AppKit
from Quartz import (
    CGWindowListCopyWindowInfo,
    kCGWindowListOptionOnScreenOnly,
    kCGWindowListExcludeDesktopElements,
    kCGNullWindowID
)

class WindowManager:
    """윈도우 관리를 위한 상수 정의"""
    IGNORED_APPS = {'Window Server', '스크린샷', 'screencapture'}
    WINDOW_LIST_OPTIONS = kCGWindowListOptionOnScreenOnly | kCGWindowListExcludeDesktopElements

class ManageProcess:
    """프로세스 및 윈도우 관리 클래스"""
    
    def __init__(self):
        """Python 프로세스 ID 초기화"""
        self.python_pids = self.get_python_processes()

    def get_layer_order(self):
        """
        화면에 표시된 윈도우의 레이어 순서를 가져옵니다.

        Returns:
            [(앱 이름, PID)] 튜플의 리스트
        """
        window_list = CGWindowListCopyWindowInfo(
            WindowManager.WINDOW_LIST_OPTIONS,
            kCGNullWindowID
        )
        return [
            (window.get('kCGWindowOwnerName', 'Unknown'),
             window.get('kCGWindowOwnerPID', 'Unknown'))
            for window in window_list
        ]

    def get_frontmost_application_window(self):
        """
        가장 앞에 있는 애플리케이션 창의 정보를 가져옵니다.

        Returns:
            [PID, X, Y, Height, Width] 또는 None
        """
        window_list = CGWindowListCopyWindowInfo(
            WindowManager.WINDOW_LIST_OPTIONS,
            kCGNullWindowID
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
        """
        가장 앞에 있는 애플리케이션의 PID를 가져옵니다.

        Returns:
            프로세스 ID
        """
        frontmost_app = (
            AppKit.NSWorkspace.sharedWorkspace()
            .frontmostApplication()
        )
        if frontmost_app.processIdentifier() == self.python_pids[0]:
            return self.get_next_frontmost_app_pid('Python')
        return frontmost_app.processIdentifier()

    def get_python_processes(self):
        """
        실행 중인 Python 프로세스의 PID 목록을 가져옵니다.

        Returns:
            Python 프로세스 ID 리스트
        """
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
        """
        특정 PID의 윈도우를 앞으로 가져옵니다.

        Args:
            pid: 프로세스 ID

        Returns:
            성공 여부
        """
        app = AppKit.NSRunningApplication.runningApplicationWithProcessIdentifier_(pid)
        if app:
            app.activateWithOptions_(AppKit.NSApplicationActivateIgnoringOtherApps)
            return True
        return False

    def ensure_python_is_frontmost(self):
        """Python 윈도우가 항상 최상위에 있도록 합니다."""
        self.bring_window_to_front(self.python_pids[0])

    def get_next_frontmost_app_pid(self, name):
        """
        특정 이름의 앱 다음으로 앞에 있는 앱의 PID를 가져옵니다.

        Args:
            name: 앱 이름

        Returns:
            다음 앱의 PID 또는 None
        """
        window_order = self.get_layer_order()
        for i, (app_name, pid) in enumerate(window_order):
            if app_name == name and i + 1 < len(window_order):
                return window_order[i + 1][1]
        return None

    def get_window_at_position(self, x, y):
        """
        특정 좌표에 있는 윈도우 정보를 가져옵니다.

        Args:
            x: X 좌표
            y: Y 좌표

        Returns:
            [(앱 이름, PID)] 튜플의 리스트
        """
        window_list = CGWindowListCopyWindowInfo(
            WindowManager.WINDOW_LIST_OPTIONS,
            kCGNullWindowID
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
        """
        특정 좌표에서 가장 위에 있는 윈도우 정보를 가져옵니다.

        Args:
            x: X 좌표
            y: Y 좌표

        Returns:
            (앱 이름, PID) 튜플 또는 None
        """
        windows_at_position = self.get_window_at_position(x, y)
        window_order = self.get_layer_order()
        
        for app_name, pid in window_order:
            if (app_name, pid) in windows_at_position:
                if app_name == 'Python':
                    continue
                return app_name, pid
        return None

# 예제 사용법
if __name__ == "__main__":
    manage_process = ManageProcess()
    frontmost_pid = manage_process.get_frontmost_app_pid()
    # second_frontmost_pid = manage_process.get_next_frontmost_app_pid()
    print(f"Frontmost PID: {frontmost_pid}")
    # print(f"Second Frontmost PID: {second_frontmost_pid}")

    # 임의의 X, Y 위치에 있는 창 정보 가져오기
    x, y = 100, 100  # 예제 좌표
    window_bounds_list = manage_process.get_window_at_position(x, y)
    top = manage_process.get_topmost_window_at_position(x,y)
    # print(top)
    if window_bounds_list:
        print(f"Window at position ({x}, {y}): Application: {window_bounds_list[0]}, PID: {window_bounds_list[1]}")
    else:
        print(f"No window found at position ({x}, {y})")