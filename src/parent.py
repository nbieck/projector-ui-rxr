from multiprocessing import Process, Queue
import os
import time
import random
import numpy as np
import glfw

# import file 
import window
import math_utils as mu
import calibration 
import numpy.typing as npt


# sending transform matrix to window generator by queue
def write(q, rs_frustum : mu.Frustum, pr_frustum : mu.Frustum):

    while True:
        if q.empty():
            # 640*480
            # randomly generating window coordinate of camera view
            bl = np.array([random.uniform( 0.1, 0.4), random.uniform( 0.1, 0.4), -100])
            br = np.array([random.uniform(0.6, 0.9), random.uniform( 0.1, 0.4), -100])
            tl = np.array([random.uniform( 0.1, 0.4), random.uniform(0.6, 0.9), -100])
            tr = np.array([random.uniform(0.6, 0.9), random.uniform(0.6, 0.9), -100])

            button = np.array([bl,br,tr,tl])
            print(button)
            projector_view = []
            # frustum conversion from screen(camera) -> world world->screen(projector) 
            for pos in button:
                world_coord = rs_frustum.screen_to_world(pos)
                projector_view.append(pr_frustum.world_to_screen(world_coord))

            
            # bl = np.array([0.2, 0.2])
            # br = np.array([0.8, 0.2])
            # tl = np.array([0.2, 0.8])
            # tr = np.array([0.8, 0.8])
            print("bl: ", projector_view[0])
            print("br: ", projector_view[1])
            print("tl: ", projector_view[2])
            print("tr: ", projector_view[3])
            
            # convert to projection matrix
            trans_m = mu.threeD_to_fourD(mu.compute_matrix(projector_view[0][0:2],projector_view[1][0:2],projector_view[2][0:2],projector_view[3][0:2]))
            print(trans_m)
            # print('Process to write: {}'.format(os.getpid()))
            q.put(trans_m)
            
            time.sleep(0.5)


# creating the window based on the matrix received from the write function


buttons = np.array([[0, 0, 0, 1],
                    [0, 1, 0, 1],
                    [1, 1, 0, 1],
                    [1, 0, 0, 1]])
def read(q):

    trans_m = np.array([[1, 0, 0, 0],
                        [0, 1, 0, 0],
                        [0, 0, 1, 0],
                        [0, 0, 0, 1]])
    w = window.Window(buttons, trans_m)

    while not glfw.window_should_close(w.window):
        if not q.empty() and w.pressed:
            trans_m = q.get()
            w.pressed = False

            print("coordinate")
            print(trans_m)
            
        w.run(trans_m=trans_m)
        # w.set_up_texture_maps()
        # w.callibration()
    w.clear()


# main function
if __name__ == "__main__":
    # Parent process is creating the queue for child process

    # random points for callibration
    world_points = [np.array([100, 100, 1]),
                    np.array([250, 250, 1]),
                    np.array([500, 500, 1])]

    # realsense parameter
    realsense_aspect_ratio = 16/9
    realsense_hfov = 69.4
    realsense_vfov = 42.5

    # projector parameter
    projector_aspect_ratio = 16/9
    projector_hfov = 38.95

    # frustum for realsense and projector
    realsense_frustum = mu.Frustum(np.array([0,0,0]),np.array([0,0,-1]),np.array([0,1,0]),realsense_aspect_ratio,mu.AngleFormat.DEG, hfov=realsense_hfov)
    projector_frustum = mu.Frustum(np.array([0,0,0]),np.array([0,0,-1]),np.array([0,1,0]),projector_aspect_ratio,mu.AngleFormat.DEG, hfov=projector_hfov)
    
    # q = Queue()
    # pw = Process(target=write, args=(q,))

    # Creating a process for write function and read function.
    q = Queue()
    pw = Process(target=write, args=(q,realsense_frustum, projector_frustum,))
    pr = Process(target=read, args=(q,))

    # activating process
    pw.start()
    pr.start()

    # wait until pw ends
    pr.join()
    # pw is infinite loop, so it needs to stop 
    pr.terminate()
    pw.terminate()

