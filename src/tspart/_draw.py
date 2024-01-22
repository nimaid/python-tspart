from typing import Tuple, Any

import numpy as np
from PIL import Image, ImageDraw

from tspart._helpers import get_bounding_corners


def map_route_points(points, route):
    return np.array([points[idx] for idx in route])


def draw_points(
        points,
        size=None,
        background=(255, 255, 255),
        foreground=(0, 0, 0),
        radius=2,
        subpixels=8
):
    if size is None:
        size = (get_bounding_corners(points)[1] + 1)
    else:
        size = np.array(size[::-1])

    size_scale = tuple((size * subpixels).round().astype(int))
    size = tuple(size.round().astype(int))

    radius = int(round(radius * subpixels))

    img = Image.new(mode="RGB", size=size_scale, color=background)
    draw = ImageDraw.Draw(img)

    for point in points:
        point = tuple((point * subpixels).round().astype(int))

        draw.ellipse(
            xy=(
                (round(point[0]-radius), round(point[1]-radius)),
                (round(point[0]+radius), round(point[1]+radius))
            ),
            fill=foreground,
            outline=None
        )

    img = img.resize(size)

    return img


def draw_route(
        points,
        route,
        size=None,
        background=(255, 255, 255),
        foreground=(0, 0, 0),
        line_width=2,
        draw_dot=False,
        dot_radius=2,
        subpixels=8
):
    if size is None:
        size = (get_bounding_corners(points)[1] + 1)
    else:
        size = np.array(size[::-1])

    subpixels = max(1, subpixels)

    size_scale = tuple((size * subpixels).round().astype(int))
    size = tuple(size.round().astype(int))

    line_width = int(round(line_width * subpixels))
    dot_radius = int(round(dot_radius * subpixels))

    img = Image.new(mode="RGB", size=size_scale, color=background)
    draw = ImageDraw.Draw(img)

    route_points = map_route_points(points, route)

    last_point = None
    for point in route_points:
        point = tuple((point * subpixels).round().astype(int))

        # Draw dot
        if draw_dot:
            draw.ellipse(
                xy=(
                    (round(point[0]-dot_radius), round(point[1]-dot_radius)),
                    (round(point[0]+dot_radius), round(point[1]+dot_radius))
                ),
                fill=foreground,
                outline=None
            )

        # Draw line
        if last_point is not None:
            draw.line(
                xy=(last_point, point),
                fill=foreground,
                width=line_width
            )

        last_point = point

    img = img.resize(size)

    return img
