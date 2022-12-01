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

def read(q):

    buttons = np.array([[0.4, 0.4, 0 ,1],
                         [0.6, 0.4, 0, 1],
                         [0.6, 0.6, 0, 1], 
                         [0.4, 0.6, 0, 1]])

    trans_m = np.array([[1, 0, 0, 0],
                        [0, 1, 0, 0],
                        [0, 0, 1, 0],
                        [0, 0, 0, 1]])
    w = window.Window(buttons, trans_m)

    while not glfw.window_should_close(w.window):
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
    realsense_frustum = mu.Frustum(np.array([0,0,0]),np.array([0,0,-1]),np.array([0,1,0]),realsense_aspect_ratio,mu.AngleFormat.DEG, hfov=realsense_hfov)
    projector_frustum = mu.Frustum(np.array([0,0,0]),np.array([0,0,-1]),np.array([0,1,0]),projector_aspect_ratio,mu.AngleFormat.DEG, hfov=projector_hfov)

    # Creating a process for write function and read function.
    q = Queue()
    pr = Process(target=read, args=(q,))

    # activating process
    # pw.start()
    pr.start()

    try:
        while True:
            fps = int(1/(time.time() - t0))
            t0 = time.time()

            color_image, depth_image = RSH.getFrames()

            depth_colormap = cv2.applyColorMap(cv2.convertScaleAbs(
                depth_image, alpha=0.1), cv2.COLORMAP_JET)

            cv2.putText(color_image,
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

            window_point = np.array([[0.4, 0.4, 1], [0.6, 0.4, 1], [0.6, 0.6, 1], [0.4, 0.6, 1]], 
                                dtype=np.float32)
            # plane_equation [a, b, c, d] (ax + by + cz + d = 0)
            # z = (ax+by+d) / c
            
            
            plane_equation, points = results[0]

            

            sample_points = np.array([[0.5, 0.5, 0], [0.6, 0.5, 0], [0.5, 0.6, 0]])
            sample_points_world = []
            for i,uv in enumerate(sample_points):
                depth = depth_image[359-int(uv[1]*360), int(uv[0]*640)]
                sample_points_world.append(realsense_frustum.screen_to_world(np.array([uv[0], uv[1], depth])))

            vec1 = sample_points_world[1] - sample_points_world[0]
            vec2 = sample_points_world[2] - sample_points_world[0]
            vec1 /= np.linalg.norm(vec1)
            vec2 /= np.linalg.norm(vec2)
            normal = np.cross(vec2, vec1)
            print('normal', normal)

            # print('depth')
            norm_point = []
            
            for i, window_uv in enumerate(window_point):
                # x = window_uv[0] - 1280/2
                # y = window_uv[1] - 720/2
                # depth = -(plane_equation[0]*window_uv[0] + plane_equation[1]*window_uv[1] + plane_equation[3])/ plane_equation[2] 
                
                depth =  depth_image[359-int(window_uv[1]*360), int(window_uv[0]*640)]
                norm_point.append(realsense_frustum.screen_to_world(np.array([window_uv[0], window_uv[1], depth])))
            norm_point *= normal
            
            # for i in range(4):
            #     window_point[i][0] = float(window_point[i][0])
            #     window_point[i][1] = float(window_point[i][1])

            print('world coordinate')
            print(norm_point)
            
            projector_view = []
            for pos in norm_point:
                # world_coord = realsense_frustum.screen_to_world(pos)
                projector_view.append(projector_frustum.world_to_screen(pos))
            
            print('projector view')
            print(projector_view)
            # convert to projection matrix
            trans_m = mu.threeD_to_fourD(mu.compute_matrix(projector_view[0][0:2],projector_view[1][0:2],projector_view[2][0:2],projector_view[3][0:2]))
            

            print('trans mat')
            # trans_m = np.array([[1.53322398, 0.06136046, 0.       ,  0.09377517],
            #                     [0.47506514, 0.88252983, 0.       ,  0.02880868],
            #                     [0.        , 0.        , 0.       ,  0.        ],
            #                     [0.78449371, 0.17133674, 0.       ,  1.        ]])
            print(trans_m)    

            if q.empty():
                q.put(trans_m)

            color_image = RSH.drawPlanes(color_image, results)
            images = RSH.combineImages(color_image, depth_colormap)
            cv2.imshow('Color', images)

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
        
