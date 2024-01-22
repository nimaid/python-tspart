import numpy as np


def get_bounding_corners(points):
    start = np.floor(points.min(0)).astype(int)
    end = np.ceil(points.max(0)).astype(int)

    return start, end
