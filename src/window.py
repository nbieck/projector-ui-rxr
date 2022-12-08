import glfw
from OpenGL.GL import *
from ctypes import Structure, sizeof
import numpy as np
import math
from PIL import Image

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
        self.image = Image.open('other/Data/IMLEX.png').convert('RGBA')
        self.image_data = np.array(list(self.image.getdata()))
        self.image_data = self.image_data[:,[2,1,0,3]]        
        print('shape', self.image_data.shape)
        self.count = True

        if not glfw.init():
            raise RuntimeError('Could not initialize GLFW3')

        # self.window_w = glfw.get_video_mode(glfw.get_primary_monitor()).size[0]
        # self.window_h = glfw.get_video_mode(glfw.get_primary_monitor()).size[1]
        self.window_w = 1280
        self.window_h = 640

        monitor = glfw.get_monitors()
        monitor_visual = glfw.get_video_mode(monitor[1])
        self.window = glfw.create_window(monitor_visual[0][0], monitor_visual[0][1], 'mouse on GLFW', monitor[1], None)
        # print(glfw.get_video_mode(glfw.get_primary_monitor()).size[0])
        # print(monitor)
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
        self.initializeWindow()
        # self.set_up_texture_maps()
        self.display(self.trans_m)   # necessary only on Windows\

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
    
    def changePic(self):
        if self.count:
            self.image = Image.open('other/Data/UEF.jpg').convert('RGBA')
            self.count = False
        elif not self.count:
            self.image = Image.open('other/Data/IMLEX.png').convert('RGBA')
            self.count = True
        
        self.image_data = np.array(list(self.image.getdata()))
        self.image_data = self.image_data[:,[2,1,0,3]]     



    def clear(self):
        glfw.terminate()

  
    def run(self, trans_m):
        # print("run",trans_m)
        glfw.wait_events_timeout(1e-3)
        self.initializeWindow()
        self.display(trans_m)
        glfw.poll_events()


    def initializeWindow(self):
        width , height = self.image.size
        # print(image.size)

        # set the viewport and projection
        glViewport(0,0,self.window_w,self.window_h)
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()

        #gluPerspective(60.0, float(w)/h, .1, 1000.) #conway
        glOrtho(0,1,0,1,0,1) #tex


        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()

        glClear( GL_COLOR_BUFFER_BIT ) #tex

        # enable textures, bind to our texture
        glEnable(GL_TEXTURE_2D)	#tex
        textureId = (GLuint * 1)()
        glGenTextures(1, textureId)
        glBindTexture(GL_TEXTURE_2D, textureId[0])

        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_CLAMP_TO_EDGE)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_CLAMP_TO_EDGE)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_NEAREST)
        #None means reserve texture memory, but texels are undefined
        glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, width, height, 0, GL_BGRA, GL_UNSIGNED_BYTE, self.image_data)
        glBindTexture(GL_TEXTURE_2D, 0)


    def display(self,trans_m):
        glClear(GL_COLOR_BUFFER_BIT)
        self.draw(self.features, trans_m)
        glfw.swap_buffers(self.window)


    def draw(self, tool, trans_m):
        glColor3f(1.0, 1.0, 1.0)

        glBegin(GL_POLYGON)

        
        # texcoord = [[0,0],[1,0],[1,1],[0,1]]
        texcoord = [ [1,1], [1,0], [0,0], [0,1]]
        p = trans_m @ tool.T
        self.P = p.T
        # print('projection coord')
        # print(p.T)
        for idx, vt in enumerate(p.T):
            glVertex4f(vt[0],vt[1], vt[2], vt[3])
            glTexCoord2f(texcoord[idx][0],texcoord[idx][1])

        glEnd()
    
    def set_up_texture_maps(self):
        image = Image.open('other/Data/images.jpeg').convert('RGBA')
        image_data = np.array(list(image.getdata()))
        width , height = image.size
        print(image.size)

        # set the viewport and projection
        glViewport(0,0,self.window_w,self.window_h)
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()

        #gluPerspective(60.0, float(w)/h, .1, 1000.) #conway
        glOrtho(0,1,0,1,0,1) #tex


        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()

        #glClear( GL_COLOR_BUFFER_BIT ) #tex

        # enable textures, bind to our texture
        glEnable(GL_TEXTURE_2D)	#tex
        textureId = (GLuint * 1)()
        glGenTextures(1, textureId)
        glBindTexture(GL_TEXTURE_2D, textureId[0])

        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_CLAMP_TO_EDGE)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_CLAMP_TO_EDGE)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_NEAREST)
        #None means reserve texture memory, but texels are undefined
        glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, width, height, 0, GL_BGRA, GL_UNSIGNED_BYTE, image_data)
        glBindTexture(GL_TEXTURE_2D, 0)
        self.draw_tex_maps()

        return textureId[0] 

        
    def draw_tex_maps(self):

        glfw.wait_events_timeout(1e-3)

        # glClear(GL_COLOR_BUFFER_BIT)

        glBegin( GL_POLYGON )
        glTexCoord2f( 0, 0 );    glVertex3f( 0, 1, 0 )
        glTexCoord2f( 1, 0 );    glVertex3f( 1, 1, 0 )
        glTexCoord2f( 1, 1 );    glVertex3f( 1, 0, 0 )
        glTexCoord2f( 0, 1 );    glVertex3f( 0, 0, 0 )
        glEnd(  )

        glfw.swap_buffers(self.window)
        glfw.poll_events()

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
