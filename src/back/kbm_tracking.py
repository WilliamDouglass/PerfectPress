from tempfile import template

import cv2 as cv
import numpy as np
from numpy import dtype



class KeyboardTracker:
    def __init__(self):
        self.kbm_corners = [None] * 4
        button_regions, kbm_template = self.init_kbm_template()
        self.button_regions = button_regions
        self.og_kbm_template = kbm_template
        self.transformation_matrix = None
        pass

    def recalibrate_projection(self,frames):
        if frames is None:
            return

        combo_masked_frame = self.get_combined_mask_frame(frames)

        old_corners = self.kbm_corners
        self.kbm_corners = self.get_corners(combo_masked_frame)

        if self.kbm_corners is None:
            self.kbm_corners = old_corners


    def get_wapped_frame(self,frame):
        if frame is None:
            return
        if self.kbm_corners is None:
            return

        warped_frame = self.warp_frame(frame, self.kbm_corners)
        return warped_frame

    def get_kbm_mask(self,frame):

        gray = cv.cvtColor(frame, cv.COLOR_BGR2GRAY)

        # Apply GaussianBlur
        blur = cv.GaussianBlur(gray, (5, 5), 0)

        # Apply thresholding
        _, thresh = cv.threshold(blur, 150, 255, cv.THRESH_BINARY)

        processed_frame = thresh

        # Find contours on the processed frame
        contours, _ = cv.findContours(processed_frame, cv.RETR_TREE, cv.CHAIN_APPROX_SIMPLE)

        # If no contours are found, return early
        if not contours:
            return

        # Find the largest contour by area
        big = max(contours, key=cv.contourArea)

        # Find the convex hull of the largest contour
        hull = cv.convexHull(big)

        # Draw the convex hull on the frame
        blank = np.zeros_like(frame)
        cv.drawContours(blank, [hull], -1, (255, 255, 255), -2)  # Fill the contour with white
        blank = cv.dilate(blank, np.ones((5, 5), np.uint8), iterations=2)

        return blank

    def get_combined_mask_frame(self, frames):
        # Takes in an array of raw capture from webcam
        # Masks the kbm then or's them all together thus (Averaging them)

        if frames is None:
            return

        combo_frame = np.zeros_like(frames[0], dtype=np.uint8)
        for frame in frames:
            mask = self.get_kbm_mask(frame)
            if mask is None or None in mask:
                continue
            combo_frame = np.maximum(combo_frame,mask)

        # Convert to grayscale and apply Gaussian blur
        gray_blank = cv.cvtColor(combo_frame, cv.COLOR_BGR2GRAY)
        blur = cv.GaussianBlur(gray_blank, (5, 5), 0)

        return blur

    def get_corners(self, combo_mask):

        # Get Contours from combined frames
        contours, _ = cv.findContours(combo_mask, cv.RETR_TREE, cv.CHAIN_APPROX_SIMPLE)
        if len(contours) == 0:
            print("[get_corners] Failed did not find any contours")
            return None

        big = max(contours, key=cv.contourArea)
        approx = cv.approxPolyDP(big, 0.02 * cv.arcLength(big, True), True)

        if len(approx) != 5:
            print("[get_corners] Failed not 5 corners in aprox")
            return None

        # Sort points
        points = self.reorder(approx, combo_mask)

        ################################################################################

        # Calculate Missing corner
        new_point = self.line_intersection(points[2], points[0], points[3], points[4])

        # Add the new point to the list of points
        points = np.append(points, [new_point], axis=0)
        points = np.delete(points, [2,3], axis=0)

        # Reorder to [top_left, top_right, bottom_right, bottom_left]
        points = np.array([points[3], points[0], points[1], points[2]])

        return points

    def line_intersection(self,p1, p2, p3, p4):
        """
        Find the intersection of two lines formed by points p1-p2 and p3-p4.
        Each point is a tuple (x, y).
        """
        # Line 1 (p1, p2): y = m1 * x + b1
        # Line 2 (p3, p4): y = m2 * x + b2

        # Calculate the slope (m) and intercept (b) of the lines
        m1 = (p2[1] - p1[1]) / (p2[0] - p1[0]) if p2[0] != p1[0] else np.inf  # m1 for line a
        b1 = p1[1] - m1 * p1[0] if m1 != np.inf else p1[0]  # b1 for line a (special case for vertical line)

        m2 = (p4[1] - p3[1]) / (p4[0] - p3[0]) if p4[0] != p3[0] else np.inf  # m2 for line b
        b2 = p3[1] - m2 * p3[0] if m2 != np.inf else p3[0]  # b2 for line b (special case for vertical line)

        # Find intersection
        if m1 == m2:  # Parallel lines don't intersect
            return None

        if m1 != np.inf and m2 != np.inf:  # Both lines are not vertical
            x = (b2 - b1) / (m1 - m2)
            y = m1 * x + b1
            return (x, y)
        elif m1 == np.inf:  # Line 1 is vertical
            x = b1
            y = m2 * x + b2
            return (x, y)
        elif m2 == np.inf:  # Line 2 is vertical
            x = b2
            y = m1 * x + b1
            return (x, y)

    def reorder(self, myPoints, screen):
        # Reshape points to (5, 2) as intended
        myPoints = myPoints.reshape((5, 2))

        # Create a new array for sorted points
        myPointsNew = np.zeros((5, 2), dtype=np.int32)

        # Get the image dimensions
        height, width = screen.shape

        # Define the top-right corner coordinates
        top_right = np.array([width - 1, 0])

        # Calculate distances from each point to the top-right corner
        distances = [np.linalg.norm(point - top_right) for point in myPoints]

        # Sort points by distance to the top-right corner
        # Convert points to lists so they are not ambiguous in sorting
        sorted_points = [point.tolist() for _, point in sorted(zip(distances, myPoints))]

        # Assign sorted points to myPointsNew
        myPointsNew = np.array(sorted_points, dtype=np.int32)

        return myPointsNew

    def warp_frame (self, frame, points):
        if points is None:
            return None, None

        height, width = self.og_kbm_template.shape[:2]

        # Ensure points are in float32 format for the transformation function
        pts1 = np.float32(points)
        pts2 = np.float32([[0, 0], [width, 0], [width, height], [0, height]])

        # Compute the perspective transformation matrix and warp the frame
        matrix = cv.getPerspectiveTransform(pts1, pts2)
        self.transformation_matrix = matrix
        warped_image = cv.warpPerspective(frame, matrix, (width, height))
        warped_image = cv.rotate(warped_image, cv.ROTATE_180)

        result = warped_image

        return result

    def draw_button_regions(self,frame):
        result = cv.drawContours(frame, self.button_regions, -1, (0, 0, 255), 2)
        return result

    def init_kbm_template(self):
        # Load and prepare the template in grayscale
        og_template = cv.imread('./Resources/kbm_template.jpg')

        # Ensure the image was loaded
        if og_template is None:
            print("Error: Image not found or unable to load.")
            return

        # Replace the variables with the given values
        top_bound = 0
        bottom_bound = 39
        left_bound = 39
        right_bound = 16

        # Crop the image using the bounds
        crop = og_template[top_bound:og_template.shape[0] - bottom_bound, left_bound:og_template.shape[1] - right_bound]



        # Apply thresholding
        gray = cv.cvtColor(crop, cv.COLOR_BGR2GRAY)
        inverted_image = 255 - gray  # Invert to make objects white
        _, threshold = cv.threshold(inverted_image, 20, 255, cv.THRESH_BINARY)
        # cv.imshow('Thresholded Image', threshold)

        # Apply blur and erosion to clean up noise
        blur = cv.medianBlur(threshold, 3)
        # cv.imshow('Blurred Image', blur)

        # Erode to enhance contours (experiment with kernel size if needed)
        erode = cv.erode(blur, np.ones((5, 5), np.uint8), iterations=1)
        # cv.imshow('Eroded Image', erode)

        # Find contours
        contours, hierarchy = cv.findContours(erode, cv.RETR_TREE, cv.CHAIN_APPROX_SIMPLE)

        if contours is None:
            print('No contours found')
            return

        return contours, crop

