from typing import Tuple, Sequence

import numpy as np
from PIL import Image
import scipy.spatial
import scipy.ndimage


def get_bounding_corners(
        points: Sequence[Sequence[float]]
) -> Tuple[float]:
    points = np.array(points)

    start = np.floor(points.min(0)).astype(int)
    end = np.ceil(points.max(0)).astype(int)

    return start, end


def image_to_array(
        image: Image,
        mode: str = "RGB"
) -> np.ndarray[np.ndarray[float | np.ndarray[float]]]:
    return np.array(image.convert(mode))


def array_to_image(
        array: np.ndarray[np.ndarray[float | np.ndarray[float]]],
        mode: str = "RGB"
) -> Image:
    return Image.fromarray(array, mode)


def map_points_to_tour(
        points: Sequence[Sequence[float]],
        tour: Sequence[int]
) -> np.ndarray[np.ndarray[float]]:
    return np.array([points[idx] for idx in tour])


def map_points_to_tour_multi(
        points_list: Sequence[Sequence[Sequence[float]]],
        tours_list: Sequence[Sequence[int]]
) -> list[np.ndarray[np.ndarray[float]]]:
    result = []
    for idx, points in enumerate(points_list):
        routes = tours_list[idx]

        r = map_points_to_tour(
            points,
            routes
        )

        result.append(r)

    return result


def ndarray_to_array_2d(array):
    return [list([list(__) for __ in _]) for _ in array]


def array_to_ndarray_2d(array):
    return [np.array(_) for _ in array]


def nearest_point_index(points, location):
    distance, index = scipy.spatial.KDTree(points).query(location)

    return int(index)


def image_array_size(img):
    return tuple([int(round(_)) for _ in img.shape[:2]][::-1])


def line_angle(start, end):
    d = np.array(end) - np.array(start)

    return np.arctan2(d[1], d[0])


def circle_point(radius, angle, offset=(0, 0)):
    offset = np.array(offset)

    x = radius * np.cos(angle)
    y = radius * np.sin(angle)

    point = np.array([x, y])

    return point + offset


def get_point_value(grayscale_array, point):
    y, x = np.floor(np.array(point)).astype(int)

    return grayscale_array[x][y]


def size_factor(grayscale_array, point):
    value = get_point_value(
        grayscale_array=grayscale_array,
        point=point
    )
    return 1 - (value / 255)


def factors_from_image(grayscale_array, points, blur_sigma=1):
    if blur_sigma > 0:
        grayscale_array = scipy.ndimage.gaussian_filter(grayscale_array, sigma=blur_sigma)

    factors = []
    for point in points:
        factor = size_factor(
            grayscale_array=grayscale_array,
            point=point
        )
        factors.append(factor)

    return np.array(factors)


def factors_from_image_multi(grayscale_arrays, points_list, blur_sigma=1):
    factors_list = []
    for grayscale_array, points in zip(grayscale_arrays, points_list):
        factors = factors_from_image(
            grayscale_array=grayscale_array,
            points=points,
            blur_sigma=blur_sigma
        )

        factors_list.append(factors)

    return factors_list


def filter_white_points(grayscale_array, points, threshold=254, blur_sigma=1):
    if blur_sigma > 0:
        grayscale_array = scipy.ndimage.gaussian_filter(grayscale_array, sigma=blur_sigma)

    result = []
    for point in points:
        value = get_point_value(
            grayscale_array=grayscale_array,
            point=point
        )
        if value <= threshold:
            result.append(point)
    return result


def filter_white_points_multi(grayscale_arrays, points_list, threshold=1, blur_sigma=1):
    results = []
    for grayscale_array, points in zip(grayscale_arrays, points_list):
        points = filter_white_points(
            grayscale_array=grayscale_array,
            points=points,
            threshold=threshold,
            blur_sigma=blur_sigma
        )

        results.append(points)

    return results
