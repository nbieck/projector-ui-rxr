from mediapipe_handler import MediapipeHandler
from realsense_handler import RealsenseHandler
import cv2
import numpy as np

if __name__ == "__main__":
    RSH = RealsenseHandler()
    MPH = MediapipeHandler()
    UI_base_depth = 0
    try:
        while True:
            color_image, depth_image = RSH.getFrames()
            hands = MPH.detectHands(color_image)
            cursor = MPH.getIndexFingerPositions(hands)

            image = MPH.drawLandmarks(color_image, hands)

            h, w = color_image.shape[0:2]
            left_up = (int(w/4.0), int(h/4.0))
            right_down = (int(w*3/4.0), int(h*3/4.0))
            cv2.rectangle(image, left_up, right_down, (255, 0, 0))

            UI_area_depth = depth_image[left_up[1]
                :right_down[1], left_up[0]:right_down[0]]
            UI_depth = np.mean(UI_area_depth[UI_area_depth > 0])

            if cursor is not None:
                cursor_depth = depth_image[cursor[1], cursor[0]]
                print(UI_depth, cursor_depth)

                c = (255, 0, 0)

                if UI_base_depth - cursor_depth < 30 \
                        and left_up[1] < cursor[0] < right_down[1] \
                        and left_up[0] < cursor[1] < right_down[0]:
                    c = (0, 0, 255)

                cv2.drawMarker(image, (int(cursor[0]), int(cursor[1])), c, markerType=cv2.MARKER_CROSS,
                               markerSize=20, thickness=5, line_type=cv2.LINE_8)
            else:
                UI_base_depth = UI_depth

            images = RSH.combineImages(image, depth_image)
            cv2.namedWindow('Align Example', cv2.WINDOW_AUTOSIZE)
            cv2.imshow('Align Example', images)

            key = cv2.waitKey(1)
            if key & 0xFF == ord('q') or key == 27:
                cv2.destroyAllWindows()
                break
    finally:
        del RSH
        del MPH
