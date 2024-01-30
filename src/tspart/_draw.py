import numpy as np
from PIL import Image, ImageDraw, ImageChops

from tspart._helpers import line_angle, circle_point


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
        factors,
        size,
        line_width=2,
        minimum_line_width_factor=(1/255),
        scale=1,
        closed=True,
        background=(255, 255, 255),
        foreground=(0, 0, 0),
        subpixels=8
):
    size = np.array(size)

    subpixels = max(1, subpixels)

    size_scale = tuple((size * subpixels * scale).round().astype(int))

    size_out = tuple((size * scale).round().astype(int))

    line_width = line_width * subpixels * scale

    img = Image.new(mode="RGB", size=size_scale, color=background)
    draw = ImageDraw.Draw(img)

    last_point = None
    last_width = None

    def draw_line_to_point(p, f, cap=True):
        nonlocal last_point, last_width

        p = tuple((p * subpixels * scale))

        f_p = ((1 - minimum_line_width_factor) * f) + minimum_line_width_factor
        w = f_p * line_width

        r = w / 2

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
            draw_multi_thickness_line(
                draw=draw,
                xy=(last_point, p),
                widths=(last_width, w),
                fill=foreground
            )

        last_point = p
        last_width = w

    for point, factor in zip(points, factors):
        draw_line_to_point(point, factor)

    if closed:
        draw_line_to_point(points[0], factors[0], cap=False)

    img = img.resize(size_out, resample=Image.Resampling.LANCZOS)

    return img


def draw_cmyk_routes(
        cmyk_points,
        cmyk_factors,
        size=None,
        line_width=2,
        minimum_line_width_factor=(1/255),
        scale=1,
        closed=True,
        subpixels=8
):
    size = np.array(size)

    size_out = tuple((size * scale).round().astype(int))

    sub_colors = (
        (255, 0, 0),
        (0, 255, 0),
        (0, 0, 255),
        (255, 255, 255)
    )

    img = Image.new(size=size_out, mode="RGB", color=(255, 255, 255))
    for points, factor, color in zip(cmyk_points, cmyk_factors, sub_colors):
        channel_img = draw_route(
            points=points,
            factors=factor,
            size=size,
            line_width=line_width,
            minimum_line_width_factor=minimum_line_width_factor,
            scale=scale,
            closed=closed,
            background=(0, 0, 0),
            foreground=color,
            subpixels=subpixels
        ).convert("RGB")

        img = ImageChops.subtract(img, channel_img)

    return img


def draw_rgb_routes(
        rgb_points,
        rgb_factors,
        size=None,
        line_width=2,
        minimum_line_width_factor=(1/255),
        scale=1,
        closed=True,
        subpixels=8
):
    size = np.array(size)

    size_out = tuple((size * scale).round().astype(int))

    add_colors = (
        (255, 0, 0),
        (0, 255, 0),
        (0, 0, 255),
    )

    img = Image.new(size=size_out, mode="RGB", color=(0, 0, 0))
    for points, factor, color in zip(rgb_points, rgb_factors, add_colors):
        channel_img = draw_route(
            points=points,
            factors=factor,
            size=size,
            line_width=line_width,
            minimum_line_width_factor=minimum_line_width_factor,
            scale=scale,
            closed=closed,
            background=(0, 0, 0),
            foreground=color,
            subpixels=subpixels
        ).convert("RGB")

        img = ImageChops.add(img, channel_img)

    return img
