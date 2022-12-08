import glfw
from OpenGL.GL import *
from ctypes import Structure, sizeof
import numpy as np
import math
from PIL import Image

class clickFunc:
    def __init__(self, func) -> None:
        self.func = func
        self.flag = False
        self.click_cnt = 0
        self.release_cnt = 0

    def clicking(self, click_flag):
        if click_flag:
            self.click_cnt += 1
            self.release_cnt = 0
        elif not click_flag: 
            self.click_cnt = 0
            self.release_cnt += 1

        if self.click_cnt > 3 and self.flag == False:
            self.func()
            self.flag = True
            self.release_cnt = 0
        
        if self.release_cnt > 3:
            self.click_cnt = 0
            self.flag = False

        # if click_flag == 0 or self.flag[0] == True:
        #     self.flag[0] = True
        #     if click_flag == 1:
        #         self.flag[1] = True
        
        # if self.flag[1] == True and click_flag == 1:
        #     self.flag[1] = False
        #     self.flag[0] = False
        #     print('changed--------------------------')
        #     return self.func()
        