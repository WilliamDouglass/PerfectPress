import cv2 as cv
import mediapipe as mp
import time
from util import Settings
from matplotlib import pyplot as plt

"""
Youtube Videos to learn:

https://www.youtube.com/watch?v=tk9war7_y0Q
https://www.youtube.com/watch?v=ON_JubFRw8M


https://www.youtube.com/watch?v=P5FTEryiTl4


"""



def draw_fps(pTime,img):
    cTime = time.time()
    fps = 1 / (cTime - pTime) if cTime - pTime > 0 else 0

    # Display FPS on the main image
    textX = 0
    textY = 30
    cv.putText(img, f"FPS: {int(fps)}", (textX, textY), cv.FONT_HERSHEY_PLAIN, 2, (0, 255, 0), 2)

    return img, cTime

def find_hands(img, hands):
    """
    This function processes the input image to detect hands using MediaPipe's Hands solution.

    Parameters:
        img (ndarray): The input image (BGR format).
        hands (mediapipe.Hands): The MediaPipe Hands object for hand detection.

    Returns:
        img (ndarray): The input image with hand landmarks drawn.
        results (mediapipe.framework.formats.landmark_pb2.HandLandmarkList): The detection results containing hand landmarks.
    """
    # Convert the image to RGB (MediaPipe expects RGB input)
    imgRGB = cv.cvtColor(img, cv.COLOR_BGR2RGB)

    # Process the image and detect hand landmarks
    results = hands.process(imgRGB)

    # If hands are detected, draw the landmarks on the image
    if results.multi_hand_landmarks:
        for handLMS in results.multi_hand_landmarks:
            mpDraw = mp.solutions.drawing_utils
            mpDraw.draw_landmarks(img, handLMS, mp.solutions.hands.HAND_CONNECTIONS)

    return img, results

def process_Keyboard(img, settings):
    # Convert to grayscale and apply thresholding
    gray = cv.cvtColor(img, cv.COLOR_BGR2GRAY)
    retval, threshold = cv.threshold(gray, 150, 255, cv.THRESH_BINARY)

    # Apply bilateral filtering to smooth the image while preserving edges
    blurred = cv.bilateralFilter(threshold, 10, 200, 200)

    # Detect edges using Canny
    edges = cv.Canny(blurred, 50, 150)

    # Display processed images for debugging purposes
    cv.imshow("Threshold", threshold)
    cv.imshow("Blurred", blurred)
    cv.imshow("Canny Edges", edges)

    cv.imwrite("./Resources/CannyIMG.jpg", edges)  # Save as a JPEG image


    # # Template matching
    # h, w = img.shape[:2]
    # template = cv.imread("./Resources/kbmTemplate.jpg", 0)  # Load template image in grayscale
    #
    # # Perform template matching using cv.TM_SQDIFF method
    # res = cv.matchTemplate(edges, template, cv.TM_SQDIFF)
    #
    # # Normalize the result to improve visualization
    # cv.normalize(res, res, 0, 1, cv.NORM_MINMAX)
    #
    # # Display the result of template matching
    # plt.imshow(res, cmap='gray')
    # plt.title('Template Matching Result')
    # plt.colorbar()  # Optional: add color bar to visualize matching scores
    # plt.show()






def init_settings():
    settings = Settings()
    # Bars for Vars

    return settings

def main():
    cap = cv.VideoCapture(0,cv.CAP_DSHOW)
    cap.set(cv.CAP_PROP_FPS, 30)

    mpHands = mp.solutions.hands
    hands = mpHands.Hands(max_num_hands=8)
    mpDraw = mp.solutions.drawing_utils

    pTime = 0  # Previous time

    settings = init_settings()


    #######################################################################################
    # Main Loop
    #######################################################################################
    while True:
        success, img = cap.read()
        if not success:
            print("Failed to grab frame.")
            break

        process_Keyboard(img,settings)


        img, results = find_hands(img, hands)


        # FPS calculation
        imgFPS,pTime = draw_fps(pTime,img)

        # Display the main image
        cv.imshow("Image", imgFPS)

        # Break the loop if 'q' is pressed
        if cv.waitKey(1) & 0xFF == ord('q'):
            break


    settings.printValues()
    cap.release()
    cv.destroyAllWindows()


if __name__ == "__main__":
    main()
