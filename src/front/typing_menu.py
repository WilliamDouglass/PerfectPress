import numpy as np
from PyQt5.QtWidgets import QWidget, QLabel, QVBoxLayout, QHBoxLayout, QPushButton, QCheckBox
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QImage, QPixmap
import cv2 as cv

from src.back.handle_webcam import WebCamHandler


class TypingMenu(QWidget):
    def __init__(self):
        super().__init__()

        # Set up components

        self.text_box = self.init_text_box()
        self.video_feed_area = self.init_video_feed()
        self.recalibrate_button = None
        self.draw_hands_button = None
        self.draw_kbm_layout = None
        self.toggle_webcam_button = None
        self.show_raw_video_button = None
        self.init_buttons()

        # Set up layouts and container
        self.main_layout = QVBoxLayout(self)
        self.init_layouts()

        # Set the window properties
        self.setup_window()

        self.time = 0

        self.webcam_handler = WebCamHandler()


########################################################################################################################
#   Update Video Frames
########################################################################################################################
# TODO: Implement the update_warped_video_frame method

    # Connected to the toggle_webcam_button
    def toggle_webcam(self):
        if self.toggle_webcam_button.isChecked():
            self.start_webcam_feed()
        else:
            self.stop_webcam_feed()

    def start_webcam_feed(self):
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_video_frames)
        self.timer.start(16)  # Update every 16ms (~60fps)
        self.webcam_handler.start_webcam()

    def stop_webcam_feed(self):
        self.timer.stop()
        self.webcam_handler.stop_webcam()
        self.video_feed_area.setText("Webcam Feed Area")
        self.update_raw_video_window_to_blank()

    # Connected to the show_raw_video_button
    def toggle_raw_video(self):
        if self.show_raw_video_button.isChecked():
            self.start_raw_video_feed_window()
        else:
            self.stop_raw_video_feed_window()

    def start_raw_video_feed_window(self):
        cv.namedWindow("Webcam Feed", cv.WINDOW_NORMAL)
        cv.resizeWindow("Webcam Feed", 427, 320)
        self.update_raw_video_window_to_blank()

    def stop_raw_video_feed_window(self):
        cv.destroyWindow("Webcam Feed")


    def update_video_frames(self):
        frame = self.webcam_handler.get_webcam_frame()

        # TODO only show the raw frame on the pyqt5 window if the warped frame is not calibrated
        self.update_warped_video_frame(frame)

        if self.show_raw_video_button.isChecked():
            self.update_raw_video_frame(frame)

        pass

    # This is the video frame that is on the OpenCV window
    def update_raw_video_frame(self, openCV_frame):
        if openCV_frame is not None:
            cv.imshow("Webcam Feed", openCV_frame)
        else:
            self.update_raw_video_window_to_blank()

    def update_raw_video_window_to_blank(self):
        if self.show_raw_video_button.isChecked():
            blank = np.zeros((320, 427, 3), np.uint8)
            blank = cv.putText(blank, "No webcam feed", (85, blank.shape[0]//2), cv.FONT_HERSHEY_DUPLEX, 1, (255, 255, 255), 1, cv.LINE_AA)
            cv.imshow("Webcam Feed", blank)


    # This is the video frame that is on the pyqt5 window
    def update_warped_video_frame(self, openCV_frame):
        # Convert the OpenCV frame from BGR to RGB
        rgb_frame = cv.cvtColor(openCV_frame, cv.COLOR_BGR2RGB)

        # Get the shape of the frame
        h, w, ch = rgb_frame.shape
        bytesPerLine = ch * w

        # Create a QImage from the OpenCV frame
        q_img = QImage(rgb_frame.data, w, h, bytesPerLine, QImage.Format_RGB888)

        # Create a QPixmap from the QImage
        pixmap = QPixmap.fromImage(q_img)

        # Scale the QPixmap to fit the label
        scaled_pixmap = pixmap.scaled(self.video_feed_area.width(), self.video_feed_area.height(), Qt.KeepAspectRatio)

        # Set the scaled pixmap to the label
        self.video_feed_area.setPixmap(scaled_pixmap)  # Use scaled_pixmap here

        self.layout().update()


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
        self.main_layout.addWidget(self.show_raw_video_button)
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
        video_feed_area = QLabel(self)
        video_feed_area.setAlignment(Qt.AlignCenter)
        video_feed_area.setText("Video Feed Area")  # Optional: Placeholder text
        video_feed_area.setStyleSheet("""
            color: #ebdbb2;
            font-size: 18px;
            border-radius: 10px;
            border: 2px solid #ebdbb2;            
        """)
        video_feed_area.setFixedSize(self.width(), self.width()/2.4)

        return video_feed_area

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
        self.toggle_webcam_button.setChecked(False)  # Default webcam is off
        self.toggle_webcam_button.stateChanged.connect(self.toggle_webcam)
        self.toggle_webcam_button.setStyleSheet(check_box_style)

        # Set up button to Show Raw
        self.show_raw_video_button = QCheckBox("Show Raw Video Feed", self)
        self.show_raw_video_button.setChecked(False)
        self.show_raw_video_button.stateChanged.connect(self.toggle_raw_video)
        self.show_raw_video_button.setStyleSheet(check_box_style)


        # Disable focus on buttons
        buttons = [self.recalibrate_button, self.draw_hands_button, self.draw_kbm_layout, self.toggle_webcam_button, self.show_raw_video_button]
        for button in buttons:
            button.setFocusPolicy(Qt.NoFocus)


