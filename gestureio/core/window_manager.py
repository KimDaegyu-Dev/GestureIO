from typing import Optional, Tuple, List, Dict
import Quartz
import AppKit
import logging

logger = logging.getLogger(__name__)

class WindowManager:
    def __init__(self):
        self.previous_window_pid: Optional[int] = None
        self.current_window_position: Optional[Tuple[int, int]] = None
        
    def get_window_at_position(self, x: int, y: int) -> Optional[Tuple[str, int]]:
        """주어진 좌표에 있는 윈도우 정보를 반환합니다.

        Args:
            x: 화면 X 좌표
            y: 화면 Y 좌표

        Returns:
            Optional[Tuple[str, int]]: (앱 이름, 프로세스 ID) 또는 None
        """
        options = Quartz.kCGWindowListOptionOnScreenOnly | Quartz.kCGWindowListExcludeDesktopElements
        window_list = Quartz.CGWindowListCopyWindowInfo(options, Quartz.kCGNullWindowID)
        
        for window in window_list:
            app_name = window.get('kCGWindowOwnerName', '')
            if app_name in ['Window Server', '스크린샷', 'screencapture']:
                continue
                
            bounds = window.get('kCGWindowBounds')
            if bounds:
                if (bounds['X'] <= x <= bounds['X'] + bounds['Width'] and
                    bounds['Y'] <= y <= bounds['Y'] + bounds['Height']):
                    pid = window.get('kCGWindowOwnerPID')
                    return app_name, pid
        return None

    def bring_window_to_front(self, pid: int) -> bool:
        """지정된 프로세스의 윈도우를 최상위로 가져옵니다.

        Args:
            pid: 프로세스 ID

        Returns:
            bool: 성공 여부
        """
        try:
            app = AppKit.NSRunningApplication.runningApplicationWithProcessIdentifier_(pid)
            if app:
                return app.activateWithOptions_(AppKit.NSApplicationActivateIgnoringOtherApps)
            return False
        except Exception as e:
            logger.error(f"Failed to bring window to front: {e}")
            return False