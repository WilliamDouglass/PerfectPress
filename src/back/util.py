import cv2 as cv
import numpy as np

class Settings:
    def __init__(self, window_name="Settings Window"):
        self.window_name = window_name
        self.trackbars = {}

        # Create a window to display the trackbars
        cv.namedWindow(self.window_name)
        self.img = 255 * np.ones((300, 300, 3), dtype=np.uint8)

    def create(self, trackbar_name, min_value=0, max_value=255, initial_value=0):
        """Creates a trackbar with a given name, min, max values, and initial value."""
        cv.createTrackbar(trackbar_name, self.window_name, initial_value, max_value, lambda x: None)
        self.trackbars[trackbar_name] = initial_value

    def get(self, trackbar_name):
        """Returns the value of the trackbar by its name."""
        if trackbar_name in self.trackbars:
            return cv.getTrackbarPos(trackbar_name, self.window_name)
        else:
            print(f"Trackbar '{trackbar_name}' does not exist.")
            return None

    def show(self):
        cv.imshow(self.window_name, self.img)

    def printValues(self):
        for trackbar_name in self.trackbars:
            print(f"{trackbar_name}: {self.get(trackbar_name)}")

class Colors:
    # Public "final" color variables (uppercase by convention)
    PINK = (203, 0, 255)    # Bright Pink (Hot Pink)
    RED = (0, 0, 255)       # Red
    BLUE = (255, 0, 0)      # Blue
    GREEN = (0, 255, 0)     # Green
    WHITE = (255, 255, 255) # White
    YELLOW = (0, 255, 255)  # Yellow
