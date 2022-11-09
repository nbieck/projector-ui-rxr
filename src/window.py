import glfw
from OpenGL.GL import *
from ctypes import Structure, sizeof
import numpy as np

width = 640
height = 480

class Window:
    def __init__(self) -> None:
        self.trans_m = np.array([[1, 0, 0, 0],
                                 [0, 1, 0, 0],
                                 [0, 0, 1, 0],
                                 [0, 0, 0, 1]])

        self.button1 = np.array([[0.1,  0.25, 0, 1],
                                 [0.40, 0.25, 0, 1],
                                 [0.40, 0.75, 0, 1],
                                 [0.1,  0.75, 0, 1]])

        self.button2 = np.array([[0.6,  0.25, 0, 1],
                                 [0.90, 0.25, 0, 1],
                                 [0.90, 0.75, 0, 1],
                                 [0.6,  0.75, 0, 1]])
        if not glfw.init():
            raise RuntimeError('Could not initialize GLFW3')


        self.window = glfw.create_window(width, height, 'mouse on GLFW', None, None)
        if not self.window:
            glfw.terminate()
            raise RuntimeError('Could not create an window')
      
    def init(self):
        glClearColor(0.0, 1.0, 0.0, 1.0)
        glOrtho(0.0, 1.0, 0.0, 1.0, -1.0, 1.0)
        self.display()   # necessary only on Windows
    
    def run(self):

        glfw.set_cursor_pos_callback(self.window, self.cursor_pos)
        glfw.set_cursor_enter_callback(self.window, self.cursor_enter)
        glfw.set_mouse_button_callback(self.window, self.mouse_button)
        glfw.set_scroll_callback(self.window, self.scroll)
        glfw.set_window_refresh_callback(self.window, self.window_refresh)
        glfw.make_context_current(self.window)

        self.init()

        while not glfw.window_should_close(self.window):
            glfw.wait_events_timeout(1e-3)

        glfw.terminate()

  
    def draw(self, tool):
        glColor3f(1.0, 1.0, 1.0)
        glBegin(GL_POLYGON)
        for vt in tool:
            w = np.dot(self.trans_m, vt.T)
            glVertex2f(w[0]/w[2],w[1]/w[2])
        glEnd()

    def display(self):
        glClear(GL_COLOR_BUFFER_BIT)

        self.draw(self.button1)
        self.draw(self.button2)

        glfw.swap_buffers(self.window)

    def cursor_pos(self, window, xpos, ypos):
        x = xpos/width
        y = ypos/height
        if x > self.button1[0][0] and y > self.button1[0][1] and x < self.button1[2][0] and y < self.button1[2][1]:
            print("self.button 1 pressed")

        if x > self.button2[0][0] and y > self.button2[0][1] and x < self.button2[2][0] and y < self.button2[2][1]:
            print("self.button 2 pressed")


    def cursor_enter(self, window, entered):
        print('cursor_enter:', entered)

    def mouse_button(self, window, button, action, mods):
        pos = glfw.get_cursor_pos(window)
        print('mouse:', self.button, end='')

        if self.button == glfw.MOUSE_self.button_LEFT:
            print('(Left)', end='')
        if self.button == glfw.MOUSE_self.button_RIGHT:
            print('(Right)', end='')
        if self.button == glfw.MOUSE_self.button_MIDDLE:
            print('(Middle)', end='')

        if action == glfw.PRESS:
            print(' press')
        elif action == glfw.RELEASE:
            print(' release')
        else:
            print(' hogehoge')

        x, y = pos
        print(pos, x, y)

    def scroll(self, window, xoffset, yoffset):
        print('scroll:', xoffset, yoffset)

    def window_refresh(self, window):
        self.display()


windo = Window()
windo.run()