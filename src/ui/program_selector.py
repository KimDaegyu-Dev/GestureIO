from PyQt5.QtWidgets import QDialog, QVBoxLayout, QPushButton, QLabel
from PyQt5.QtCore import Qt

class ProgramSelector(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Select Application")
        self.setGeometry(100, 100, 300, 150)
        self.selected_program = None
        self.initUI()

    def initUI(self):
        layout = QVBoxLayout()

        label = QLabel("Which application would you like to run?")
        label.setAlignment(Qt.AlignCenter)
        layout.addWidget(label)

        self.main_button = QPushButton("Main Application")
        self.main_button.clicked.connect(self.select_main)
        layout.addWidget(self.main_button)

        self.landmark_button = QPushButton("Landmark Sharing Client")
        self.landmark_button.clicked.connect(self.select_landmark)
        layout.addWidget(self.landmark_button)

        self.setLayout(layout)

    def select_main(self):
        self.selected_program = "main"
        self.accept()

    def select_landmark(self):
        self.selected_program = "landmark"
        self.accept()

    def get_selected_program(self):
        if self.exec_() == QDialog.Accepted:
            return self.selected_program
        return None

