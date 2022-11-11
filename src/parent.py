from multiprocessing import Process, Queue
import os
import time
import random
import numpy as np
import glfw

# import file 
import window
import math_utils as mu


# sending transform matrix to window generator by queue
def write(q):

    while True:
        # bl = np.array([random.uniform(0,0.5), random.uniform(0,0.5)])
        # br = np.array([random.uniform(0.5,1.0), random.uniform(0,0.5)])
        # tl = np.array([random.uniform(0,0.5), random.uniform(0.5,1.0)])
        # tr = np.array([random.uniform(0.5,1.0), random.uniform(0.5,1.0)])
        bl = np.array([0.2, 0.2])
        br = np.array([0.8, 0.2])
        tl = np.array([0.2, 0.8])
        tr = np.array([0.8, 0.8])
        
        
        trans_m = mu.threeD_to_fourD(mu.compute_matrix(bl,br,tr,tl))
        
        print('Process to write: {}'.format(os.getpid()))
        q.put(trans_m)
        time.sleep(0.5)


# creating the window based on the matrix received from the write function

buttons = np.array([[[0, 0, 0, 1],
                     [0, 1, 0, 1],
                     [1, 1, 0, 1],
                     [1, 0, 0, 1]]])

def read(q):
    trans_m = np.array([[1, 0, 0, 0],
                      [0, 1, 0, 0],
                      [0, 0, 1, 0],
                      [0, 0, 0, 1]])
    
    w = window.Window(buttons, trans_m)
    print('Process to read: {}'.format(os.getpid()))

    while not glfw.window_should_close(w.window):
        if not q.empty():
            trans_m = q.get()
        w.run(trans_m=trans_m)
    w.clear()

if __name__ == "__main__":
    # Parent process is creating the queue for child process
    q = Queue()
    pw = Process(target=write, args=(q,))
    pr = Process(target=read, args=(q,))
    # activating process
    pw.start()
    pr.start()

    # wait until pw ends
    pr.join()
    # pw is infinite loop, so it needs to stop 
    pr.terminate()
    pw.terminate()

