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


# sending transform matrix to window generator by queue
def write(q):

    while True:

        if q.empty():
            bl = np.array([random.uniform(0.1,0.4), random.uniform(0.1,0.4)])
            br = np.array([random.uniform(0.4,0.9), random.uniform(0.1,0.4)])
            tl = np.array([random.uniform(0.1,0.4), random.uniform(0.4,0.9)])
            tr = np.array([random.uniform(0.4,0.9), random.uniform(0.4,0.9)])
            # bl = np.array([0.2, 0.2])
            # br = np.array([0.8, 0.2])
            # tl = np.array([0.2, 0.8])
            # tr = np.array([0.8, 0.8])
            print("bl: ", bl)
            print("br: ", br)
            print("tl: ", tl)
            print("tr: ", tr)
            
            trans_m = mu.threeD_to_fourD(mu.compute_matrix(bl,br,tr,tl))
            
            # print('Process to write: {}'.format(os.getpid()))
            q.put(trans_m)
            time.sleep(0.5)


# creating the window based on the matrix received from the write function


def read(q, frutsum):

    trans_m = np.array([[1, 0, 0, 0],
                        [0, 1, 0, 0],
                        [0, 0, 1, 0],
                        [0, 0, 0, 1]])

    while not glfw.window_should_close(w.window):
        if not q.empty() and w.pressed:
            trans_m = q.get()
            w.pressed = False
            print("coordinate")
            print(w.P)
            
        # w.run(trans_m=trans_m)
        w.callibration()
    w.clear()

if __name__ == "__main__":
    # Parent process is creating the queue for child process
    buttons = np.array([[[0, 0, 0, 1],
                        [0, 1, 0, 1],
                        [1, 1, 0, 1],
                        [1, 0, 0, 1]]])

    trans_m = np.array([[1, 0, 0, 0],
                        [0, 1, 0, 0],
                        [0, 0, 1, 0],
                        [0, 0, 0, 1]])

    world_points = [np.array([100, 100, 1]),
                    np.array([250, 250, 1]),
                    np.array([500, 500, 1])]
    w = window.Window(buttons, trans_m)

    hight = 480
    weight = 640
    frustum = calibration.calibrate(world_points=world_points, texture_points=w.callibration_point, aspect_ratio=weight/hight,hfov=0.4)

    q = Queue()
    pw = Process(target=write, args=(q,frustum,))

    # q = Queue()
    # pw = Process(target=write, args=(q,))
    pr = Process(target=read, args=(q,))

    # activating process
    pw.start()
    pr.start()

    # wait until pw ends
    pr.join()
    # pw is infinite loop, so it needs to stop 
    pr.terminate()
    pw.terminate()

