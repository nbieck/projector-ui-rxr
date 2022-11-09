import numpy as np
import numpy.typing as npt

def compute_matrix(bl: npt.NDArray, br: npt.NDArray, tr: npt.NDArray, tl: npt.NDArray) -> np.ndarray:
    """Computes a projection matrix to project from the unit square (0-1) to the given corners"""

    # We set this up as a system of linear equations that we then solve for the factors of the 
    # projection matrix.

    # Projection is defined as taking an expanded point [x, y, 1], multiplying by M
    # to get [x', y', w] and then divide by w to get a projected point [x'/w, y'/w]

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
