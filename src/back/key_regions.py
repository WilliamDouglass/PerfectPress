import numpy as np
import cv2 as cv
import csv


########################################################################################################################
#   KeyRegions Class - Handles key mapping and region sorting
########################################################################################################################

class KeyRegions:
    def __init__(self, keymap_path="../../Resources/keyMappings.csv"):
        """
        Initializes KeyRegions object with keymap path.
        """
        self.template_processor = TemplateProcessor()
        self.keymap = self.load_keymap(keymap_path)  # Load the keymap from CSV
        self.sorted_button_regions = self.get_key_regions()  # Get the sorted key regions

    def get_region_id(self, key):
        """
        Fetches the region ID for the given key.
        """
        return self.keymap.get(key)

    def get_key_regions(self):
        """
        Retrieves and sorts the key regions.
        """
        regions = self.find_regions()
        sorted_regions = self.sort_regions(regions)
        return sorted_regions

    def load_keymap(self, path):
        """
        Loads the keymap from a CSV file and stores it as a dictionary.

        Parameters:
        - path: Path to the CSV file containing key mappings.
        """
        try:
            with open(path, "r") as file:
                csv_reader = csv.DictReader(file)
                keymap = {}
                for row in csv_reader:
                    keycode = row['key']
                    buttons = row['button'].split(', ')  # Split by commas to handle multiple buttons
                    for button in buttons:
                        keymap[button.strip()] = keycode  # Map the button to the keycode
                return keymap
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
        base_template = self.template_processor.cropped_template

        rows_y = []
        pad = 0.02 * base_template.shape[0]
        height_of_temp = base_template.shape[0] - pad
        dist_between_rows = height_of_temp // 5

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

        return out

    def display_regions(self):
        """
        Displays the regions on the template image with different colored rectangles and labels.
        """
        blank = np.zeros((self.cropped_template.shape[0], self.cropped_template.shape[1], 3), dtype=np.uint8)
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

    def find_regions(self):
        """
        Finds the regions on the template image by applying thresholding, blur, and erosion,
        followed by contour detection.
        """
        gray = cv.cvtColor(self.cropped_template, cv.COLOR_BGR2GRAY)
        inverted_image = 255 - gray  # Invert to make objects white
        _, threshold = cv.threshold(inverted_image, 20, 255, cv.THRESH_BINARY)

        # Apply blur and erosion to clean up noise
        blur = cv.medianBlur(threshold, 3)
        erode = cv.erode(blur, np.ones((5, 5), np.uint8), iterations=1)

        # Find contours
        contours, hierarchy = cv.findContours(erode, cv.RETR_TREE, cv.CHAIN_APPROX_SIMPLE)

        if contours is None:
            print('No contours found')
            return []

        return contours

########################################################################################################################
#   TemplateProcessor Class - Handles template loading and cropping
########################################################################################################################

class TemplateProcessor:

    def __init__(self, template_path="../../Resources/kbm_template.jpg"):
        """
        Initializes TemplateProcessor with the provided template image path.
        """
        self.original_template = cv.imread(template_path)
        self.cropped_template = self.crop_template()

    def crop_template(self):
        """
        Crops the template image based on pre-defined bounds.
        """
        # Ensure the image was loaded
        if self.original_template is None:
            print("Error: Image not found or unable to load.")
            return None

        # Replace the variables with the given values
        top_bound = 0
        bottom_bound = 39
        left_bound = 39
        right_bound = 16

        # Crop the image using the bounds
        crop = self.original_template[top_bound:self.original_template.shape[0] - bottom_bound,
                                      left_bound:self.original_template.shape[1] - right_bound]
        return crop
