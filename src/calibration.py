import numpy as np
import numpy.typing as npt
from typing import List, Optional, Callable
import math_utils as mu
from math import cos,sin

NEWTON_ITERATION_COUNT = 10

def calibrate(world_points: List[npt.NDArray], texture_points: List[npt.NDArray], aspect_ratio: float, fov_format: mu.AngleFormat = mu.AngleFormat.DEG, *,
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
        if p.shape != (3,):
            raise ValueError("World Points should have 3 elements.")
    for p in texture_points:
        if p.shape != (2,):
            raise ValueError("Texture Points should have 2 elements.")
        # if np.any(p < 0 or p > 1):
        #     raise ValueError("All Texture Coordinates should be in the range [0,1].")
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
    J = __define_J(world_points, texture_points, aspect_ratio, hfov_rad)

    # initial estimate
    solution = np.zeros((10,))

    for _ in range(NEWTON_ITERATION_COUNT):
        diff = np.linalg.solve(J(solution[0], solution[1], solution[2], solution[3:6], solution[6:9], solution[9]), 
            -F(solution[0], solution[1], solution[2], solution[3:6], solution[6:9], solution[9]))
        solution += diff

    u = solution[6:9]
    theta = solution[9]

    pos = solution[3:6]
    fwd = -np.array([
         u[0]*u[2]*(1-cos(theta))+u[2]*sin(theta),
         u[1]*u[2]*(1-cos(theta))-u[1]*sin(theta),
         cos(theta)+u[2]**2*(1-cos(theta))
        ])
    up = np.array([
        u[0]*u[1]*(1-cos(theta))-u[2]*sin(theta),
        cos(theta)+u[1]**2*(1-cos(theta)),
        u[2]*u[1]*(1-cos(theta))-u[0]*sin(theta)
        ])

    return mu.Frustum(pos, fwd, up, aspect_ratio, mu.AngleFormat.RAD, hfov=hfov_rad)

__FuncType = Callable[[float,float,float,npt.NDArray,npt.NDArray,float],npt.NDArray]

# The formula for this was derived using matlab. This is a direct translation of the output there
def __define_F(xs: List[npt.NDArray], ts: List[npt.NDArray], ar, hfov) -> __FuncType:

    def F(f1: float, f2: float, f3: float, p: npt.NDArray, u: npt.NDArray, theta: float) -> npt.NDArray:
        #helpers
        cost = cos(theta)
        sint = sin(theta)
        chfov = cos(hfov/2)

        p1 = p[0]
        p2 = p[1]
        p3 = p[2]
        u1 = u[0]
        u2 = u[1]
        u3 = u[2]
        t11 = ts[0][0]
        t12 = ts[0][1]
        t21 = ts[1][0]
        t22 = ts[1][1]
        t31 = ts[2][0]
        t32 = ts[2][1]
        x11 = xs[0][0]
        x12 = xs[0][1]
        x13 = xs[0][2]
        x21 = xs[1][0]
        x22 = xs[1][1]
        x23 = xs[1][2]
        x31 = xs[2][0]
        x32 = xs[2][1]
        x33 = xs[2][2]

        return np.array([
                u1**2 + u2**2 + u3**2 - 1,
                p1 - x11 - f1*(u2*sint - u1*u3*(cost - 1)) + f1*t11*chfov*((1 - cost)*u1**2 + cost) - (f1*t12*chfov*(u3*sint + u1*u2*(cost - 1)))/ar,
                p2 - x12 + f1*(u1*sint + u2*u3*(cost - 1)) + f1*t11*chfov*(u3*sint - u1*u2*(cost - 1)) + (f1*t12*chfov*((1 - cost)*u2**2 + cost))/ar,
                p3 - x13 - f1*((1 - cost)*u3**2 + cost) - f1*t11*chfov*(u2*sint + u1*u3*(cost - 1)) + (f1*t12*chfov*(u1*sint - u2*u3*(cost - 1)))/ar,
                p1 - x21 - f2*(u2*sint - u1*u3*(cost - 1)) + f2*t21*chfov*((1 - cost)*u1**2 + cost) - (f2*t22*chfov*(u3*sint + u1*u2*(cost - 1)))/ar,
                p2 - x22 + f2*(u1*sint + u2*u3*(cost - 1)) + f2*t21*chfov*(u3*sint - u1*u2*(cost - 1)) + (f2*t22*chfov*((1 - cost)*u2**2 + cost))/ar,
                p3 - x23 - f2*((1 - cost)*u3**2 + cost) - f2*t21*chfov*(u2*sint + u1*u3*(cost - 1)) + (f2*t22*chfov*(u1*sint - u2*u3*(cost - 1)))/ar,
                p1 - x31 - f3*(u2*sint - u1*u3*(cost - 1)) + f3*t31*chfov*((1 - cost)*u1**2 + cost) - (f3*t32*chfov*(u3*sint + u1*u2*(cost - 1)))/ar,
                p2 - x32 + f3*(u1*sint + u2*u3*(cost - 1)) + f3*t31*chfov*(u3*sint - u1*u2*(cost - 1)) + (f3*t32*chfov*((1 - cost)*u2**2 + cost))/ar,
                p3 - x33 - f3*((1 - cost)*u3**2 + cost) - f3*t31*chfov*(u2*sint + u1*u3*(cost - 1)) + (f3*t32*chfov*(u1*sint - u2*u3*(cost - 1)))/ar
            ])

    return F

__JacobianType = Callable[[float,float,float,npt.NDArray,npt.NDArray,float],npt.NDArray]

def __define_J(xs: List[npt.NDArray], ts: List[npt.NDArray], ar, hfov) -> __JacobianType:
    def J(f1: float, f2: float, f3: float, p: npt.NDArray, u: npt.NDArray, theta: float) -> npt.NDArray:

        #helpers
        cost = cos(theta)
        sint = sin(theta)
        chfov = cos(hfov/2)

        u1 = u[0]
        u2 = u[1]
        u3 = u[2]
        t11 = ts[0][0]
        t12 = ts[0][1]
        t21 = ts[1][0]
        t22 = ts[1][1]
        t31 = ts[2][0]
        t32 = ts[2][1]

        return np.array([
                [                                                                                                            0,                                                                                                             0,                                                                                                             0, 0, 0, 0,                                                                              2*u1,                                                                              2*u2,                                                                              2*u3,                                                                                                          0],
                [u1*u3*(cost - 1) - u2*sint + t11*chfov*((1 - cost)*u1**2 + cost) - (t12*chfov*(u3*sint + u1*u2*(cost - 1)))/ar,                                                                                                             0,                                                                                                             0, 1, 0, 0, f1*u3*(cost - 1) - 2*f1*t11*u1*chfov*(cost - 1) - (f1*t12*u2*chfov*(cost - 1))/ar,                                       - f1*sint - (f1*t12*u1*chfov*(cost - 1))/ar,                                         f1*u1*(cost - 1) - (f1*t12*chfov*sint)/ar, - f1*(u2*cost + u1*u3*sint) - f1*t11*chfov*(- sint*u1**2 + sint) - (f1*t12*chfov*(u3*cost - u1*u2*sint))/ar],
                [u1*sint + u2*u3*(cost - 1) + t11*chfov*(u3*sint - u1*u2*(cost - 1)) + (t12*chfov*((1 - cost)*u2**2 + cost))/ar,                                                                                                             0,                                                                                                             0, 0, 1, 0,                                              f1*sint - f1*t11*u2*chfov*(cost - 1), f1*u3*(cost - 1) - f1*t11*u1*chfov*(cost - 1) - (2*f1*t12*u2*chfov*(cost - 1))/ar,                                              f1*u2*(cost - 1) + f1*t11*chfov*sint,   f1*(u1*cost - u2*u3*sint) + f1*t11*chfov*(u3*cost + u1*u2*sint) - (f1*t12*chfov*(- sint*u2**2 + sint))/ar],
                [u3**2*(cost - 1) - cost - t11*chfov*(u2*sint + u1*u3*(cost - 1)) + (t12*chfov*(u1*sint - u2*u3*(cost - 1)))/ar,                                                                                                             0,                                                                                                             0, 0, 0, 1,                               (f1*t12*chfov*sint)/ar - f1*t11*u3*chfov*(cost - 1),                             - f1*t11*chfov*sint - (f1*t12*u3*chfov*(cost - 1))/ar, 2*f1*u3*(cost - 1) - f1*t11*u1*chfov*(cost - 1) - (f1*t12*u2*chfov*(cost - 1))/ar,   f1*(- sint*u3**2 + sint) - f1*t11*chfov*(u2*cost - u1*u3*sint) + (f1*t12*chfov*(u1*cost + u2*u3*sint))/ar],
                [                                                                                                            0, u1*u3*(cost - 1) - u2*sint + t21*chfov*((1 - cost)*u1**2 + cost) - (t22*chfov*(u3*sint + u1*u2*(cost - 1)))/ar,                                                                                                             0, 1, 0, 0, f2*u3*(cost - 1) - 2*f2*t21*u1*chfov*(cost - 1) - (f2*t22*u2*chfov*(cost - 1))/ar,                                       - f2*sint - (f2*t22*u1*chfov*(cost - 1))/ar,                                         f2*u1*(cost - 1) - (f2*t22*chfov*sint)/ar, - f2*(u2*cost + u1*u3*sint) - f2*t21*chfov*(- sint*u1**2 + sint) - (f2*t22*chfov*(u3*cost - u1*u2*sint))/ar],
                [                                                                                                            0, u1*sint + u2*u3*(cost - 1) + t21*chfov*(u3*sint - u1*u2*(cost - 1)) + (t22*chfov*((1 - cost)*u2**2 + cost))/ar,                                                                                                             0, 0, 1, 0,                                              f2*sint - f2*t21*u2*chfov*(cost - 1), f2*u3*(cost - 1) - f2*t21*u1*chfov*(cost - 1) - (2*f2*t22*u2*chfov*(cost - 1))/ar,                                              f2*u2*(cost - 1) + f2*t21*chfov*sint,   f2*(u1*cost - u2*u3*sint) + f2*t21*chfov*(u3*cost + u1*u2*sint) - (f2*t22*chfov*(- sint*u2**2 + sint))/ar],
                [                                                                                                            0, u3**2*(cost - 1) - cost - t21*chfov*(u2*sint + u1*u3*(cost - 1)) + (t22*chfov*(u1*sint - u2*u3*(cost - 1)))/ar,                                                                                                             0, 0, 0, 1,                               (f2*t22*chfov*sint)/ar - f2*t21*u3*chfov*(cost - 1),                             - f2*t21*chfov*sint - (f2*t22*u3*chfov*(cost - 1))/ar, 2*f2*u3*(cost - 1) - f2*t21*u1*chfov*(cost - 1) - (f2*t22*u2*chfov*(cost - 1))/ar,   f2*(- sint*u3**2 + sint) - f2*t21*chfov*(u2*cost - u1*u3*sint) + (f2*t22*chfov*(u1*cost + u2*u3*sint))/ar],
                [                                                                                                            0,                                                                                                             0, u1*u3*(cost - 1) - u2*sint + t31*chfov*((1 - cost)*u1**2 + cost) - (t32*chfov*(u3*sint + u1*u2*(cost - 1)))/ar, 1, 0, 0, f3*u3*(cost - 1) - 2*f3*t31*u1*chfov*(cost - 1) - (f3*t32*u2*chfov*(cost - 1))/ar,                                       - f3*sint - (f3*t32*u1*chfov*(cost - 1))/ar,                                         f3*u1*(cost - 1) - (f3*t32*chfov*sint)/ar, - f3*(u2*cost + u1*u3*sint) - f3*t31*chfov*(- sint*u1**2 + sint) - (f3*t32*chfov*(u3*cost - u1*u2*sint))/ar],
                [                                                                                                            0,                                                                                                             0, u1*sint + u2*u3*(cost - 1) + t31*chfov*(u3*sint - u1*u2*(cost - 1)) + (t32*chfov*((1 - cost)*u2**2 + cost))/ar, 0, 1, 0,                                              f3*sint - f3*t31*u2*chfov*(cost - 1), f3*u3*(cost - 1) - f3*t31*u1*chfov*(cost - 1) - (2*f3*t32*u2*chfov*(cost - 1))/ar,                                              f3*u2*(cost - 1) + f3*t31*chfov*sint,   f3*(u1*cost - u2*u3*sint) + f3*t31*chfov*(u3*cost + u1*u2*sint) - (f3*t32*chfov*(- sint*u2**2 + sint))/ar],
                [                                                                                                            0,                                                                                                             0, u3**2*(cost - 1) - cost - t31*chfov*(u2*sint + u1*u3*(cost - 1)) + (t32*chfov*(u1*sint - u2*u3*(cost - 1)))/ar, 0, 0, 1,                               (f3*t32*chfov*sint)/ar - f3*t31*u3*chfov*(cost - 1),                             - f3*t31*chfov*sint - (f3*t32*u3*chfov*(cost - 1))/ar, 2*f3*u3*(cost - 1) - f3*t31*u1*chfov*(cost - 1) - (f3*t32*u2*chfov*(cost - 1))/ar,   f3*(- sint*u3**2 + sint) - f3*t31*chfov*(u2*cost - u1*u3*sint) + (f3*t32*chfov*(u1*cost + u2*u3*sint))/ar]
            ])

    return J
