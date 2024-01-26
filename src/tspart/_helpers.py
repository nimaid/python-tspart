import numpy as np
import scipy.spatial
import scipy.ndimage


def get_bounding_corners(points):
    points = np.array(points)

    start = np.floor(points.min(0)).astype(int)
    end = np.ceil(points.max(0)).astype(int)

    return start, end


def image_to_array(image, mode):
    return np.asarray(image.convert(mode))


def map_points_to_tour(points, tour):
    return np.array([points[idx] for idx in tour])


def map_points_to_tour_multi(points_list, tours_list):
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


def size_factor(grayscale_array, point):
    width, height = image_array_size(grayscale_array)

    y, x = np.array(point).round().astype(int)

    x = min(width - 1, x)
    y = min(height - 1, y)

    px = grayscale_array[x][y]
    return 1 - (px / 255)


def factors_from_image(grayscale_array, points, blur_sigma=1):
    if blur_sigma > 0:
        grayscale_array = scipy.ndimage.gaussian_filter(grayscale_array, sigma=blur_sigma)

    factors = []
    for point in points:
        factor = size_factor(grayscale_array, point)
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


def filter_white_points(grayscale_array, points, threshold=0.001):
    result = []
    for point in points:
        factor = size_factor(grayscale_array, point)

        if factor > threshold:
            result.append(point)

    return result


def filter_white_points_multi(grayscale_arrays, points_list, threshold=0.001):
    results = []
    for grayscale_array, points in zip(grayscale_arrays, points_list):
        points = filter_white_points(
            grayscale_array=grayscale_array,
            points=points,
            threshold=threshold
        )

        results.append(points)

    return results
