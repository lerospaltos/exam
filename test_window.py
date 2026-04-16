from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel
import sys

class TestWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Тест")
        self.setGeometry(100, 100, 300, 200)
        label = QLabel("Окно работает!", self)
        label.move(100, 80)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = TestWindow()
    window.show()
    sys.exit(app.exec_())