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





class KeyRegions:
    def __init__(self, regions, template, keymap_path="keyMappings.csv"):
        """
        Initializes the KeyRegions class with the given regions and template.

        Parameters:
        - regions: List of regions to be processed (likely contours or bounding boxes).
        - template: Image template to extract region information.
        - keymap_path: Path to the key mappings CSV (defaults to "keyMappings.csv").
        """
        self.template = template
        self.keymap = {}  # Initialize an empty dictionary for the keymap
        self.sorted_button_regions = []
        self.sort_regions(regions)
        self.load_keymap(keymap_path)  # Load the keymap from the provided CSV path

    def load_keymap(self, path):
        """
        Loads the keymap from a CSV file and stores it as a dictionary.

        Parameters:
        - path: Path to the CSV file containing key mappings.
        """
        try:
            with open(path, "r") as file:
                csv_reader = csv.DictReader(file)
                for row in csv_reader:
                    keycode = row['key']
                    buttons = row['button'].split(', ')  # Remove brackets and split by commas

                    for button in buttons:
                        self.keymap[button.strip()] = keycode  # Map the button to the keycode
        except FileNotFoundError:
            print(f"Error: The file '{path}' was not found.")
        except KeyError as e:
            print(f"Error: Missing expected key in CSV file: {e}")
        except Exception as e:
            print(f"An unexpected error occurred while loading the keymap: {e}")

    def sort_regions(self, regions):
        """
        Sorts regions into rows based on their Y-coordinate, assuming the template divides the regions
        into 5 rows.

        Parameters:
        - regions: List of regions (bounding boxes) to be sorted.

        Returns:
        - A list of lists, each containing bounding boxes sorted into rows.
        """
        rows_y = []
        pad = 0.02 * self.template.shape[0]
        h_of_temp = self.template.shape[0] - pad
        dist_between_rows = h_of_temp // 5

        # Calculate the Y-coordinate positions for each row
        for i in range(5):
            rows_y.append(pad // 2 + dist_between_rows * i)

        radius = dist_between_rows // 2
        out = [[] for _ in range(5)]  # Create a list with 5 empty sublists to store the sorted regions

        # Sort regions into the appropriate row based on the Y-coordinate
        for button in regions:
            bound = cv.boundingRect(button)
            x, y, w, h = bound
            for i, row_y in enumerate(rows_y):
                if row_y - radius <= y <= row_y + radius:
                    out[i].append(bound)
                    break

        self.sorted_button_regions = out

    def display_regions(self):
        """
        Displays the regions on the template image with different colored rectangles and labels.
        """
        blank = np.zeros((self.template.shape[0], self.template.shape[1], 3), dtype=np.uint8)
        colors = [(0, 0, 255), (0, 255, 0), (255, 0, 0), (255, 255, 0), (255, 0, 255)]
        template = blank.copy()

        for i, row in enumerate(self.sorted_button_regions):
            row = sorted(row, key=lambda x: x[0])  # Sort each row by the X-coordinate (left to right)
            self.sorted_button_regions[i] = row
            for j, button in enumerate(row):
                x, y, w, h = button
                center = (x + w // 2, y + h // 2)
                cv.putText(template, f"{i}:{j}", center, cv.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2, cv.LINE_AA)
                cv.rectangle(template, (x, y), (x + w, y + h), colors[i], 2)

        cv.imshow("Template", template)

    def get_region_id(self, key):
        return self.keymap.get(key)


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












