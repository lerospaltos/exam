import sys
from PyQt5.QtWidgets import *
from PyQt5.QtCore import Qt
from auth import Auth


class LoginWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.auth = Auth()
        self.initUI()

    def initUI(self):
        self.setWindowTitle("Авторизация - TechStore")
        self.setFixedSize(400, 450)
        self.setStyleSheet("background-color: white;")

        # Центральный виджет
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)

        # Шапка
        header = QLabel("TechStore")
        header.setAlignment(Qt.AlignCenter)
        header.setStyleSheet(
            "font-size: 28px; font-weight: bold; color: white; background-color: #19493f; padding: 20px;")
        layout.addWidget(header)

        # Форма
        form_widget = QWidget()
        form_layout = QVBoxLayout(form_widget)
        form_layout.setSpacing(15)

        title = QLabel("Вход в систему")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("font-size: 22px; font-weight: bold; color: #19493f; margin: 20px 0;")
        form_layout.addWidget(title)

        self.txt_username = QLineEdit()
        self.txt_username.setPlaceholderText("Логин")
        self.txt_username.setStyleSheet("height: 35px; padding: 5px; border: 1px solid #ccc;")
        form_layout.addWidget(self.txt_username)

        self.txt_password = QLineEdit()
        self.txt_password.setPlaceholderText("Пароль")
        self.txt_password.setEchoMode(QLineEdit.Password)
        self.txt_password.setStyleSheet("height: 35px; padding: 5px; border: 1px solid #ccc;")
        form_layout.addWidget(self.txt_password)

        self.btn_login = QPushButton("ВОЙТИ")
        self.btn_login.setStyleSheet("""
            QPushButton {
                background-color: #359A85; 
                color: white; 
                font-weight: bold; 
                height: 40px;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #19493f;
            }
        """)
        self.btn_login.clicked.connect(self.login)
        form_layout.addWidget(self.btn_login)

        self.btn_register = QPushButton("Зарегистрироваться")
        self.btn_register.setStyleSheet("""
            QPushButton {
                background-color: transparent; 
                color: #359A85; 
                border: 1px solid #359A85;
                height: 35px;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #359A85;
                color: white;
            }
        """)
        self.btn_register.clicked.connect(self.register)
        form_layout.addWidget(self.btn_register)

        self.lbl_error = QLabel("")
        self.lbl_error.setStyleSheet("color: red;")
        self.lbl_error.setAlignment(Qt.AlignCenter)
        self.lbl_error.setVisible(False)
        form_layout.addWidget(self.lbl_error)

        layout.addWidget(form_widget)

        # Нижняя панель
        footer = QLabel("© 2024 TechStore")
        footer.setAlignment(Qt.AlignCenter)
        footer.setStyleSheet("background-color: #f5f5f5; padding: 10px; color: #666;")
        layout.addWidget(footer)

    def login(self):
        username = self.txt_username.text().strip()
        password = self.txt_password.text()

        if not username or not password:
            self.show_error("Введите логин и пароль")
            return

        if self.auth.is_blocked(username):
            self.show_error("Пользователь заблокирован")
            return

        user = self.auth.login(username, password)
        if user:
            self.open_main_window(user)
        else:
            self.show_error("Неверный логин или пароль")

    def register(self):
        username = self.txt_username.text().strip()
        password = self.txt_password.text()

        if not username or not password:
            self.show_error("Введите логин и пароль")
            return

        if len(password) < 3:
            self.show_error("Пароль должен быть минимум 3 символа")
            return

        if self.auth.register(username, password):
            QMessageBox.information(self, "Успех", "Регистрация успешна! Теперь вы можете войти.")
            self.lbl_error.setVisible(False)
        else:
            self.show_error("Пользователь уже существует")

    def show_error(self, message):
        self.lbl_error.setText(message)
        self.lbl_error.setVisible(True)

    def open_main_window(self, user):
        from main_window import MainWindow
        self.main_window = MainWindow(user)
        self.main_window.show()
        self.close()