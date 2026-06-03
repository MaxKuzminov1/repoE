from PyQt6.QtWidgets import QMainWindow, QMessageBox
from login import Ui_MainWindow as LoginWindow
from db import select
from products_window import ProductsWindow

class LoginApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.ui = LoginWindow()
        self.ui.setupUi(self)
        self.setWindowTitle("Авторизация")
        self.ui.btn_login.clicked.connect(self.login)
        self.ui.btn_guest.clicked.connect(self.open_guest)

    def login(self):
        login = self.ui.line_login.text()
        password = self.ui.line_password.text()
        user = select(
            "SELECT r.name, u.FIO FROM Users u JOIN Roles r ON u.RoleID = r.RoleID WHERE u.Login=%s AND u.Password=%s",
            (login, password)
        )
        if not user:
            QMessageBox.warning(self, "Ошибка", "Неверный логин или пароль")
            return
        role, fio = user[0]
        self.open_products(role, fio)

    def open_guest(self):
        self.open_products("guest", "Гость")

    def open_products(self, role, fio):
        self.w = ProductsWindow(role, fio)
        self.w.show()
        self.close()