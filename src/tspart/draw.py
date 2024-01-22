import numpy as np
from PIL import Image, ImageDraw


def map_route_points(points, route):
    result = np.ndarray
    for idx in route:
        np.append(result, points[idx])

    return result


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
