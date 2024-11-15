import cv2 as cv
import time
from util import Settings


def main():
    # Create the camera capture object
    cap = cv.VideoCapture(0, cv.CAP_DSHOW)
    if not cap.isOpened():
        print("Cannot open camera")
        exit()

    # Initialize variable for FPS calculation
    prev_time = time.time()

    while True:
        # Capture frame-by-frame
        ret, frame = cap.read()
        if not ret:
            print("Can't receive frame (stream end?). Exiting ...")
            break

        # Get the current position of the threshold and blur sliders
        threshold_value = cv.getTrackbarPos("Threshold", "Settings")
        blurSize = cv.getTrackbarPos("Blur", "Settings")

        # Process the frame with the given parameters
        # processed_frame = process_image(frame, threshold_value, blurSize)

        # Calculate and display FPS on the frame
        prev_time = display_fps(frame, prev_time)

        # Display the processed frame
        cv.imshow("Frame", frame)

        # Check for 'q' key press to exit
        if cv.waitKey(1) == ord('q'):
            break

    # Release resources
    cap.release()
    cv.destroyAllWindows()


def process_image(image, threshold_value=130, blurSize=5):
    # Ensure blurSize is odd (required for blurring)
    blurSize += 0 if blurSize % 2 == 1 else 1

    # Convert to grayscale
    gray = cv.cvtColor(image, cv.COLOR_BGR2GRAY)

    # Apply threshold using the slider value
    retval, threshold = cv.threshold(gray, threshold_value, 255, cv.THRESH_BINARY)
    cv.imshow("threshold", threshold)

    # Optionally apply additional processing (e.g., blurring, edge detection)
    blurred = cv.blur(threshold, (blurSize, blurSize))
    cv.imshow("blurred", blurred)

    edges = cv.Canny(blurred, 50, 150)
    cv.imshow("canny", edges)

    return edges


def display_fps(frame, prev_time):
    """
    Calculate FPS and display it on the given frame.

    Parameters:
    - frame: The image frame where FPS is to be displayed.
    - prev_time: The previous time when the last frame was processed.

    Returns:
    - Updated prev_time for the next frame.
    """
    # Calculate FPS
    current_time = time.time()
    fps = 1 / (current_time - prev_time)
    prev_time = current_time

    # Display FPS on the frame
    cv.putText(frame, f"FPS: {fps:.2f}", (10, 30), cv.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

    return prev_time


def nothing(x):
    # Dummy function for createTrackbar
    pass


if __name__ == "__main__":
    main()
