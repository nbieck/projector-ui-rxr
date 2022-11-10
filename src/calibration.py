import numpy as np
import numpy.typing as npt
from typing import List
from math_utils import Frustum

def calibrate(world_points: List[npt.NDArray], texture_points: List[npt.NDArray]) -> Frustum:
    """
        Given 4 points an world space (camera view space) and the corresponsing texture coordinates in 
        the projector's screen space, computes the Frustum of the projector in whatever coordinate system the
        world space points are in. (The solution will only be somewhat approximate, but should be good enough)
        Important, the points should correspond directly, i.e. the first world point is the projection of the first
        texture point, etc.
        Parameters:
         - world_points: A list of 4 ndarrays of length 3, each representing a point in euclidean space
         - texture_points: A list of 4 ndarrays of length 2, each representing a point in the screen space of the projector.
                           All coordinate values here should be in the interval [0,1]
    """
    if len(world_points) != 4:
        raise ValueError("World Points for calibration should be exactly 4.")
    if len(texture_points) != 4:
        raise ValueError("Texture Points for calibration should be exacly 4.")
    for p in world_points:
        if p.size != (3,):
            raise ValueError("World Points should have 3 elements")
    for p in texture_points:
        if p.size != (2,):
            raise ValueError("Texture Points should have 2 elements")
        if np.any(p < 0 or p > 1):
            raise ValueError("All Texture Coordinates should be in the range [0,1]")

    return None
