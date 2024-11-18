import cv2 as cv
import mediapipe as mp

class HandTracking:

    def __init__(self):
        self.mpHands = mp.solutions.hands
        self.hands = self.mpHands.Hands()
        self.mpDraw = mp.solutions.drawing_utils

    def get_hand_landmarks(self,input_img):

        # bgr -> rgb
        img_rgb = cv.cvtColor(input_img, cv.COLOR_BGR2RGB)

        # Find Landmarks
        results = self.hands.process(img_rgb)

        return results

    def draw_landmarks(self, img, results):
        for handLMS in results.multi_hand_landmarks:
            self.mpDraw.draw_landmarks(img, handLMS, mp.solutions.hands.HAND_CONNECTIONS)
        return img


