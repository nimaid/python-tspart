import numpy as np
from PIL import Image, ImageDraw, ImageChops

from tspart._helpers import get_bounding_corners, image_array_size, line_angle, circle_point


def draw_multi_thickness_line(draw, xy, widths, fill=None):
    if len(xy) != 2:
        raise ValueErrror("xy must be of length 2")
    if len(widths) != 2:
        raise ValueErrror("widths must be of length 2")

    angle = line_angle(xy[0], xy[1])

    point_transforms = []
    for point, width in zip(xy, widths):
        radius = width / 2
        point_transforms.append(circle_point(radius, angle + (np.pi / 2), point))
        point_transforms.append(circle_point(radius, angle - (np.pi / 2), point))

    polygon_points = point_transforms[:2] + point_transforms[2:][::-1]
    polygon_points = [tuple(_) for _ in polygon_points]

    draw.polygon(
        xy=polygon_points,
        fill=fill,
        outline=None
    )


def draw_route(
        points,
        line_width=2,
        size=None,
        image=None,
        scale=1,
        closed=True,
        background=(255, 255, 255),
        foreground=(0, 0, 0),
        line_width_factor=0.95,
        subpixels=8
):
    if size is None and image is None:
        size = (np.array(get_bounding_corners(points)[1]) + 1)
    elif size is None and image is not None:
        size = np.array(image_array_size(image))
    else:
        size = np.array(size)

    subpixels = max(1, subpixels)

    size_scale = tuple((size * subpixels * scale).round().astype(int))

    size_out = tuple((size * scale).round().astype(int))

    line_width = line_width * subpixels * scale

    img = Image.new(mode="RGB", size=size_scale, color=background)
    draw = ImageDraw.Draw(img)

    last_point = None
    last_width = None

    def draw_line_to_point(p, cap=True):
        nonlocal last_point, last_width

        p = np.array(p)
        y, x = (np.array(p)).round().astype(int)

        p = tuple((p * subpixels * scale))

        if image is not None:
            px = image[x][y]
            factor = (-line_width_factor * (px / 255)) + 1
            width = line_width * factor
        else:
            width = line_width
        r = width / 2

        # Draw dot
        if cap:
            draw.ellipse(
                xy=(
                    (round(p[0] - r), round(p[1] - r)),
                    (round(p[0] + r), round(p[1] + r))
                ),
                fill=foreground,
                outline=None
            )

        # Draw line
        if last_point is not None:
            if image is None:
                draw.line(
                    xy=(last_point, p),
                    fill=foreground,
                    width=width
                )
            else:
                draw_multi_thickness_line(
                    draw=draw,
                    xy=(last_point, p),
                    widths=(last_width, width),
                    fill=foreground
                )

        last_point = p
        last_width = width

    for point in points:
        draw_line_to_point(point)

    if closed:
        draw_line_to_point(points[0], cap=False)

    img = img.resize(size_out, resample=Image.Resampling.LANCZOS)

    return img


def draw_cmyk_routes(
        cmyk_points,
        line_width=2,
        size=None,
        images=None,
        scale=1,
        closed=True,
        line_width_factor=0.95,
        subpixels=8
):
    if size is None and images is None:
        size = (np.array(get_bounding_corners(cmyk_points[0])[1]) + 1)
    elif size is None and images is not None:
        size = np.array(image_array_size(images[0]))
    else:
        size = np.array(size)

    size_out = tuple((size * scale).round().astype(int))

    if images is None:
        images = [None] * len(cmyk_points)

    sub_colors = (
        (255, 0, 0),
        (0, 255, 0),
        (0, 0, 255),
        (255, 255, 255)
    )

    img = Image.new(size=size_out, mode="RGB", color=(255, 255, 255))
    for idx, channel_points in enumerate(cmyk_points):
        channel_img = draw_route(
            points=channel_points,
            size=size,
            image=images[idx],
            scale=scale,
            closed=closed,
            background=(0, 0, 0),
            foreground=sub_colors[idx],
            line_width=line_width,
            line_width_factor=line_width_factor,
            subpixels=subpixels
        ).convert("RGB")

        img = ImageChops.subtract(img, channel_img)

    return img
