import numpy as np


def split_cmyk(rgb_array, threshhold=1):
    data = rgb_array.astype(float) / 255
    threshold = threshhold / 255

    channel_max = data.max(2)
    channel_max[channel_max < threshold] = threshold

    k = 1 - channel_max
    c = (1 - data[:, :, 0] - k) / channel_max
    m = (1 - data[:, :, 1] - k) / channel_max
    y = (1 - data[:, :, 2] - k) / channel_max

    result = 1 - np.array([c, m, y, k])

    return tuple([(_ * 255).round().astype(int) for _ in result])


def split_rgb(rgb_array):
    r = rgb_array[:, :, 0]
    g = rgb_array[:, :, 1]
    b = rgb_array[:, :, 2]

    return r, g, b


def rgb_to_gray(rgb):
    r, g, b = rgb

    return int(round((0.299 * r) + (0.587 * g) + (0.114 * b)))


def rgb_array_to_grayscale(rgb_array):
    return np.array([[rgb_to_gray(__) for __ in _] for _ in rgb_array])
