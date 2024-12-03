import sys
from PyQt5.QtWidgets import QApplication, QMessageBox
from PyQt5.QtCore import Qt
from landmark_sharing_client import LandmarkSharingApp
from main import main as main_app

def main():
    app = QApplication(sys.argv)
    
    # 선택 창 생성
    msg_box = QMessageBox()
    msg_box.setStandardButtons(QMessageBox.NoButton)
    app.installEventFilter(msg_box)

    def eventFilter(obj, event):
        if event.type() == event.KeyPress and event.key() == Qt.Key_P:
            msg_box.show()
        return super(QMessageBox, msg_box).eventFilter(obj, event)

    msg_box.eventFilter = eventFilter
    msg_box.setWindowTitle("Select Application")
    msg_box.setText("Which application would you like to run?")
    main_button = msg_box.addButton("Main", QMessageBox.ActionRole)
    landmark_button = msg_box.addButton("Landmark Sharing Client", QMessageBox.ActionRole)
    msg_box.exec_()
    
    if msg_box.clickedButton() == main_button:
        main_app()
    elif msg_box.clickedButton() == landmark_button:
        ex = LandmarkSharingApp()
        sys.exit(app.exec_())

if __name__ == '__main__':
    main()

