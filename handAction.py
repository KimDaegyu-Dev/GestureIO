import pyautogui

class HandAction:
    def __init__(self):
        # 화면 크기 가져오기
        self.screen_width, self.screen_height = pyautogui.size()
        self.previous_gesture = 'unknown'
        self.z_threshold = 0.1  # z좌표 임계값 설정

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

    def click(self, index_finger_tip, current_gesture):
        """
        제스처가 standby에서 point로 바뀌면 index_finger_tip의 위치에 마우스 클릭을 수행하는 메소드
        """
        # 제스처가 standby에서 point로 바뀌었는지 확인
        if self.previous_gesture == 'standby' and current_gesture == 'point':
            # 랜드마크의 x, y 좌표를 화면 크기에 맞게 변환
            x = int(index_finger_tip.x * self.screen_width)
            y = int(index_finger_tip.y * self.screen_height) -5

            # 좌표 보정 (예: 중앙을 기준으로 좌표를 조정)
            # x = self.screen_width - x
            # y = self.screen_height - y

            # 마우스 클릭 수행
            pyautogui.click(x, y)
            print(x,y)

        # 이전 제스처 상태 업데이트
        self.previous_gesture = current_gesture

# 예제 사용법
if __name__ == "__main__":
    hand_action = HandAction()
    # Mediapipe로 손의 랜드마크를 추정한 후, index_finger_tip 객체와 current_gesture를 전달하여 제스처를 인식하고 클릭을 수행합니다.
    # 예를 들어:
    # hand_action.click(index_finger_tip, current_gesture)
    pass