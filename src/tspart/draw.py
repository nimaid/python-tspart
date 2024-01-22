import numpy as np
from PIL import Image, ImageDraw


def map_route_points(points, route):
    return np.array([points[idx] for idx in route])


def draw_points(points, size=None, background=(255, 255, 255), foreground=(0, 0, 0), radius=2):
    if size is None:
        size = tuple(np.ceil(points.max(0)).astype(int) + 1)

    img = Image.new(mode="RGB", size=size, color=background)
    draw = ImageDraw.Draw(img)

    for point in points:
        point = tuple(point.round().astype(int))
        # draw.point(point, fill=foreground)

        draw.ellipse(
            xy=(
                (round(point[0]-radius), round(point[1]-radius)),
                (round(point[0]+radius), round(point[1]+radius))
            ),
            fill=foreground,
            outline=None
        )

    return img


def draw_route(points, route, size=None, background=(255, 255, 255), foreground=(0, 0, 0), line_width=2):
    if size is None:
        size = tuple(np.ceil(points.max(0)).astype(int) + 1)

    img = Image.new(mode="RGB", size=size, color=background)
    draw = ImageDraw.Draw(img)

    route_points = map_route_points(points, route)

    last_point = None
    for point in route_points:
        point = tuple(point.round().astype(int))

        # Draw dot
        '''
        radius = line_width
        draw.ellipse(
            xy=(
                (round(point[0]-radius), round(point[1]-radius)),
                (round(point[0]+radius), round(point[1]+radius))
            ),
            fill=foreground,
            outline=None
        )
        '''

        # Draw line
        if last_point is not None:
            draw.line(
                xy=(last_point, point),
                fill=foreground,
                width=line_width
            )

        last_point = point

    return img