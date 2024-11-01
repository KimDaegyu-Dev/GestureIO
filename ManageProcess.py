import Quartz
import AppKit

class ManageProcess:
    def __init__(self):
        self.python_pids = self.get_python_processes()

    def get_frontmost_application_window(self):
        options = Quartz.kCGWindowListOptionOnScreenOnly | Quartz.kCGWindowListExcludeDesktopElements
        window_list = Quartz.CGWindowListCopyWindowInfo(options, Quartz.kCGNullWindowID)
        frontmost_app_pid = AppKit.NSWorkspace.sharedWorkspace().frontmostApplication().processIdentifier()
        for window in window_list:
            if window.get('kCGWindowLayer') == 0 and window.get('kCGWindowOwnerPID') == frontmost_app_pid:
                window_bound = window.get('kCGWindowBounds')
                window_PID = window.get('kCGWindowOwnerPID')
                return [window_PID, window_bound['X'], window_bound['Y'], window_bound['Height'], window_bound['Width']]
        return None
    def get_frontmost_app_pid(self):
        frontmost_app = AppKit.NSWorkspace.sharedWorkspace().frontmostApplication()
        return frontmost_app.processIdentifier()
    def get_python_processes(self):
        python_processes = []
        running_apps = AppKit.NSWorkspace.sharedWorkspace().runningApplications()
        for app in running_apps:
            if 'Python' in app.localizedName():
                python_processes.append(app.processIdentifier())
        return python_processes

    def bring_window_to_front(self, pid):
        app = AppKit.NSRunningApplication.runningApplicationWithProcessIdentifier_(pid)
        if app:
            app.activateWithOptions_(AppKit.NSApplicationActivateIgnoringOtherApps)
            return True
        return False
    def ensure_python_is_frontmost(self):
        self.bring_window_to_front(self.python_pids[0])
        # frontmost_pid = self.get_frontmost_app_pid()
        # if frontmost_pid in self.python_pids:
        #     print("Python process is already frontmost.")
        #     return True
        # else:
        #     # print("Python process is not frontmost. Bringing to front...")
        #     return self.bring_window_to_front(self.python_pids[0])
    def bring_python_to_front(self):
        python_pids = self.get_python_processes()
        if python_pids:
            # print(f"Python processes found with PIDs: {python_pids}")
            for pid in python_pids:
                success = self.bring_window_to_front(pid)
                if success:
                    # print(f"Successfully brought window with PID {pid} to front.")
                    pass
                else:
                    # print(f"Failed to bring window with PID {pid} to front.")
                    pass
        else:
            print("No Python processes found.") 
