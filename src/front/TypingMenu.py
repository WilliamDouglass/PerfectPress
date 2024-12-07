import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QLabel, QVBoxLayout, QHBoxLayout, QPushButton, QCheckBox
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QImage, QPixmap


class TypingMenu(QWidget):
    def __init__(self):
        super().__init__()

        # Set up the QLabel to display the video frames
        self.webcam_video = QLabel(self)
        self.webcam_video.setAlignment(Qt.AlignCenter)

        # Initialize the text_box label
        self.text_box = QLabel(self)
        self.text_box.setAlignment(Qt.AlignCenter)
        self.text_box.setText("This is the example text box")
        self.text_box.setStyleSheet("""
            background-color: #282828;
            color: #ebdbb2;
            font-size: 20px;
            border-radius: 10px;
            padding: 5px;
        """)

        # Initialize the warped_video label
        self.warped_video = QLabel(self)
        self.warped_video.setAlignment(Qt.AlignCenter)
        self.warped_video.setText("Warped Video Area")  # Optional: Placeholder text
        self.warped_video.setStyleSheet("""
            background-color: #282828;
            color: #d4d4d4;
            font-size: 18px;
        """)

        # Set up the button to trigger recalibrate
        self.recalibrate_button = QPushButton("Recalibrate", self)
        self.recalibrate_button.clicked.connect(self.start_recalibration)
        self.recalibrate_active = False
        self.prev_five_frames = []

        # Set up button to Draw Hand
        self.draw_hands_button = QCheckBox("Draw Hand Tracking?", self)

        # Set up button to Draw Kbm Layout
        self.draw_kbm_layout = QCheckBox("Draw Kbm Button Borders?", self)
        self.draw_kbm_layout.setChecked(True)  # Default kbm template is drawn

        # Disable focus on buttons
        self.disable_button_focus()

        # Create a horizontal layout to center the warped_video label
        center_layout = QHBoxLayout()
        center_layout.addWidget(self.warped_video)  # Add the warped_video label

        # Create the main layout
        layout = QVBoxLayout(self)
        layout.addWidget(self.text_box)  # Add text_box at the top
        layout.addLayout(center_layout)  # Add the centered warped_video label

        # Set the maximum width of the warped_video to half the window's width
        self.setGeometry(100, 100, 1400, 700)  # Set window size
        self.warped_video.setMaximumWidth(self.width() / 1.8)  # Make the width half of the window's width

        # Set the main window layout
        layout.addWidget(self.recalibrate_button)
        layout.addWidget(self.draw_kbm_layout)
        layout.addWidget(self.draw_hands_button)

        # Container widget
        container = QWidget()
        container.setLayout(layout)
        self.setLayout(layout)


    def disable_button_focus(self):
        # Disable focus on buttons
        self.recalibrate_button.setFocusPolicy(Qt.NoFocus)
        self.draw_kbm_layout.setFocusPolicy(Qt.NoFocus)
        self.draw_hands_button.setFocusPolicy(Qt.NoFocus)


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        # Set window title
        self.setWindowTitle("OpenCV with PyQt5")
        self.setGeometry(100, 100, 1400, 700)

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
