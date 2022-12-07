# from mediapipe_pose import MediapipeHandler
from mediapipe_handler import MediapipeHandler
from realsense_handler import RealsenseHandler
import cv2
import numpy as np
import time


def calculateDistancePoint2Plane(point, plane):

    # point: x,y,z
    # plane: a,b,c,d (ax + by + cz + d = 0)
    dis = np.abs(np.sum(plane[0:3] * point) +
                 plane[3]) / np.sqrt(np.sum(plane[0:3]**2))
    return dis


if __name__ == "__main__":
    RSH = RealsenseHandler()
    MPH = MediapipeHandler()
    UI_base_depth = 0
    t0 = 0
    count = 30
    try:
        while True:
            fps = int(1/(time.time() - t0))
            t0 = time.time()

            color_image, depth_image = RSH.getFrames()

            mp_results = MPH.detectHands(color_image)
            cursor = MPH.getIndexFingerPositions(mp_results, LPF=0.2)
            
            depth_colormap = cv2.applyColorMap(cv2.convertScaleAbs(
                depth_image, alpha=0.1), cv2.COLORMAP_JET)
            image = MPH.drawLandmarks(color_image, mp_results)
            UI_img = np.zeros((720, 1280, 3), dtype=np.uint8)

            cv2.putText(image,
                        str(fps),
                        org=(50, 50),
                        fontFace=cv2.FONT_HERSHEY_SIMPLEX,
                        fontScale=1.0,
                        color=(255, 0, 0),
                        thickness=2,
                        lineType=cv2.LINE_4
                        )

            points, texcoords = RSH.getPointCloud()

            if count >= 10:
                results = RSH.detectPlanes(
                    points, texcoords, down_sampling_rate=1/41)
                count = 0
            count += 1

            h, w = color_image.shape[0:2]
            left_up = (int(w/3.0), int(h/3.0))
            right_down = (int(w*2/3.0), int(h*2/3.0))

            cv2.rectangle(image, left_up, right_down, (255, 0, 0))
            UI_area_depth = depth_image[left_up[1]:right_down[1],
                                        left_up[0]:right_down[0]]
            UI_depth = np.mean(UI_area_depth[UI_area_depth > 0])

            if cursor is not None:
                texcoords = np.asarray(
                    texcoords * np.asarray([w, h]), dtype=np.uint16)

                p = np.argmin(np.sum(np.abs(texcoords - cursor[0:2]), axis=1))
                cursor_depth = calculateDistancePoint2Plane(
                    points[p], results[0][0]) * 100  # cm
                print(cursor, "distance: ", cursor_depth)

                c = (255, 0, 0)

                if cursor_depth < 2 \
                        and left_up[1] < cursor[1] < right_down[1] \
                        and left_up[0] < cursor[0] < right_down[0]:
                    c = (0, 0, 255)
                    UI_img[int(UI_img.shape[0]/3):int(2*UI_img.shape[0]/3),
                           int(UI_img.shape[1]/3):int(2*UI_img.shape[1]/3)] = [0, 0, 50]

                cv2.drawMarker(image, (int(cursor[0]), int(cursor[1])), c, markerType=cv2.MARKER_CROSS,
                               markerSize=20, thickness=5, line_type=cv2.LINE_8)
            else:
                UI_base_depth = UI_depth

            depth_colormap = RSH.drawPlanes(depth_colormap, results)
            image = RSH.drawPlanes(image, results)
            images = RSH.combineImages(image, depth_colormap)
            # cv2.imshow('Color', cv2.resize(
            #     images, (int(images.shape[1]/2), int(images.shape[0]/2))))
            cv2.imshow('Color', images)

            # cv2.imshow('Depth', depth_colormap)

            cv2.imshow('UI', UI_img)

            key = cv2.waitKey(1)
            if key & 0xFF == ord('q') or key == 27:
                cv2.destroyAllWindows()
                break
    finally:
        print("closing")
        time.sleep(1)
        del RSH
        del MPH
