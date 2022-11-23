import numpy as np
import numpy.typing as npt
import enum
import math
import sys
from typing import Optional

def compute_matrix(bl: npt.NDArray, br: npt.NDArray, tr: npt.NDArray, tl: npt.NDArray) -> np.ndarray:
    """Computes a projection matrix to project from the unit square (0-1) to the given corners"""

    # We set this up as a system of linear equations that we then solve for the factors of the 
    # projection matrix.

    # Projection is defined as taking an expanded point [x, y, 1], multiplying by M
    # to get [x', y', w] and then divide by w to get a projected point [x'/w, y'/w]
    for c in [bl, br, tr, tl]:
        if c.shape != (2,):
            raise ValueError("Passed Corners should be 2-dimensional points.")

    A = np.array([[0, 0, 1, 0, 0, 0, 0,      0],
                  [0, 0, 0, 0, 0, 1, 0,      0],
                  [1, 0, 1, 0, 0, 0, -br[0], 0],
                  [0, 0, 0, 1, 0, 1, -br[1], 0],
                  [1, 1, 1, 0, 0, 0, -tr[0], -tr[0]],
                  [0, 0, 0, 1, 1, 1, -tr[1], -tr[1]],
                  [0, 1, 1, 0, 0, 0, 0,      -tl[0]],
                  [0, 0, 0, 0, 1, 1, 0,      -tl[1]]])
    b = np.array([bl[0], bl[1], br[0], br[1], tr[0], tr[1], tl[0], tl[1]])

    mat_factors = np.linalg.solve(A, b)
    mat_factors = np.append(mat_factors, [1])

    matrix = mat_factors.reshape((3, 3))

    return matrix

def compute_inverse_matrix(bl: npt.NDArray, br: npt.NDArray, tr: npt.NDArray, tl: npt.NDArray) -> np.ndarray:
    """ Computes the matrix to go from the rectangle given by the four corners provided to the unit square.
        Should make checking which button was clicked easier."""
    for c in [bl, br, tr, tl]:
        if c.shape != (2,):
            raise ValueError("Passed Corners should be 2-dimensional points.")

    A = np.array([
        [bl[0], bl[1], 1,     0,     0, 0,      0,      0],
        [    0,     0, 0, bl[0], bl[1], 1,      0,      0],
        [br[0], br[1], 1,     0,     0, 0, -br[0], -br[1]],
        [    0,     0, 0, br[0], br[1], 1,      0,      0],
        [tr[0], tr[1], 1,     0,     0, 0, -tr[0], -tr[1]],
        [    0,     0, 0, tr[0], tr[1], 1, -tr[0], -tr[1]],
        [tl[0], tl[1], 1,     0,     0, 0,      0,      0],
        [    0,     0, 0, tl[0], tl[1], 1, -tl[0], -tl[1]]
        ])
    b = np.array([0, 0, 1, 0, 1, 1, 0, 1])

    mat_factors = np.linalg.solve(A, b)
    mat_factors = np.append(mat_factors, [1])

    matrix = mat_factors.reshape((3, 3))

    return matrix

def threeD_to_fourD(mat: npt.NDArray) -> np.ndarray:
    """Reshape a 3D matrix to a 4D one by inserting a row and column of zeroes.

    i.e.:    [a, b, c]        [a, b, 0, c]
             [d, e, f]   ->   [d, e, 0, f]
             [g, h, i]        [0, 0, 0, 0]
                              [g, h, 0, i]"""

    return np.insert(np.insert(mat, 2, 0, axis=0), 2, 0, axis=1)

class AngleFormat(enum.Enum):
    DEG = enum.auto()
    RAD = enum.auto()

def convert_angles(angle: float, input_format: AngleFormat, output_format: AngleFormat) -> float:
    if input_format == output_format:
        return angle
    if input_format == AngleFormat.DEG:
        return math.radians(angle)
    return math.degrees(angle)

def normalize_vector(vec: npt.NDArray) -> np.ndarray:
    if len(vec.shape) != 1:
        raise ValueError("The Vector to be normalized must be a 1D array.")

    len_sq = np.dot(vec, vec)
    return vec / math.sqrt(len_sq)

def vfov_to_hfov(vfov: float, aspect_ratio: float, in_format: AngleFormat, out_format: AngleFormat) -> float:
    vfov_rad = convert_angles(vfov, in_format, AngleFormat.RAD)
    half_height = math.sin(vfov_rad / 2)
    half_width = aspect_ratio * half_height
    hfov_rad = math.asin(half_width) * 2
    return convert_angles(hfov_rad, AngleFormat.RAD, out_format)


class Frustum:
    """Represents a frustum in space, with an origin, orientation, field of view and aspect ratio.
       Allows for easy conversion from points in world space (i.e. the coordinate system in which the 
       origin and orientation are defined) to view space (origin at 0, view along -z) to screen space
       (u,v, are bounded in [0,1] + depth, if the point is located within the frustum)"""

    def __init__(self, position: npt.NDArray, forward: npt.NDArray, up: npt.NDArray, aspect_ratio: float,
                fov_format : AngleFormat = AngleFormat.DEG, *, hfov : Optional[float] = None, vfov : Optional[float] = None) -> None:
        """
        Parameters:
          - position: Position of the frustum tip (i.e. position of camera or projector)
          - forward, up: Give the orientation of the frustum, the coordinate system is assumed to be right handed, i.e fwd x up = right
                         These vectors must be orthogonal
          - aspect_ratio: aspect ratio calculated as width/height
          - format: whether the angles are provided in degrees or radians. defaults to radians
          - hfov, vfov: horizontal or vertical fov. One of the two must be provided
          """

        if hfov is None and vfov is None:
            raise ValueError("Field of View (either horizontal or vertical) must be provided.")
        if hfov is not None and vfov is not None:
            raise ValueError("Only one Field of Vue must be provided.")
        self.__verify_3d_or_die(position)
        self.__verify_3d_or_die(forward)
        self.__verify_3d_or_die(up)
        if np.dot(forward,up) > sys.float_info.epsilon:
            raise ValueError("Forward and Up must be orthogonal.")

        self.__pos = position
        self.__fwd = normalize_vector(forward)
        self.__up = normalize_vector(up)
        self.__right = np.cross(self.__fwd, self.__up)
        self.__ar = aspect_ratio
        if hfov is not None:
            self.__hfov = convert_angles(hfov, fov_format, AngleFormat.RAD)
        else:
            assert vfov is not None
            self.__hfov = vfov_to_hfov(vfov, aspect_ratio, fov_format, AngleFormat.RAD)

        self.__rot_mat = np.array([self.__right, self.__up, -self.__fwd]).transpose()
        self.__inv_rot_mat = np.linalg.inv(self.__rot_mat)

    def get_position(self) -> np.ndarray:
        return self.__pos

    def get_forward(self) -> np.ndarray:
        return self.__fwd

    def get_up(self) -> np.ndarray:
        return self.__up

    def get_right(self) -> np.ndarray:
        return self.__right

    def get_aspect_ratio(self) -> float:
        return self.__ar

    def get_horizontal_fov(self) -> float:
        return self.__hfov

    def world_to_view(self, vec: npt.NDArray) -> np.ndarray:
        """ Transform a point from world space to the frustum's view space """
        self.__verify_3d_or_die(vec)

        return np.matmul(self.__rot_mat,(vec - self.__pos))

    def view_to_world(self, vec: npt.NDArray) -> np.ndarray:
        """ Transform from view space back to world space """
        self.__verify_3d_or_die(vec)

        return np.matmul(self.__inv_rot_mat, vec) + self.__pos

    def screen_to_view(self, vec: npt.NDArray) -> np.ndarray:
        """ Transform a point in screen coordinates (u,v,depth) to view space """
        self.__verify_3d_or_die(vec)

        depth = vec[2]

        # bring uv into range [-1,1] for easier handling
        uv = np.resize(vec, 2)
        # uv = vec.resize(2)
        uv *= np.full_like(uv, 2)
        uv -= np.full_like(uv, 1)

        half_width = math.sin(self.__hfov / 2)
        half_height = half_width / self.__ar

        return np.array([half_width * uv[0], half_height * uv[1], 1]) * depth

    def screen_to_world(self, vec: npt.NDArray) -> np.ndarray:
        """ Convenience function to convert directly from screen space to world space """

        return self.view_to_world(self.screen_to_view(vec))

    def view_to_screen(self, vec: npt.NDArray) -> np.ndarray:
        """ Convert from view space to screen space """
        depth = vec[2]
        xy = np.resize(vec, 2)
        # xy = vec.resize(2)
        xy /= depth

        half_width = math.sin(self.__hfov / 2)
        half_height = half_width / self.__ar

        uv = xy / np.array([half_width, half_height])
        uv += np.full_like(uv, 1)
        uv /= np.full_like(uv, 2)

        return np.array([uv[0], uv[1], depth])

    def world_to_screen(self, vec: npt.NDArray) -> np.ndarray:
        """ Convenience function to go directly from world to screen space """
        return self.view_to_screen(self.world_to_view(vec))
        
    def __verify_3d_or_die(self, vec: npt.NDArray) -> None:
        if vec.shape != (3,):
            raise ValueError("Vector should be a 1D array with 3 values.")

