# from mediapipe_pose import MediapipeHandler
from mediapipe_handler import MediapipeHandler
from realsense_handler import RealsenseHandler
import cv2
import numpy as np
import time
import parent
from multiprocessing import Process, Queue
import window
import math_utils as mu
import calibration
import numpy.typing as npt
import glfw
from clicker import * 

def read(q, a):

    buttons = np.array([[0.4, 0.4, 0, 1],
                        [0.6, 0.4, 0, 1],
                        [0.6, 0.6, 0, 1],
                        [0.4, 0.6, 0, 1]])

    trans_m = np.array([[1, 0, 0, 0],
                        [0, 1, 0, 0],
                        [0, 0, 1, 0],
                        [0, 0, 0, 1]])
    w = window.Window(buttons, trans_m)
    clicked = clickFunc(w.changePic)

    while not glfw.window_should_close(w.window):
        if not a.empty():
            clicked.clicking(a.get())
        if not q.empty():
            trans_m = q.get()
            w.pressed = False

        w.run(trans_m=trans_m)
        # w.set_up_texture_maps()
        # w.callibration()
    w.clear()


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

    realsense_aspect_ratio = 16/9
    realsense_hfov = 69.4
    realsense_vfov = 42.5

    # projector parameter
    projector_aspect_ratio = 16/9
    projector_hfov = 38.95

    # frustum for realsense and projector
    realsense_frustum = mu.Frustum(np.array([0, 0, 0]), np.array(
        [0, 0, -1]), np.array([0, 1, 0]), realsense_aspect_ratio, mu.AngleFormat.DEG, hfov=realsense_hfov)
    projector_frustum = mu.Frustum(np.array([0, 0, 0]), np.array(
        [0, 0, -1]), np.array([0, 1, 0]), projector_aspect_ratio, mu.AngleFormat.DEG, hfov=projector_hfov)

    # Creating a process for write function and read function.
    q = Queue()
    click = Queue()
    pr = Process(target=read, args=(q,click,))

    # activating process
    # pw.start()
    pr.start()
    current_click_state = 0
    try:
        while True:
            fps = int(1/(time.time() - t0))

            color_image, depth_image = RSH.getFrames()
            cv2.putText(color_image,
                        str(fps),
                        org=(50, 50),
                        fontFace=cv2.FONT_HERSHEY_SIMPLEX,
                        fontScale=1.0,
                        color=(255, 0, 0),
                        thickness=2,
                        lineType=cv2.LINE_4
                        )
            t0 = time.time()

            mp_results = MPH.detectHands(color_image)
            cursor = MPH.getIndexFingerPositions(mp_results, LPF=0.3)
            color_image = MPH.drawLandmarks(color_image, mp_results)
            depth_colormap = cv2.applyColorMap(cv2.convertScaleAbs(
                depth_image, alpha=0.1), cv2.COLORMAP_JET)
            points, texcoords = RSH.getPointCloud()

            if count >= 10:
                results = RSH.detectPlanes(
                    points, texcoords, down_sampling_rate=1/41)
                count = 0
            count += 1
            # plane_equation [a, b, c, d] (ax + by + cz + d = 0)
            plane_equation, a = results[0]

            if cursor is not None:
                texcoords = np.asarray(
                    texcoords * np.asarray([depth_image.shape[1], depth_image.shape[0]]), dtype=np.uint16)
                p = np.argmin(np.sum(np.abs(texcoords - cursor[0:2]), axis=1))
                cursor_depth = calculateDistancePoint2Plane(
                    points[p], results[0][0]) * 100  # cm

                # print(cursor, "distance: ", cursor_depth)
                if cursor_depth < 2 and current_click_state == 0:
                    current_click_state = 1
                elif current_click_state == 1 and cursor_depth > 4:
                    current_click_state = 0

                click.put(current_click_state)
                c = (0, 255*current_click_state, 255)
                    
                cv2.drawMarker(color_image, (int(cursor[0]), int(cursor[1])), c, markerType=cv2.MARKER_CROSS,
                               markerSize=20, thickness=5, line_type=cv2.LINE_8)

            print("count: ", click)

            window_point = np.array([[0.5, 0.5, 1], [0.6, 0.4, 1], [0.6, 0.6, 1], [0.4, 0.6, 1]],
                                    dtype=np.float32)

            d = depth_image[359-int(window_point[0][1]*360), int(window_point[0][0]*640)]
            tmp = realsense_frustum.screen_to_world(np.array([window_point[0][0], window_point[0][1], d]))

            sample_points = np.array(
                [[0.5, 0.5, 0], [0.4, 0.5, 0], [0.5, 0.6, 0]])
            sample_points_world = []
            for i, uv in enumerate(sample_points):
                depth = depth_image[359-int(uv[1]*360), int(uv[0]*640)]
                sample_points_world.append(
                    realsense_frustum.screen_to_world(np.array([uv[0], uv[1], depth])))

            # nikals version
            # vec1 = sample_points_world[1] - sample_points_world[0]
            # vec2 = sample_points_world[2] - sample_points_world[0]
            # vec1 /= np.linalg.norm(vec1)
            # vec2 /= np.linalg.norm(vec2)
            # normal1 = np.cross(vec2, vec1)
            # print('n_normal', normal1)

            # takehiro version
            normal = np.array(
                 [-plane_equation[0], plane_equation[1], -plane_equation[2]])
            # print('t_normal', normal)
            # print('depth')
            norm_point = []

            WIDTH = 2000 #[mm]
            HEIGHT = 1000 #[mm]

            right = np.array([1, 0, 0]) - np.dot(normal,
                                                 np.array([1, 0, 0])) * normal
            right /= np.linalg.norm(right)
            up = np.array([0, 1, 0]) - np.dot(normal,
                                              np.array([0, 1, 0])) * normal
            up /= np.linalg.norm(up)

            corners = np.array([tmp - up * HEIGHT/2 - right * WIDTH/2,
                       tmp - up * HEIGHT/2 + right * WIDTH/2,
                       tmp + up * HEIGHT/2 + right * WIDTH/2,
                       tmp + up * HEIGHT/2 - right * WIDTH/2])

            projector_view = []
            for pos in corners:
                projector_view.append(projector_frustum.world_to_screen(pos))

            # convert to projection matrix
            try:
                trans_m = mu.threeD_to_fourD(mu.compute_matrix(
                    projector_view[0][0:2], projector_view[1][0:2], projector_view[2][0:2], projector_view[3][0:2]))
                if q.empty():
                    q.put(trans_m)
            except:
                pass
            # print('projector view')
            # print(projector_view)
            # print('trans mat')
            # print(trans_m)


            color_image = RSH.drawPlanes(color_image, results)
            combined_image = RSH.combineImages(color_image, depth_colormap)
            cv2.imshow('Color', combined_image)

            key = cv2.waitKey(1)
            if key & 0xFF == ord('q') or key == 27:
                cv2.destroyAllWindows()
                break
    finally:
        print("closing")
        time.sleep(1)
        del RSH
        del MPH

        # wait until pw ends
        # pr.join()
        # pw is infinite loop, so it needs to stop
        pr.terminate()
