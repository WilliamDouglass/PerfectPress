import csv

import cv2 as cv
import numpy as np
from kbm_tracking import KeyboardTracker
from PyQt5.QtCore import QTimer, Qt
import keyboard

cv.namedWindow("Template", cv.WINDOW_NORMAL)

# Initialize the keyboard tracker and template
kbmTrack = KeyboardTracker()
regions, kbm_template = kbmTrack.init_kbm_template()








keyRegions = KeyRegions(regions, kbm_template)
keyRegions.display_regions()


# Function to handle mouse click events
def mouse_click(event, x, y, flags, param):
    if event == cv.EVENT_LBUTTONDOWN:
        print(f"Mouse clicked at: ({x}, {y})")

# Set the mouse callback function
cv.setMouseCallback("Template", mouse_click)

def handle_global_key_press(event):
    """
    Handles global key press events (from the keyboard library).
    """
    key_name = event.name
    print(f"{key_name} -> {keyRegions.get_region_id(key_name)}")

keyboard.on_press(handle_global_key_press)

while True:
    # Check if the window is closed by checking its state
    if cv.getWindowProperty("Template", cv.WND_PROP_VISIBLE) < 1:
        break  # Exit loop if the window is closed

    # Wait for a key event indefinitely
    cv.waitKey(1)
cv.destroyAllWindows()












