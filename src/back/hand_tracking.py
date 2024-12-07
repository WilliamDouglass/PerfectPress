import cv2 as cv
import mediapipe as mp

class HandTracker:

    def __init__(self):
        self.mpHands = mp.solutions.hands
        self.hands = self.mpHands.Hands()
        self.mpDraw = mp.solutions.drawing_utils

    def get_hand_landmarks(self,input_img):
        if input_img is None:
            return None

        # bgr -> rgb
        img_rgb = cv.cvtColor(input_img, cv.COLOR_BGR2RGB)

        # Find Landmarks
        results = self.hands.process(img_rgb)

        return results

    def draw_landmarks(self, img, results):
        if results.multi_hand_landmarks is None:
            return img

        # Define the fingertip landmark indices
        fingertip_indices = [4, 8, 12, 16, 20]

        for hand_landmarks in results.multi_hand_landmarks:
            for index in fingertip_indices:
                # Get the x,y coordinates of the landmark
                x = int(hand_landmarks.landmark[index].x * img.shape[1])
                y = int(hand_landmarks.landmark[index].y * img.shape[0])

                # Draw a circle on the image
                cv.circle(img, (x, y), 2, (0, 255, 0), cv.FILLED)
        return img


