import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QLabel, QVBoxLayout, QHBoxLayout, QPushButton, QCheckBox
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QImage, QPixmap
from typing_menu import TypingMenu


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        # Set window title
        self.setWindowTitle("OpenCV with PyQt5")
        self.setGeometry(-1500, 200, 1400, 700)
        self.setFixedSize(1400, 700)
        self.setStyleSheet("background-color: #282828;")

        # Create TypingMenu widget
        self.typing_menu = TypingMenu()

        # Set the central widget of the main window
        self.setCentralWidget(self.typing_menu)

        # Show the window
        self.show()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    sys.exit(app.exec_())
