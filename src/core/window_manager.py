import Quartz
import AppKit
import PyXA
import numpy as np
from src.utils.data_classes import WindowInfo

class WindowManager:
    IGNORED_APPS = {'Window Server', '스크린샷', 'screencapture'}
    WINDOW_LIST_OPTIONS = Quartz.kCGWindowListOptionOnScreenOnly | Quartz.kCGWindowListExcludeDesktopElements

    def __init__(self):
        self.python_pids = self.get_python_processes()

    def get_layer_order(self):
        window_list = Quartz.CGWindowListCopyWindowInfo(
            self.WINDOW_LIST_OPTIONS,
            Quartz.kCGNullWindowID
        )
        return [
            (window.get('kCGWindowOwnerName', 'Unknown'),
             window.get('kCGWindowOwnerPID', 'Unknown'))
            for window in window_list
        ]

    def get_frontmost_application_window(self):
        window_list = Quartz.CGWindowListCopyWindowInfo(
            self.WINDOW_LIST_OPTIONS,
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
            self.WINDOW_LIST_OPTIONS,
            Quartz.kCGNullWindowID
        )
        
        window_bounds_list = []
        for window in window_list:
            app_name = window.get('kCGWindowOwnerName', 'Unknown')
            if app_name in self.IGNORED_APPS:
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

    def get_application_window_info(self, pid):
        window_list = Quartz.CGWindowListCopyWindowInfo(self.WINDOW_LIST_OPTIONS, Quartz.kCGNullWindowID)
        
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

    def update_window_position(self, pid, new_position):
        app = self.get_app_by_pid(pid)
        if app and app.windows():
            app.windows()[0].position = new_position.tolist()

