import numpy as np
from PIL import Image, ImageDraw, ImageChops

from tspart._helpers import get_bounding_corners


def draw_points(
        points,
        size=None,
        background=(255, 255, 255),
        foreground=(0, 0, 0),
        radius=2,
        subpixels=8
):
    if size is None:
        size = (np.array(get_bounding_corners(points)[1]) + 1)
    else:
        size = np.array(size[::-1])

    size_scale = tuple((size * subpixels).round().astype(int))
    size = tuple(size.round().astype(int))

    subpixels = max(1, subpixels)

    radius = int(round(radius * subpixels))

    img = Image.new(mode="RGB", size=size_scale, color=background)
    draw = ImageDraw.Draw(img)

    for point in points:
        point = np.array(point)

        point = tuple((point * subpixels).round().astype(int))

        draw.ellipse(
            xy=(
                (round(point[0] - radius), round(point[1] - radius)),
                (round(point[0] + radius), round(point[1] + radius))
            ),
            fill=foreground,
            outline=None
        )

    img = img.resize(size)

    return img


def draw_cmyk_points(
        cmyk_points,
        size=None,
        radius=2,
        subpixels=8
):
    if size is None:
        size = tuple(np.array(get_bounding_corners(cmyk_points[0])[1]) + 1)
    else:
        size = tuple(size)

    sub_colors = (
        (255, 0, 0),
        (0, 255, 0),
        (0, 0, 255),
        (255, 255, 255)
    )

    img = Image.new(size=size[::-1], mode="RGB", color=(255, 255, 255))
    for idx, channel_points in enumerate(cmyk_points):
        channel_img = draw_points(
            points=channel_points,
            size=size,
            background=(0, 0, 0),
            foreground=sub_colors[idx],
            radius=radius,
            subpixels=subpixels
        ).convert("RGB")

        img = ImageChops.subtract(img, channel_img)

    return img


def draw_route(
        points,
        size=None,
        background=(255, 255, 255),
        foreground=(0, 0, 0),
        line_width=2,
        subpixels=8
):
    if size is None:
        size = (np.array(get_bounding_corners(points)[1]) + 1)
    else:
        size = np.array(size[::-1])

    subpixels = max(1, subpixels)

    size_scale = tuple((size * subpixels).round().astype(int))
    size = tuple(size.round().astype(int))

    line_width = int(round(line_width * subpixels))
    dot_radius = int(round(line_width / 2))

    img = Image.new(mode="RGB", size=size_scale, color=background)
    draw = ImageDraw.Draw(img)

    last_point = None
    for point in points:
        point = np.array(point)
        point = tuple((point * subpixels).round().astype(int))

        # Draw dot
        draw.ellipse(
            xy=(
                (round(point[0] - dot_radius), round(point[1] - dot_radius)),
                (round(point[0] + dot_radius), round(point[1] + dot_radius))
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


def draw_cmyk_routes(
        cmyk_points,
        size=None,
        line_width=2,
        subpixels=8
):
    if size is None:
        size = tuple(np.array(get_bounding_corners(cmyk_points[0])[1]) + 1)
    else:
        size = tuple(size)

    sub_colors = (
        (255, 0, 0),
        (0, 255, 0),
        (0, 0, 255),
        (255, 255, 255)
    )

    img = Image.new(size=size[::-1], mode="RGB", color=(255, 255, 255))
    for idx, channel_points in enumerate(cmyk_points):
        channel_img = draw_route(
            points=channel_points,
            size=size,
            background=(0, 0, 0),
            foreground=sub_colors[idx],
            line_width=line_width,
            subpixels=subpixels
        ).convert("RGB")

        img = ImageChops.subtract(img, channel_img)

    return img
