import numpy as np


def get_bounding_corners(points):
    points = np.array(points)

    start = np.floor(points.min(0)).astype(int)
    end = np.ceil(points.max(0)).astype(int)

    return start, end


def image_to_array(image, mode):
    return np.asarray(image.convert(mode))


def map_points_to_route(points, route):
    return np.array([points[idx] for idx in route])


def ndarray_to_array_2d(array):
    return [list([list(__) for __ in _]) for _ in array]
