import cv2
import mediapipe as mp
import numpy as np


class MediapipeHandler():
    def __init__(self) -> None:
        self.mp_drawing = mp.solutions.drawing_utils
        self.mp_drawing_styles = mp.solutions.drawing_styles
        self.mp_hands = mp.solutions.hands
        self.hands = self.mp_hands.Hands(
            model_complexity=1,
            min_detection_confidence=0.2,
            min_tracking_confidence=0.2)
        self._x = 0
        self._y = 0
        self._z = 0

    def detectHands(self, image):
        idxs = np.where(np.sum(image, axis=2) != 0)
        self.pixel_min = np.min(idxs, axis=1)
        self.pixel_max = np.max(idxs, axis=1)
        image = image[self.pixel_min[0]:self.pixel_max[0],
                      self.pixel_min[1]:self.pixel_max[1]]

        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        self.image_height, self.image_width = image.shape[0:2]
        results = self.hands.process(image)
        return results

    def drawLandmarks(self, image, results):
        # image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        if results.multi_hand_landmarks:
            for hand_landmarks in results.multi_hand_landmarks:
                self.mp_drawing.draw_landmarks(
                    image[self.pixel_min[0]:self.pixel_max[0],
                          self.pixel_min[1]:self.pixel_max[1]],
                    hand_landmarks,
                    self.mp_hands.HAND_CONNECTIONS,
                    self.mp_drawing_styles.get_default_hand_landmarks_style(),
                    self.mp_drawing_styles.get_default_hand_connections_style())
        return image

    def getIndexFingerPositions(self, results, LPF=0):
        if results.multi_hand_landmarks:
            hand = results.multi_hand_landmarks[0]
            self._x = hand.landmark[7].x * (1-LPF) + self._x * LPF
            self._y = hand.landmark[7].y * (1-LPF) + self._y * LPF
            self._z = hand.landmark[7].z * (1-LPF) + self._z * LPF
            x_w = int(np.clip(self._x * self.image_width, 0, self.image_width-1))
            y_h = int(np.clip(self._y * self.image_height,
                      0, self.image_height-1))
            return x_w+self.pixel_min[1], y_h+self.pixel_min[0], self._z
        return None

    def isGestureNeutral(self, results):
        if results.multi_hand_landmarks:
            hand = results.multi_hand_landmarks[0]
            landmarks = np.zeros((21, 3))
            for i, landmark in enumerate(hand.landmark):
                landmarks[i][0] = landmark.x
                landmarks[i][1] = landmark.y
                landmarks[i][2] = landmark.z

            min_pos = np.min(landmarks, axis=0)
            max_pos = np.max(landmarks, axis=0)
            landmarks = (landmarks - min_pos) / (max_pos-min_pos)

            return np.sum((landmarks[4] - landmarks[20]) ** 2)
        return None


if __name__ == "__main__":
    MPH = MediapipeHandler()
    cap = cv2.VideoCapture(1)
    while cap.isOpened():
        success, image = cap.read()
        if not success:
            print("Ignoring empty camera frame.")
            continue

        results = MPH.detectHands(image)
        image = MPH.drawLandmarks(image, results)
        cv2.imshow('MediaPipe Hands', cv2.flip(image, 1))
        if cv2.waitKey(5) & 0xFF == 27:
            break
    cap.release()
