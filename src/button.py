import glfw
from OpenGL.GL import *
from ctypes import Structure, sizeof
import numpy as np
import math
from PIL import Image

class Button:
    def __init__(self, position) -> None:
        self.pos = position
    
    def getMat(self):
        return self.pos

    def setMat(self, mat):
        self.pos = mat
    
    def clicked(self, cursor):
        return self.pos[0][0] < cursor[0] & self.pos[0][1] < cursor[1] & self.pos[2][0] > cursor[0] & self.pos[2][1] > cursor[1]