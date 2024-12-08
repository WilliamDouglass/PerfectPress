import sys
import cv2
import time
from PyQt5.QtWidgets import QApplication, QLabel, QVBoxLayout, QWidget
from PyQt5.QtGui import QImage, QPixmap
from PyQt5.QtCore import QThread, pyqtSignal


class CaptureThread(QThread):
    frame_ready = pyqtSignal(object)  # Signal to send the captured frame to the main thread

    def __init__(self, cap):
        super().__init__()
        self.cap = cap
        self.running = True

    def run(self):
        while self.running:
            ret, frame = self.cap.read()
            if ret:
                # Convert the frame from BGR to RGB
                frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                # Emit the frame
                self.frame_ready.emit(frame)

    def stop(self):
        self.running = False
        self.wait()


class WebcamApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Webcam Display - 60 FPS")
        self.resize(640, 480)

        # QLabel to display the webcam feed
        self.image_label = QLabel(self)
        self.image_label.setScaledContents(True)

        # Layout for QLabel
        layout = QVBoxLayout()
        layout.addWidget(self.image_label)
        self.setLayout(layout)

        # Initialize OpenCV video capture with DSHOW backend
        self.cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
        if not self.cap.isOpened():
            raise RuntimeError("Error: Unable to access the webcam.")

        # Set the desired resolution and frame rate
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
        self.cap.set(cv2.CAP_PROP_FPS, 60)

        # Start the capture thread
        self.capture_thread = CaptureThread(self.cap)
        self.capture_thread.frame_ready.connect(self.update_image)
        self.capture_thread.start()

        # For performance debugging, measure FPS
        self.last_time = time.time()

    def update_image(self, frame):
        # Measure FPS for debugging
        current_time = time.time()
        fps = 1 / (current_time - self.last_time)
        self.last_time = current_time
        print(f"FPS: {fps:.2f}")

        # Convert the frame to QImage and display it
        height, width, channels = frame.shape
        bytes_per_line = channels * width
        q_image = QImage(frame.data, width, height, bytes_per_line, QImage.Format_RGB888)
        self.image_label.setPixmap(QPixmap.fromImage(q_image))

    def closeEvent(self, event):
        # Release resources on close
        self.capture_thread.stop()
        self.cap.release()
        event.accept()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = WebcamApp()
    window.show()
    sys.exit(app.exec_())
