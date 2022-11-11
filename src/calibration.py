import numpy as np
import numpy.typing as npt
from typing import List, Optional, Callable
import math_utils as mu
from math import cos,sin

def calibrate(world_points: List[npt.NDArray], texture_points: List[npt.NDArray], aspect_ratio: float, fov_format: mu.AngleFormat = mu.AngleFormat.RAD, *,
              hfov: Optional[float] = None, vfov: Optional[float] = None) -> mu.Frustum:
    """
        Given 3 points an world space (camera view space) and the corresponsing texture coordinates in 
        the projector's screen space, computes the Frustum of the projector in whatever coordinate system the
        world space points are in. (The solution will only be somewhat approximate, but should be good enough)
        Important, the points should correspond directly, i.e. the first world point is the projection of the first
        texture point, etc.
        Parameters:
         - world_points: A list of 4 ndarrays of length 3, each representing a point in euclidean space
         - texture_points: A list of 4 ndarrays of length 2, each representing a point in the screen space of the projector.
                           All coordinate values here should be in the interval [0,1]
    """
    if len(world_points) != 3:
        raise ValueError("World Points for calibration should be exactly 3.")
    if len(texture_points) != 3:
        raise ValueError("Texture Points for calibration should be exacly 3.")
    for p in world_points:
        if p.size != (3,):
            raise ValueError("World Points should have 3 elements.")
    for p in texture_points:
        if p.size != (2,):
            raise ValueError("Texture Points should have 2 elements.")
        if np.any(p < 0 or p > 1):
            raise ValueError("All Texture Coordinates should be in the range [0,1].")
    if hfov is not None and vfov is not None:
        raise ValueError("Only one of horizontal and vertical fov should be provided.")
    if hfov is None and vfov is None:
        raise ValueError("Horizontal or vertical fov must be provided.")

    hfov_rad = 0
    if hfov is not None:
        hfov_rad = mu.convert_angles(hfov, fov_format, mu.AngleFormat.RAD)
    else:
        assert vfov is not None
        hfov_rad = mu.vfov_to_hfov(vfov, aspect_ratio, fov_format, mu.AngleFormat.RAD)

    # Solving for the frustum turns out to be a system of nonlinear equations.
    # We use the method mentioned here https://en.wikipedia.org/wiki/Newton%27s_method#Systems_of_equations
    # To get an approximation


    # Our 10D function we want to zero
    F = __define_F(world_points, texture_points, aspect_ratio, hfov_rad)

    raise NotImplementedError("Not fully implemented yet")

__FuncType = Callable[[float,float,float,npt.NDArray,npt.NDArray,float],npt.NDArray]

# The formula for this was derived using matlab. This is a direct translation of the output there
def __define_F(xs: List[npt.NDArray], ts: List[npt.NDArray], ar, hfov) -> __FuncType:

    def F(f1: float, f2: float, f3: float, p: npt.NDArray, u: npt.NDArray, theta: float) -> npt.NDArray:
        #helpers
        sigma1 = cos(theta) - u[2]^2*(cos(theta)-1)
        sigma2 = cos(theta) - u[1]^2*(cos(theta)-1)
        sigma3 = cos(theta) - u[0]^2*(cos(theta)-1)
        sigma10 = (cos(theta) - 1)
        sigma11 = (cos(theta) - 1)
        sigma12 = (cos(theta) - 1)
        sigma4 = u[2]*sin(theta) - sigma10
        sigma5 = u[1]*sin(theta) - sigma11
        sigma6 = u[0]*sin(theta) - sigma12
        sigma7 = u[2]*sin(theta) + sigma10
        sigma8 = u[1]*sin(theta) + sigma11
        sigma9 = u[0]*sin(theta) + sigma12

        chfov = cos(hfov/2)

        return np.array([
            u[0]^2+u[1]^2+u[2]^2-1,
            p[0] - xs[0][0] + f1 * sigma5 + f1 * ts[0][0] * chfov * sigma3 - f1 * ts[0][1] * chfov * sigma7 / ar,
            p[1] - xs[0][1] + f1 * sigma9 + f1 * ts[0][0] * chfov * sigma4 - f1 * ts[0][1] * chfov * sigma2 / ar,
            p[2] - xs[0][2] + f1 * sigma1 + f1 * ts[0][0] * chfov * sigma8 - f1 * ts[0][1] * chfov * sigma6 / ar,
            p[0] - xs[1][0] + f2 * sigma5 + f2 * ts[1][0] * chfov * sigma3 - f2 * ts[1][1] * chfov * sigma7 / ar,
            p[1] - xs[1][1] + f2 * sigma9 + f2 * ts[1][0] * chfov * sigma4 - f2 * ts[1][1] * chfov * sigma2 / ar,
            p[2] - xs[1][2] + f2 * sigma1 + f2 * ts[1][0] * chfov * sigma8 - f2 * ts[1][1] * chfov * sigma6 / ar,
            p[0] - xs[2][0] + f3 * sigma5 + f3 * ts[2][0] * chfov * sigma3 - f3 * ts[2][1] * chfov * sigma7 / ar,
            p[1] - xs[2][1] + f3 * sigma9 + f3 * ts[2][0] * chfov * sigma4 - f3 * ts[2][1] * chfov * sigma2 / ar,
            p[2] - xs[2][2] + f3 * sigma1 + f3 * ts[2][0] * chfov * sigma8 - f3 * ts[2][1] * chfov * sigma6 / ar,
            ])

    return F

