import sys
from PyQt6.QtWidgets import QApplication
from login_app import LoginApp

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = LoginApp()
    window.show()
    sys.exit(app.exec())