class FingerStatus:
    def __init__(self):
        pass
    def get_right_finger_status(self, hand):
        """
        손가락이 펴져 있는지 접혀 있는지 확인하는 함수
        """
        # 오른손만 사용
        fingers = []

        # 엄지: 랜드마크 4가 랜드마크 3의 오른쪽에 있으면 펼쳐진 상태
        if hand.landmark[4].x < hand.landmark[3].x:
            fingers.append(1)
        else:
            fingers.append(0)

        # 나머지 손가락: 각 손가락의 팁 (8, 12, 16, 20)이 PIP (6, 10, 14, 18) 위에 있으면 펼쳐진 상태
        tips = [8, 12, 16, 20]
        pip_joints = [6, 10, 14, 18]
        for tip, pip in zip(tips, pip_joints):
            if hand.landmark[tip].y < hand.landmark[pip].y:
                fingers.append(1)
            else:
                fingers.append(0)

        return fingers

    def get_left_finger_status(self, hand):
        """
        손가락이 펴져 있는지 접혀 있는지 확인하는 함수
        """
        # 왼손만 사용
        fingers = []

        # 엄지: 랜드마크 4가 랜드마크 3의 왼쪽에 있으면 펼쳐진 상태
        if hand.landmark[4].x > hand.landmark[3].x:
            fingers.append(1)
        else:
            fingers.append(0)

        # 나머지 손가락: 각 손가락의 팁 (8, 12, 16, 20)이 PIP (6, 10, 14, 18) 위에 있으면 펼쳐진 상태
        tips = [8, 12, 16, 20]
        pip_joints = [6, 10, 14, 18]
        for tip, pip in zip(tips, pip_joints):
            if hand.landmark[tip].y < hand.landmark[pip].y:
                fingers.append(1)
            else:
                fingers.append(0)

        return fingers


    def recognize_gesture(self, fingers_status):
        if fingers_status == [0, 0, 0, 0, 0]:
            return 'fist'
        elif fingers_status == [0, 1, 0, 0, 0]:
            return 'point'
        elif fingers_status == [1, 1, 0, 0, 0]:
            return 'standby'
        elif fingers_status == [1, 1, 1, 1, 1]:
            return 'open'
        elif fingers_status == [0, 1, 1, 0, 0]:
            return 'two'
        elif fingers_status == [0, 1, 1, 1, 0]:
            return 'three'
        elif fingers_status == [0, 1, 1, 1, 1]:
            return 'four'
        elif fingers_status == [1, 0, 1, 1, 1]:
            return 'okay'
        else:
            return 'unknown'
            
    

