import glfw
from OpenGL.GL import *
from ctypes import Structure, sizeof
import numpy as np

width = 640
height = 480

trans_m = np.array([[1, 0, 0, 0],
                    [0, 1, 0, 0],
                    [0, 0, 1, 0],
                    [0, 0, 0, 1]])

button1 = np.array([[0.1, 0.25, 0, 1],
                    [0.40, 0.25, 0, 1],
                    [0.40, 0.75, 0, 1],
                    [0.1, 0.75, 0, 1]])

button2 = np.array([[0.6, 0.25, 0, 1],
                    [0.90, 0.25, 0, 1],
                    [0.90, 0.75, 0, 1],
                    [0.6, 0.75, 0, 1]])

def display(window):
    glClear(GL_COLOR_BUFFER_BIT)

    glColor3f(1.0, 1.0, 1.0)
    glBegin(GL_POLYGON)
    for vt in button1:
        w = np.dot(trans_m, vt.T)
        glVertex2f(w[0]/w[2],w[1]/w[2])

    for vt in button2:
        w = np.dot(trans_m, vt.T)
        glVertex2f(w[0]/w[2],w[1]/w[2])
    glEnd()

    glfw.swap_buffers(window)

def window_refresh(window):
    display(window)

class Window:
    def __init__(self, window_refresh) -> None:
        if not glfw.init():
            raise RuntimeError('Could not initialize GLFW3')


        self.window = glfw.create_window(width, height, 'mouse on GLFW', None, None)
        if not self.window:
            glfw.terminate()
            raise RuntimeError('Could not create an window')
        
        self.init(window_refresh)
      
    def init(self, window_refresh):
        glfw.set_cursor_pos_callback(self.window, self.cursor_pos)
        glfw.set_cursor_enter_callback(self.window, self.cursor_enter)
        glfw.set_mouse_button_callback(self.window, self.mouse_button)
        glfw.set_scroll_callback(self.window, self.scroll)
        glfw.set_window_refresh_callback(self.window, window_refresh)
        glfw.make_context_current(self.window)

        glClearColor(0.0, 1.0, 0.0, 1.0)
        glOrtho(0.0, 1.0, 0.0, 1.0, -1.0, 1.0)
        display(self.window)   # necessary only on Windows
    
    def run(self):

        while not glfw.window_should_close(self.window):
            glfw.wait_events_timeout(1e-3)

        glfw.terminate()

  
    # def draw(self, tool):
    #     glColor3f(1.0, 1.0, 1.0)
    #     glBegin(GL_POLYGON)
    #     for vt in tool:
    #         w = np.dot(self.trans_m, vt.T)
    #         glVertex2f(w[0]/w[2],w[1]/w[2])
    #     glEnd()

    # def display(self):
    #     glClear(GL_COLOR_BUFFER_BIT)

    #     self.draw(button1)
    #     self.draw(button2)

    #     glfw.swap_buffers(self.window)

    def cursor_pos(self, window, xpos, ypos):
        x = xpos/width
        y = ypos/height
        if x > button1[0][0] and y > button1[0][1] and x < button1[2][0] and y < button1[2][1]:
            print("button 1 pressed")

        if x > button2[0][0] and y > button2[0][1] and x < button2[2][0] and y < button2[2][1]:
            print("button 2 pressed")


    def cursor_enter(self, window, entered):
        print('cursor_enter:', entered)

    def mouse_button(self, window, button, action, mods):
        pos = glfw.get_cursor_pos(window)
        print('mouse:', button, end='')

        if button == glfw.MOUSE_button_LEFT:
            print('(Left)', end='')
        if button == glfw.MOUSE_button_RIGHT:
            print('(Right)', end='')
        if button == glfw.MOUSE_button_MIDDLE:
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

    # def window_refresh(self, window):
    #     self.display()


windo = Window(window_refresh)
windo.run()