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


def factors_from_image(grayscale_array, points, blur_sigma=5):
    blurred_img = scipy.ndimage.gaussian_filter(grayscale_array, sigma=blur_sigma)

    factors = []
    for point in points:
        x, y = tuple(np.array(point).round().astype(int))

        factors.append(blurred_img[x][y] / 255)

    return np.array(factors)


def factors_from_image_multi(grayscale_arrays, points_list):
    factors_list = []
    for grayscale_array, points in zip(grayscale_arrays, points_list):
        factors = factors_from_image(
            grayscale_array=grayscale_array,
            points=points
        )

        factors_list.append(factors)

    return factors_list
