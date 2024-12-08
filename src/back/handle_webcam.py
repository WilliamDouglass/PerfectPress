# recalibrate
# set the video feed from the front end
# draw the hands
# draw the keyboard layout
import cv2 as cv


class WebCamHandler:
    def __init__(self):
        self.capture = None

    def start_webcam(self):
        self.capture = cv.VideoCapture(0, cv.CAP_DSHOW)
        if not self.capture.isOpened():
            print("[WebCamHandler] Error: Could not open webcam.")
            return

    def stop_webcam(self):
        self.capture.release()

    def get_webcam_frame(self):
        if self.capture is None:
            # print("[WebcamHandler] Error: Webcam not started.")
            return None

        ret, frame = self.capture.read()
        if not ret:
            print("[WebcamHandler] Error: Could not read frame.")
            return None

        return frame

