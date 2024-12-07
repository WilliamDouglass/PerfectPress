import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QLabel, QVBoxLayout, QHBoxLayout, QPushButton, QCheckBox
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QImage, QPixmap


class TypingMenu(QWidget):
    def __init__(self):
        super().__init__()

        # Set up components
        self.webcam_video = QLabel(self)
        self.webcam_video.setAlignment(Qt.AlignCenter)

        self.text_box = self.init_text_box()
        self.video_feed_area = self.init_video_feed()
        self.recalibrate_button = None
        self.draw_hands_button = None
        self.draw_kbm_layout = None
        self.toggle_webcam_button = None
        self.init_buttons()

        # Set up layouts and container
        self.main_layout = QVBoxLayout(self)
        self.init_layouts()

        # Set the window properties
        self.setup_window()

        # Webcam feed
        self.timer = None
        # self.start_webcam_feed()


########################################################################################################################
#   Update Frame
########################################################################################################################
    def start_webcam_feed(self):
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_warped_video_frame)
        self.timer.start(16)  # Update every 16ms (~60fps)

    def update_warped_video_frame(self, openCV_frame):
        pass

########################################################################################################################
#   Menu Setup
########################################################################################################################

    def init_layouts(self):
        # Create a horizontal layout for the video_feed
        center_layout = QHBoxLayout()
        center_layout.addWidget(self.video_feed_area)

        # Add components to the main layout
        self.main_layout.addWidget(self.text_box)  # Add text_box at the top
        self.main_layout.addLayout(center_layout)  # Add the centered video_feed label
        self.main_layout.addWidget(self.toggle_webcam_button)
        self.main_layout.addWidget(self.recalibrate_button)
        self.main_layout.addWidget(self.draw_kbm_layout)
        self.main_layout.addWidget(self.draw_hands_button)


        # Set the main window layout
        container = QWidget()
        container.setLayout(self.main_layout)
        self.setLayout(self.main_layout)

    def setup_window(self):
        # Set the geometry of the window
        self.setGeometry(100, 100, 1400, 700)

        # Adjust the maximum width of the video_feed
        self.video_feed_area.setMaximumWidth(self.width() / 1.8)

    def init_text_box(self):
        text_box = QLabel(self)
        text_box.setAlignment(Qt.AlignCenter)
        text_box.setText("This is the example text box")
        text_box.setStyleSheet("""
                    color: #ebdbb2;
                    font-size: 20px;
                    border-radius: 10px;
                    border: 2px solid #ebdbb2;                    
                """)
        return text_box

    def init_video_feed(self):
        warped_video = QLabel(self)
        warped_video.setAlignment(Qt.AlignCenter)
        warped_video.setText("Video Feed Area")  # Optional: Placeholder text
        warped_video.setStyleSheet("""
            color: #ebdbb2;
            font-size: 18px;
            border-radius: 10px;
            border: 2px solid #ebdbb2;            
        """)
        return warped_video

    def init_buttons(self):

        push_button_style = """
            QPushButton {
                color: #ebdbb2;
                font-size: 18px;
                border-radius: 10px;
                background-color: #3c3836;
                padding: 5px;
            }
            QPushButton:hover {
                background-color: #504945;
            }
            QPushButton:pressed {
                background-color: #262625; /* Darker color when pressed */
                border: 2px solid #e8ddc1; /* Optional: change border color when pressed */
            }
        """

        check_box_style = """
            QCheckBox {
                color: #ebdbb2;
                font-size: 18px;
            }
            QCheckBox::indicator {
                width: 15px;
                height: 15px;
                border-radius: 10px;
            }
            QCheckBox::indicator:unchecked {
                background-color: #3c3836;
            }
            QCheckBox::indicator:checked {
                background-color: #0ff702;
            }
            QCheckBox::indicator:checked:hover {
                background-color: #4b8f47;
            }
            QCheckBox::indicator:unchecked:hover {
                background-color: #504945;
            }
        """

        # Init Recalibration Button
        self.recalibrate_button = QPushButton("Recalibrate", self)
        self.recalibrate_button.setStyleSheet(push_button_style)

        # Set up button to Draw Hand
        self.draw_hands_button = QCheckBox("Draw Hand Tracking?", self)
        self.draw_hands_button.setStyleSheet(check_box_style)

        # Set up button to Draw Kbm Layout
        self.draw_kbm_layout = QCheckBox("Draw Kbm Button Borders?", self)
        self.draw_kbm_layout.setChecked(True)  # Default kbm template is drawn
        self.draw_kbm_layout.setStyleSheet(check_box_style)

        # Set up button to Toggle Webcam
        self.toggle_webcam_button = QCheckBox("Toggle Webcam", self)
        self.toggle_webcam_button.setStyleSheet(check_box_style)

        # Disable focus on buttons
        buttons = [self.recalibrate_button, self.draw_hands_button, self.draw_kbm_layout, self.toggle_webcam_button]
        for button in buttons:
            button.setFocusPolicy(Qt.NoFocus)


