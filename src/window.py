import glfw
from OpenGL.GL import *
from ctypes import Structure, sizeof
import numpy as np
import math

width = 640
height = 480

trans_m = np.array([[1, 0, 0, 0],
                    [0, 1, 0, 0],
                    [0, 0, 1, 0],
                    [0, 0, 0, 1]])

class Window:
    def __init__(self, features, trans_m) -> None:
        self.trans_m = trans_m
        self.features = features
        self.pressed = False
        self.P = None
        self.callibration_point=[
                np.array([0.05, 0.05]),
                np.array([0.5, 0.5]),
                np.array([0.95,0.95])]

        if not glfw.init():
            raise RuntimeError('Could not initialize GLFW3')


        self.window = glfw.create_window(glfw.get_video_mode(glfw.get_primary_monitor()).size[0],glfw.get_video_mode(glfw.get_primary_monitor()).size[1], 'mouse on GLFW', None, None)
        # print(glfw.get_video_mode(glfw.get_primary_monitor()).size[0])
        print()
        if not self.window:
            glfw.terminate()
            raise RuntimeError('Could not create an window')
        
        self.init()
      

    def init(self):
        # glfw.set_cursor_pos_callback(self.window, self.cursor_pos)
        # glfw.set_cursor_enter_callback(self.window, self.cursor_enter)
        glfw.set_mouse_button_callback(self.window, self.mouse_button)
        glfw.make_context_current(self.window)

        glClearColor(0.0, 0.0, 0.0, 1.0)
        glOrtho(0.0, 1.0, 0.0, 1.0, -1.0, 1.0)
        # self.display(self.trans_m)   # necessary only on Windows
    

    def callibration(self): 
        
        glfw.wait_events_timeout(1e-3)
        self._callibrationDisplay()
        glfw.poll_events()

    def _callibrationDisplay(self):
        glClear(GL_COLOR_BUFFER_BIT)

        for i in range(3):
            glBegin(GL_POLYGON)
            glColor3f(i==0, i==1, i==2)
            glVertex2f(self.callibration_point[i][0]-0.05,self.callibration_point[i][1]-0.05)
            glVertex2f(self.callibration_point[i][0]-0.05,self.callibration_point[i][1]+0.05)
            glVertex2f(self.callibration_point[i][0]+0.05,self.callibration_point[i][1]+0.05)
            glVertex2f(self.callibration_point[i][0]+0.05,self.callibration_point[i][1]-0.05)
            glEnd()

        glfw.swap_buffers(self.window)
    

    def clear(self):
        glfw.terminate()

  
    def run(self, trans_m, size=None, pos=None):
        # print("run",trans_m)
        glfw.wait_events_timeout(1e-3)
        self.display(trans_m, size, pos)
        glfw.poll_events()


    def display(self,trans_m, size=None, pos=None):
        glClear(GL_COLOR_BUFFER_BIT)
        self.draw(self.features, trans_m, size, pos)
        glfw.swap_buffers(self.window)


    def draw(self, tool, trans_m, size=None, pos=None):
        glColor3f(1.0, 1.0, 1.0)

        for f in tool:
            glBegin(GL_POLYGON)
    
            if size is not None and pos is not None:
                f = f*size + pos

            p = trans_m @ f.T
            self.P = p.T
            for vt in p.T:
                glVertex4f(vt[0],vt[1], vt[2], vt[3])

            glEnd()
    

    def cursor_pos(self, window, xpos, ypos):
        x = xpos/width
        y = ypos/height
        if x > self.features[0][0][0] and y > self.features[0][0][1] and x < self.features[0][2][0] and y < self.features[0][2][1]:
            print("self.button 1 pressed")

        # if x > self.features[1][0][0] and y > self.features[1][0][1] and x < self.features[1][2][0] and y < self.features[1][2][1]:
        #     print("self.button 2 pressed")


    def cursor_enter(self, window, entered):
        print('cursor_enter:', entered)


    def mouse_button(self, window, button, action, mods):
        pos = glfw.get_cursor_pos(window)
        print('mouse:', button, end='')

        if button == glfw.MOUSE_BUTTON_LEFT:
            self.pressed = True
            print('(Left)', end='')
        if button == glfw.MOUSE_BUTTON_RIGHT:
            print('(Right)', end='')
        if button == glfw.MOUSE_BUTTON_MIDDLE:
            print('(Middle)', end='')

        if action == glfw.PRESS:
            print(' press')
        elif action == glfw.RELEASE:
            print(' release')
        else:
            print(' hogehoge')

        x, y = pos
        print(pos, x, y)
