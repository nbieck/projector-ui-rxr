from multiprocessing import Process, Queue
import os
import time
import random
import numpy as np
import glfw

# import file 
import window


# sending transform matrix to window generator by queue
def write(q):

    while True:
        trans_m = np.array([[1, 0, 0, 0],
                            [0, 1, 0, 0],
                            [0, 0, 1, 0],
                            [random.random(), 0, 0, 1]])
        print('Process to write: {}'.format(os.getpid()))
        q.put(trans_m)
        time.sleep(random.random())


# creating the window based on the matrix received from the write function
def read(q):
    value = np.array([[1, 0, 0, 0],
                      [0, 1, 0, 0],
                      [0, 0, 1, 0],
                      [0, 0, 0, 1]])

    w = window.Window(window.buttons, window.trans_m)
    print('Process to read: {}'.format(os.getpid()))

    while not glfw.window_should_close(w.window):
        if not q.empty():
            value = q.get()
            print(value)
        w.run(trans_m=value)
    w.clear()

# Parent process is creating the queue for child process
q = Queue()
pw = Process(target=write, args=(q,))
pr = Process(target=read, args=(q,))
# activating process
pw.start()
pr.start()

# wait until pw ends
pw.join()
# pw is infinite loop, so it needs to stop 
pr.terminate()

