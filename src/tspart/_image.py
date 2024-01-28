import base64
from io import BytesIO

import numpy as np
from PIL import Image


def split_cmyk(rgb_array, invert=False, threshhold=1):
    data = rgb_array.astype(float) / 255
    threshold = threshhold / 255

    channel_max = data.max(2)
    channel_max[channel_max < threshold] = threshold

    k = 1 - channel_max
    c = (1 - data[:, :, 0] - k) / channel_max
    m = (1 - data[:, :, 1] - k) / channel_max
    y = (1 - data[:, :, 2] - k) / channel_max

    result = 1 - np.array([c, m, y, k])

    result = tuple([(_ * 255).round().astype(int) for _ in result])
    if invert:
        result = invert_array_multi(result)

    return result


def split_rgb(rgb_array, invert=False):
    r = rgb_array[:, :, 0]
    g = rgb_array[:, :, 1]
    b = rgb_array[:, :, 2]

    result = (r, g, b)
    if invert:
        result = invert_array_multi(result)

    return result


def luminance(rgb):
    r, g, b = rgb

    return int(round((0.299 * r) + (0.587 * g) + (0.114 * b)))


def rgb_to_grayscale(rgb_array, invert=False):
    result = np.array([[luminance(__) for __ in _] for _ in rgb_array])
    if invert:
        result = invert_array_multi(result)

    return result


def invert_array(grayscale_array):
    return 255 - grayscale_array


def invert_array_multi(grayscale_arrays):
    return [invert_array(_) for _ in grayscale_arrays]


def image_to_base64(image, format="JPEG"):
    buffered = BytesIO()
    image.save(buffered, format=format)

    return base64.b64encode(buffered.getvalue()).decode("utf-8")


def base64_to_image(base64_string):
    image_bytes = BytesIO(base64.b64decode(base64_string))

    return Image.open(image_bytes)
