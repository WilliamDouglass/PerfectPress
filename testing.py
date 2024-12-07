import cv2 as cv
import numpy as np
from kbm_tracking import KeyboardTracker
from PyQt5.QtCore import QTimer, Qt

cv.namedWindow("Template", cv.WINDOW_NORMAL)

# Initialize the keyboard tracker and template
kbmTrack = KeyboardTracker()
regions, kbm_template = kbmTrack.init_kbm_template()


import_warped_img = cv.imread("Resources/warped_img_good.jpg")

# Create a blank image (initialize a black image with the same height and width as the template)
blank = np.zeros((kbm_template.shape[0], kbm_template.shape[1], 3), dtype=np.uint8)

# rows_y =[70,270,480,690,890]
rows_y = []
print(kbm_template.shape[:2])
pad = 0.02 * kbm_template.shape[0]
h_of_temp = kbm_template.shape[0] - pad
dist_between_rows = h_of_temp // 5
for i in range(5):
    rows_y.append(pad//2+dist_between_rows*i)
print(rows_y)


colors = [(0,0,255),(0,255,0),(255,0,0),(255,255,0),(255,0,255)]
radius = dist_between_rows//2
print(radius)

sorted_regions = [[] for _ in range(5)]  # Create a list with 5 empty sublists
# for i in range(5):
#     sorted_regions[i].append([])  # Now you can append to each sublist

# print(len(regions))


for button in regions:
    bound = cv.boundingRect(button)
    x, y, w, h = bound
    if rows_y[0]-radius <= y  <= rows_y[0]+radius:
        sorted_regions[0].append(bound)
    elif rows_y[1]-radius <= y <= rows_y[1]+radius:
        sorted_regions[1].append(bound)
    elif rows_y[2]-radius <= y  <= rows_y[2]+radius:
        sorted_regions[2].append(bound)
    elif rows_y[3]-radius <= y  <= rows_y[3]+radius:
        sorted_regions[3].append(bound)
    elif rows_y[4]-radius <= y  <= rows_y[4]+radius:
        sorted_regions[4].append(bound)



template = np.zeros((kbm_template.shape[0], kbm_template.shape[1], 3), dtype=np.uint8)
for i,row in enumerate(sorted_regions):
    row = sorted(row, key=lambda x: x[0])
    sorted_regions[i] = row
    for j,button in enumerate(row):
        x, y, w, h = button
        center = (x + w // 2, y + h // 2)
        cv.putText(template, f"{i}:{j}:{(y-(pad//2))//dist_between_rows%5}", center, cv.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2, cv.LINE_AA)
        cv.rectangle(template, (x, y), (x + w, y + h), colors[i], 2)


# Sort each row by x-coordinate
# Then append all to a single list
# Use the index to determine the button ID





# Resize template for display
# template = cv.resize(template, (0, 0), fx=0.5, fy=0.5)

# Function to handle mouse click events
def mouse_click(event, x, y, flags, param):
    if event == cv.EVENT_LBUTTONDOWN:
        print(f"Mouse clicked at: ({x}, {y})")

# Set the mouse callback function
cv.setMouseCallback("Template", mouse_click)

# Display the template
cv.imshow("Template", template)

# Wait until a key is pressed
cv.waitKey(0)
cv.destroyAllWindows()








class keyRegions:
    def __init__(self):
        self.buttonMap = {}
        self.sorted_button_regions = []

    class buttonRegion:
        def __init__(self, index, region):
            self.original_index = index
            self.x = region[0]
            self.y = region[1]
            self.width = region[2]
            self.height = region[3]

    def add_button_region(self, region, index):
        # Mapping index to Qt keys
        index_to_qt = {
            0: Qt.Key_Alt,
            2: Qt.Key_Control,
            # Continue with other key mappings
        }

        key = index_to_qt.get(index)
        if key is not None:
            # Create a new buttonRegion instance and store it in the buttonMap
            self.buttonMap[key] = self.buttonRegion(index, region)
        else:
            print(f"Index {index} not mapped to a Qt key.")

    def get_key_ID(self, key):
        print(f"Key: {key}\tID: {self.buttonMap.get(key)}")
