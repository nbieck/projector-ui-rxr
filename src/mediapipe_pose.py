import cv2
import mediapipe as mp
import numpy as np


class MediapipeHandler():
    def __init__(self) -> None:
        self.mp_drawing = mp.solutions.drawing_utils
        self.mp_drawing_styles = mp.solutions.drawing_styles
        self.mp_holistic = mp.solutions.holistic

        self.holistic = self.mp_holistic.Holistic(
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5,
            model_complexity=0)

    def detectHands(self, image):
        idxs = np.where(np.sum(image, axis=2) != 0)
        self.pixel_min = np.min(idxs, axis=1)
        self.pixel_max = np.max(idxs, axis=1)
        image = image[self.pixel_min[0]:self.pixel_max[0],
                      self.pixel_min[1]:self.pixel_max[1]]

        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        self.image_height, self.image_width = image.shape[0:2]
        results = self.holistic.process(image)
        return results

    def drawLandmarks(self, image, results):
        # image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        self.mp_drawing.draw_landmarks(
            image[self.pixel_min[0]:self.pixel_max[0],
                  self.pixel_min[1]:self.pixel_max[1]],
            results.face_landmarks,
            self.mp_holistic.FACEMESH_CONTOURS,
            landmark_drawing_spec=None,
            connection_drawing_spec=self.mp_drawing_styles
            .get_default_face_mesh_contours_style())
        self.mp_drawing.draw_landmarks(
            image[self.pixel_min[0]:self.pixel_max[0],
                  self.pixel_min[1]:self.pixel_max[1]],
            results.pose_landmarks,
            self.mp_holistic.POSE_CONNECTIONS,
            landmark_drawing_spec=self.mp_drawing_styles
            .get_default_pose_landmarks_style())
        self.mp_drawing.draw_landmarks(
            image[self.pixel_min[0]:self.pixel_max[0],
                  self.pixel_min[1]:self.pixel_max[1]],
            results.right_hand_landmarks,
            self.mp_holistic.HAND_CONNECTIONS,
            self.mp_drawing_styles.get_default_hand_landmarks_style(),
            self.mp_drawing_styles.get_default_hand_connections_style())
        self.mp_drawing.draw_landmarks(
            image[self.pixel_min[0]:self.pixel_max[0],
                  self.pixel_min[1]:self.pixel_max[1]],
            results.left_hand_landmarks,
            self.mp_holistic.HAND_CONNECTIONS,
            self.mp_drawing_styles.get_default_hand_landmarks_style(),
            self.mp_drawing_styles.get_default_hand_connections_style())
        return image

    def getIndexFingerPositions(self, results):
        if results.right_hand_landmarks:
            # hand = results.multi_hand_landmarks[0]
            hand = results.right_hand_landmarks
            x = hand.landmark[8].x
            y = hand.landmark[8].y
            z = hand.landmark[8].z
            x = int(np.clip(x * self.image_width, 0, self.image_width-1))
            y = int(np.clip(y * self.image_height, 0, self.image_height-1))
            return x+self.pixel_min[1], y+self.pixel_min[0], z
        return None

    def getRightSholderPositions(self, results):
        if results.pose_landmarks:
            x = results.pose_landmarks.landmark[12].x
            y = results.pose_landmarks.landmark[12].y
            z = results.pose_landmarks.landmark[12].z
            x = int(np.clip(x * self.image_width, 0, self.image_width-1))
            y = int(np.clip(y * self.image_height, 0, self.image_height-1))
            return x+self.pixel_min[1], y+self.pixel_min[0], z
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
    cap = cv2.VideoCapture(0)
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
