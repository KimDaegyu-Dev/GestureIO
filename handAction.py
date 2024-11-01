import pyautogui
import PyXA
from ManageProcess import ManageProcess
import Quartz
import AppKit
class HandAction:
    def get_frontmost_application_window(self):
        options = Quartz.kCGWindowListOptionOnScreenOnly | Quartz.kCGWindowListExcludeDesktopElements
        window_list = Quartz.CGWindowListCopyWindowInfo(options, Quartz.kCGNullWindowID)
        # print(window_list)
        frontmost_app_pid = AppKit.NSWorkspace.sharedWorkspace().frontmostApplication().processIdentifier()
        
        for window in window_list:
            if window.get('kCGWindowLayer') == 0 and window.get('kCGWindowOwnerPID') == frontmost_app_pid:
                window_bound=window.get('kCGWindowBounds')
                window_name=window.get('kCGWindowOwnerName')
                return [window_name, window_bound['X'], window_bound['Y'], window_bound['Height'], window_bound['Width']] 
        return None
    def __init__(self):
        # 화면 크기 가져오기
        self.screen_width, self.screen_height = pyautogui.size()
        self.previous_gesture = 'unknown'
        self.z_threshold = 0.1  # z좌표 임계값 설정
        self.previous_y = None  # 이전 y 좌표 저장
        self.scroll_direction = None  # 스크롤 방향 저장
        self.mouse_down_executed = False  # mouseDown 실행 여부
        self.x = 0 
        self.y = 0
        self.mange_process = ManageProcess()
        self.prev_mid_x = None
        self.prev_mid_y = None
        self.current_position = self.get_frontmost_application_window()[1:3]
        self.current_size = self.get_frontmost_application_window()[3:5]
        self.current_name = self.get_frontmost_application_window()[0]
    def calculate_distance(self, point1, point2):
        return ((point1.x - point2.x) ** 2 + (point1.y - point2.y) ** 2) ** 0.5
    def print_finger_position(self, index_finger_tip):
        """
        검지 손가락의 랜드마크를 받아서 화면의 어느 위치인지 출력하는 메소드
        """
        # 랜드마크의 x, y 좌표를 화면 크기에 맞게 변환
        x = int(index_finger_tip.x * self.screen_width)
        y = int(index_finger_tip.y * self.screen_height)
        z = index_finger_tip.z

        # 위치 출력
        print(f"Index Finger Position: ({x}, {y}, {z})")
    def get_app_by_pid(self, pid):
        # NSRunningApplication을 통해 PID로 실행 중인 애플리케이션 가져오기
        app_ref = AppKit.NSRunningApplication.runningApplicationWithProcessIdentifier_(pid)
        
        if app_ref:
            # PyXA를 사용해 PID로 애플리케이션 접근
            app = PyXA.Application(app_ref.localizedName())
            return app
        else:
            return None
    def calculate_midpoint(self, point1, point2):
        mid_x = (point1.x + point2.x) / 2
        mid_y = (point1.y + point2.y) / 2
        return mid_x, mid_y
    def process_landmarks(self, left_index_finger_tip, left_thumb_tip):
        current_distance = self.calculate_distance(left_index_finger_tip, left_thumb_tip)

        if current_distance < 0.05: #얼마나 가까워야하는지
            self.update_window_position(left_index_finger_tip, left_thumb_tip)

    def update_window_position(self, left_index_finger_tip, left_thumb_tip):
        mid_x, mid_y = self.calculate_midpoint(left_index_finger_tip, left_thumb_tip)
        screen_width, screen_height = pyautogui.size()
        new_x = int(mid_x * screen_width)
        new_y = int(mid_y * screen_height)

        if self.prev_mid_x is not None and self.prev_mid_y is not None:
            move_x = new_x - self.prev_mid_x
            move_y = new_y - self.prev_mid_y

            frontmost_app = self.get_app_by_pid(self.mange_process.get_frontmost_app_pid())
            frontmost_window = frontmost_app.windows()[0]
            if frontmost_window:
                frontmost_window.position = [self.current_position[0] + move_x, self.current_position[1] + move_y]
                self.current_position = [self.current_position[0] + move_x, self.current_position[1] + move_y]

        self.prev_mid_x, self.prev_mid_y = new_x, new_y
    def watchGesture(self, hand_landmark, current_gesture, isLeft=True):
        """
        제스처가 standby에서 point로 바뀌면 index_finger_tip의 위치에 마우스 클릭을 수행하는 메소드
        """
        # 검지 손가락의 랜드마크 가져오기
        index_finger_tip = hand_landmark[8]  # 8번 랜드마크가 검지 손가락 끝
        thumb_tip = hand_landmark[4]
        # 제스처가 'point'에서 'point'로 유지되는지 확인
        

        # 제스처가 standby에서 point로 바뀌었는지 확인
        if self.previous_gesture == 'okay' and current_gesture == 'okay':
            self.process_landmarks(index_finger_tip, thumb_tip)
        if self.previous_gesture == 'point' and current_gesture == 'point':
            # 랜드마크의 x, y 좌표를 화면 크기에 맞게 변환
            self.x = int(index_finger_tip.x * self.screen_width)
            self.y = int(index_finger_tip.y * self.screen_height) - 5

            # 마우스 위치 이동
            pyautogui.moveTo(self.x, self.y)
        elif (self.previous_gesture == 'point' and current_gesture == 'four'):
            # 랜드마크의 x, y 좌표를 화면 크기에 맞게 변환
            # x = int(index_finger_tip.x * self.screen_width)
            # y = int(index_finger_tip.y * self.screen_height) - 5

            # 마우스 클릭 수행
            pyautogui.click(self.x, self.y)
        if isLeft:
            
            # 제스처가 'two'에서 'two'로 유지되는지 확인
            if self.previous_gesture == 'two' and current_gesture == 'two':
                # 이전 y 좌표가 설정되어 있는지 확인
                if self.previous_y is not None:
                    current_y = int(index_finger_tip.y * self.screen_height)
                    delta_y = current_y - self.previous_y
                    if delta_y > 0:
                        pyautogui.scroll(delta_y / 20)
                self.previous_y = int(index_finger_tip.y * self.screen_height)
            if self.previous_gesture == 'three' and current_gesture == 'three':
                if self.previous_y is not None:
                    current_y = int(index_finger_tip.y * self.screen_height)
                    delta_y = current_y - self.previous_y
                    if delta_y < 0:
                        pyautogui.scroll(delta_y / 20)
                self.previous_y = int(index_finger_tip.y * self.screen_height)
        else:
            if self.previous_gesture == 'two' and current_gesture == 'two':
                if not self.mouse_down_executed:
                    pyautogui.mouseDown()
                    self.mouse_down_executed = True
                # 랜드마크의 x, y 좌표를 화면 크기에 맞게 변환
                x = int(index_finger_tip.x * self.screen_width)
                y = int(index_finger_tip.y * self.screen_height) - 5

                # 마우스 위치 이동
                pyautogui.moveTo(x, y)
            else:
                self.mouse_down_executed = False

            if self.previous_gesture == 'three' and current_gesture == 'three':
                pyautogui.mouseUp()

            if self.previous_gesture == 'three' and current_gesture == 'fist':
                pyautogui.rightClick()
        # 이전 제스처 상태 업데이트
        self.previous_gesture = current_gesture

# 예제 사용법
if __name__ == "__main__":
    hand_action = HandAction()
    # 예제 데이터
    class Landmark:
        def __init__(self, x, y, z):
            self.x = x
            self.y = y
            self.z = z
    hand_landmark = [Landmark(0.5, 0.5, 0.0) for _ in range(21)]  # 21개의 랜드마크 생성
    hand_action.watchGesture(hand_landmark, 'point', True)
    hand_action.watchGesture(hand_landmark, 'two', True)
    hand_action.watchGesture(hand_landmark, 'two', True)
    hand_action.watchGesture(hand_landmark, 'point', True)
    hand_action.watchGesture(hand_landmark, 'point', True)