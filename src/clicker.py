import glfw
from OpenGL.GL import *
from ctypes import Structure, sizeof
import numpy as np
import math
from PIL import Image

class clickFunc:
    def __init__(self, func) -> None:
        self.func = func
        self.flag = [False, False, False]
        self.clicked = False
    
    def clicked(self, click_flag):
        if click_flag[0] or self.flag[0]:
            self.flag[0] = True
            if click_flag[1]:
                self.flag[1] = True
        
        if click_flag[0] == False and self.flag[1] and self.flag[0]:
            self.flag[2] = True

        if self.flag[0] and self.flag[1] and self.flag[2]:
            return True
        else:
            return False