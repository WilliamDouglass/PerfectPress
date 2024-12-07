import sys
import cv2 as cv
from PyQt5.QtCore import QTimer, Qt
from PyQt5.QtGui import QImage, QPixmap
from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel, QPushButton, QVBoxLayout, QWidget, QHBoxLayout, \
    QCheckBox
import keyboard

from src.back.kbm_tracking import KeyboardTracker
from src.back.hand_tracking import HandTracker

c = 0


class Calulate_FPS:
    def __init__(self):
        self.prev_frame_time = 0
        self.new_frame_time = 0

    def get_fps(self):
        self.new_frame_time = cv.getTickCount()
        fps = cv.getTickFrequency() / (self.new_frame_time - self.prev_frame_time)
        self.prev_frame_time = self.new_frame_time
        return fps

    def display_fps(self, frame):
        fps = self.get_fps()
        fps_text = f"FPS: {fps:.2f}"
        cv.putText(frame, fps_text, (10, 20), cv.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1, cv.LINE_AA)
        return frame


class VideoApp(QMainWindow):
    def __init__(self):
        super().__init__()


        # Set up the main UI
        self.setWindowTitle("OpenCV with PyQt5")
        self.setGeometry(100, 100, 1400, 700)

        # Set up OpenCV video capture
        self.cap = cv.VideoCapture(0, cv.CAP_DSHOW)
        self.cap.set(cv.CAP_PROP_FRAME_WIDTH, 640)
        self.cap.set(cv.CAP_PROP_FRAME_HEIGHT, 480)
        self.cap.set(cv.CAP_PROP_FPS, 30)

        # Initialize FPS and KeyboardTracker and HandTracker
        self.fps_tracker = Calulate_FPS()
        self.kbmTracker = KeyboardTracker()
        self.handTracker = HandTracker()

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

        # Initialize the video_feed label
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
        self.draw_hands_button = QCheckBox("Draw Hand Tracking?",self)

        # Set up button to Draw Kbm Layout
        self.draw_kbm_layout = QCheckBox("Draw Kbm Button Borders?",self)
        self.draw_kbm_layout.setChecked(True) # Default kbm template is drawn

        # Disable focus on buttons
        self.disable_button_focus()

        # Create a horizontal layout to center the video_feed label
        center_layout = QHBoxLayout()
        # center_layout.addStretch()  # Add stretch on the left side
        center_layout.addWidget(self.warped_video)  # Add the video_feed label
        # center_layout.addStretch()  # Add stretch on the right side

        # Create the main layout
        layout = QVBoxLayout(self)
        layout.addWidget(self.text_box)  # Add text_box at the top
        layout.addLayout(center_layout)  # Add the centered video_feed label

        # Set the maximum width of the video_feed to half the window's width
        self.setGeometry(100, 100, 1400, 700)  # Set window size
        self.warped_video.setMaximumWidth(self.width() / 1.8)  # Make the width half of the window's width

        # Set the main window layout
        layout.addWidget(self.recalibrate_button)
        layout.addWidget(self.draw_kbm_layout)
        layout.addWidget(self.draw_hands_button)

        # Container widget
        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

        # Set up a QTimer to refresh frames periodically
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_frame)
        self.timer.start(30)  # Set timer to update every 30 ms (about 33 FPS)

        # Set up global keyboard listener
        keyboard.on_press(self.handle_global_key_press)

    def handle_global_key_press(self, event):
        """
        Handles global key press events (from the keyboard library).
        """
        key_name = event.name
        print(f"Global key pressed: {key_name}")


    def update_frame(self):
        # Read a frame from the camera
        ret, frame = self.cap.read()
        if not ret:
            print("Failed to grab frame")
            return

        self.handleWebcamImage(frame)

        ################################################################################
        # warped img
        self.handleWarpedImage(frame)


        ################################################################################
        self.handle_recalibrate()



    def handleWebcamImage(self, frame):
        # Display FPS on the frame
        frame = self.fps_tracker.display_fps(frame)

        cv.imshow("Webcam", frame)

        # # Convert the frame to RGB format for PyQt
        # rgb_frame = cv.cvtColor(frame, cv.COLOR_BGR2RGB)
        # h, w, ch = rgb_frame.shape
        # bytes_per_line = ch * w
        # qt_image = QImage(rgb_frame.data, w, h, bytes_per_line, QImage.Format_RGB888)
        #
        # # Set the image in the QLabel
        # self.webcam_video.setPixmap(QPixmap.fromImage(qt_image))

    def handleWarpedImage(self, frame):
        if self.kbmTracker.kbm_corners is None or None in self.kbmTracker.kbm_corners:
            return

        frame_copy = frame.copy()
        drawn_img = None

        # Draw Hand tracking on the projection
        if self.draw_hands_button.isChecked():
            hand_landmarks = self.handTracker.get_hand_landmarks(frame_copy)
            self.handTracker.draw_landmarks(frame_copy, hand_landmarks)

        warped_img = self.kbmTracker.get_wapped_frame(frame_copy)

        # Draw Button Regions
        if self.draw_kbm_layout.isChecked():
            draw_on_img = warped_img if drawn_img is None else drawn_img
            drawn_img = self.kbmTracker.draw_button_regions(draw_on_img)

        show_img = warped_img if drawn_img is None else drawn_img

        if show_img.any: # Show the projection
            show_img = cv.resize(show_img, (0,0), fx=0.3, fy=0.3)
            # Convert the frame to RGB format for PyQt
            rgb_warped_img = cv.cvtColor(show_img, cv.COLOR_BGR2RGB)
            h, w, ch = rgb_warped_img.shape
            bytes_per_line = ch * w
            qt_warped_img = QImage(rgb_warped_img.data, w, h, bytes_per_line, QImage.Format_RGB888)

            # Create a QPixmap from the QImage
            pixmap = QPixmap.fromImage(qt_warped_img)

            # Scale the pixmap to fit the size of the video_feed label, maintaining aspect ratio
            scaled_pixmap = pixmap.scaled(self.warped_video.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation)

            # Set the scaled pixmap as the label's image
            self.warped_video.setPixmap(scaled_pixmap)

    def handle_recalibrate(self):
        if self.recalibrate_active:
            # Store the last 5 frames
            if len(self.prev_five_frames) < 5:
                print(len(self.prev_five_frames))
                ret, frame = self.cap.read()
                if frame is not None:
                    self.prev_five_frames.append(frame)
            else:
                # Recalibrate the KeyboardTracker with the last 5 frames
                self.kbmTracker.recalibrate_projection(self.prev_five_frames)
                self.recalibrate_active = False
                self.prev_five_frames = []
                print(self.kbmTracker.transformation_matrix)

    def start_recalibration(self):
        print("Recalibrate button clicked.")
        # Set flag to start recalibration and store frames
        self.recalibrate_active = True

    def closeEvent(self, event):

        keyboard.unhook_all()  # Remove all hooks to prevent lingering listeners
        event.accept()

        # Release video capture when the window is closed
        self.cap.release()
        cv.destroyAllWindows()
        event.accept()

    def disable_button_focus(self):
        # Define the types of widgets you want to apply the focus policy to
        button_types = (QPushButton, QCheckBox)

        # Iterate through all children and check if they are instances of any button type
        for widget in self.findChildren(QWidget):
            if isinstance(widget, button_types):
                widget.setFocusPolicy(Qt.NoFocus)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = VideoApp()
    window.show()
    sys.exit(app.exec_())
