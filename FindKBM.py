import cv2 as cv
import numpy as np
from PIL.ImageOps import invert
from PIL.ImageTransform import PerspectiveTransform
from matplotlib.pyplot import contour
from numpy.random import laplace

from util import Settings
from util import Colors


setting = Settings()

# Initialize the webcam capture
def initialize_webcam():
    cap = cv.VideoCapture(0, cv.CAP_DSHOW)
    if not cap.isOpened():
        print("Error: Could not access the webcam.")
        exit()

    cap.set(cv.CAP_PROP_AUTO_WB, 0)  # Disable auto white balance
    cap.set(cv.CAP_PROP_WHITE_BALANCE_BLUE_U, 4000)  # Set a fixed blue value (in Kelvin)
    cap.set(cv.CAP_PROP_WHITE_BALANCE_RED_V, 4000)  # Set a fixed red value (in Kelvin)

    return cap

def process_frame(frame):
    # cv.imshow('Webcam Feed - Original', frame)

    # Invert the image
    inv = cv.bitwise_not(frame)
    blur = cv.bilateralFilter(inv, 9, 75, 75)

    # Thresholding and conversion to grayscale
    threshold = cv.threshold(blur, 140, 255, cv.THRESH_BINARY)[1]
    gray = cv.cvtColor(threshold, cv.COLOR_BGR2GRAY)
    threshold2 = cv.threshold(gray, 160, 255, cv.THRESH_BINARY)[1]
    # cv.imshow('Webcam Feed - Threshold2', threshold2)

    # Canny edge detection
    canny = cv.Canny(threshold2, 100, 200)

    # Dilate the Canny edges to thicken them
    kernel = np.ones((3, 3), np.uint8)  # Adjust kernel size to control thickness
    thick_edges = cv.dilate(canny, kernel, iterations=1)
    # cv.imshow('Webcam Feed - Thickened Canny Edges', thick_edges)

    # Invert the thresholded result for further processing
    inverted = cv.bitwise_not(threshold2)

    return inverted

def find_contours(base_img, edges_frame):
    # Find contours from the edge-detected image
    contours, hierarchy = cv.findContours(edges_frame, cv.RETR_EXTERNAL, cv.CHAIN_APPROX_SIMPLE)

    # Biggest contour
    biggest = max(contours, key=cv.contourArea)
    # e = setting.get("epsilon")
    # e = e / 1000
    # print(e)

    processed_contours = cv.approxPolyDP(biggest, 0.02 * cv.arcLength(biggest, True), True)

    # cv.drawContours(base_img, [processed_contours], -1, (0, 255, 0), 2)

    # Display the base image with contours
    # cv.imshow('Webcam Feed - Contours', base_img)

    return processed_contours


def line_intersection(p1, p2, p3, p4):
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

def warp_perspective(frame, contour):
    if len(contour) != 5:
        return None

    copy = frame.copy()  # Copy the frame so the original image is not modified

    # Assuming frame is the image and contour is a list of contour points
    height, width = frame.shape[:2]  # Get the height and width of the image

    # Sort the contour points by their distance from the bottom-left corner (0, height)
    contour_sorted = sorted(contour,
                            key=lambda point: (np.sqrt(point[0][0] ** 2 + (point[0][1] - height) ** 2), point[0][0]))

    colors = [Colors.PINK, Colors.YELLOW, Colors.BLUE, Colors.GREEN, Colors.WHITE]

    # Draw the points and label them
    for i, point in enumerate(contour_sorted):
        cv.circle(copy, (point[0][0], point[0][1]), radius=5, color=colors[i], thickness=-1)
        cv.putText(copy, f"{i}", (point[0][0] + 4, point[0][1] - 4), cv.FONT_HERSHEY_SIMPLEX, 0.5, colors[i], 2)

    # Calculate the intersection of lines a (0-2) and b (1-3)
    p0 = contour_sorted[0][0]
    p1 = contour_sorted[1][0]

    p2 = contour_sorted[2][0]
    p4 = contour_sorted[4][0]

    p3 = contour_sorted[3][0]

    intersection = line_intersection(p0, p1, p2, p4)

    if intersection:
        # Draw the intersection point in red
        ix, iy = intersection
        cv.circle(copy, (int(ix), int(iy)), 5, (0, 0, 255), thickness=-1)  # Red color for intersection point
        cv.putText(copy, "Intersection", (int(ix) + 4, int(iy) - 4), cv.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)

    ################################################################################
    # Warp Perspective
    critical_points = np.float32([p3,p0,intersection,p4])

    transformMatrix = cv.getPerspectiveTransform(critical_points, np.float32([[0, 0], [width, 0], [width, height], [0, height]]))
    imgOutput = cv.warpPerspective(frame, transformMatrix, (width, height))

    cv.imshow("Output", imgOutput)








    # Optionally, display the frame with points and intersection
    cv.imshow('Contour Points and Intersection', copy)

    return copy


# Main method to capture video, process frames, and handle user input
def main():

    # setting.create("Contour Area", 0, 1000, 100)
    setting.create("epsilon", 0, 100, 10)

    # Load the keyboard template (make sure it's aligned with the perspective you expect)
    template = cv.imread('Resources/kbmTemplate.jpg')

    # Set up webcam capture
    cap = initialize_webcam()

    while True:
        # Capture frame-by-frame from webcam
        ret, frame = cap.read()

        if not ret:
            print("Error: Failed to grab frame.")
            break

        # Process the frame
        edges_frame = process_frame(frame)

        # Call find_contours to find and draw approximated contours on the base image
        contours = find_contours(frame, edges_frame)

        # Warp the perspective of the image
        warp_perspective(frame, contours)


        # Display the frame
        cv.imshow('Webcam Feed', frame)


        # Wait for a key press to break the loop (press 'q' to exit)
        if cv.waitKey(1) & 0xFF == ord('q'):
            break

    # Release the webcam and close any OpenCV windows
    cap.release()
    cv.destroyAllWindows()

# Run the main function
if __name__ == "__main__":
    main()
