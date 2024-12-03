import socketio
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QPushButton, QLineEdit, QListWidget
from PyQt5.QtCore import QTimer
import cv2
import mediapipe as mp
from src.ui.landmark_visualizer import LandmarkVisualizerWindow
from src.core.hand_tracker import HandTracker


class LandmarkSharing(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('Landmark Sharing App')
        self.setGeometry(100, 100, 400, 300)
        
        self.sio = socketio.Client()
        self.setup_socket_events()
        
        # HandTracker 초기화
        self.hand_tracker = HandTracker()
        self.cap = cv2.VideoCapture(0)
        
        self.landmark_visualizer = LandmarkVisualizerWindow()
        self.initUI()
        self.setup_camera_timer()

    def initUI(self):
        layout = QVBoxLayout()
        
        self.username_input = QLineEdit(self)
        self.username_input.setPlaceholderText("Enter your username")
        layout.addWidget(self.username_input)
        
        self.connect_button = QPushButton('Connect', self)
        self.connect_button.clicked.connect(self.connect_to_server)
        layout.addWidget(self.connect_button)
        
        self.user_list = QListWidget(self)
        self.user_list.itemClicked.connect(self.select_user)
        layout.addWidget(self.user_list)
        
        self.setLayout(layout)
    def setup_camera_timer(self):
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_frame)
        self.timer.start(10)  # 10ms 간격으로 업데이트

    def update_frame(self):
        ret, frame = self.cap.read()
        if not ret:
            return

        result = self.hand_tracker.process_frame(frame)
        if result:
            left_hand, right_hand, connections = result
            # 랜드마크를 딕셔너리 형태로 변환
            landmarks = self.convert_landmarks_to_dict(left_hand, right_hand)
            if landmarks:
                self.landmark_visualizer.update_landmarks(landmarks)
                if hasattr(self, 'selected_user'):
                    self.sio.emit('landmarks', {
                        'targetUser': self.selected_user,
                        'landmarks': landmarks
                    })

    def convert_landmarks_to_dict(self, left_hand, right_hand):
        landmarks = []
        
        def add_landmarks(hand_landmarks):
            if hand_landmarks:
                for lm in hand_landmarks:
                    landmarks.append({
                        'x': lm.x,
                        'y': lm.y,
                        'z': lm.z
                    })
        
        add_landmarks(left_hand)
        add_landmarks(right_hand)
        return landmarks

    def cleanup(self):
        if self.cap.isOpened():
            self.cap.release()
    def setup_socket_events(self):
        @self.sio.event
        def connect():
            print('Connected to server')

        @self.sio.event
        def disconnect():
            print('Disconnected from server')

        @self.sio.on('userList')
        def on_user_list(users):
            self.user_list.clear()
            for user in users:
                if user != self.username_input.text():
                    self.user_list.addItem(user)

        @self.sio.on('landmarks')
        def on_landmarks(data):
            self.landmark_visualizer.update_landmarks(data['landmarks'], received=True)
            self.check_winner(data['landmarks'])

    def connect_to_server(self):
        username = self.username_input.text()
        if username:
            self.sio.connect('http://3.34.70.33:3000')
            self.sio.emit('register', username)
            self.connect_button.setEnabled(False)
            self.username_input.setEnabled(False)
            self.landmark_visualizer.show()

    def select_user(self, item):
        self.selected_user = item.text()

    def send_landmarks(self, landmarks):
        if hasattr(self, 'selected_user'):
            self.sio.emit('landmarks', {'targetUser': self.selected_user, 'landmarks': landmarks})

    def check_winner(self, opponent_landmarks):
        # Implement winner checking logic here
        pass