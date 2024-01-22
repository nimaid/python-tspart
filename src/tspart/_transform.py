import sys
import numpy as np
from PIL import Image, ImageChops

from tspart import stipple, solve, draw_route, split_cmyk


def image_to_array(image, mode):
    return np.asarray(image.convert(mode))


def transform(
        grayscale_array,
        stipple_points=5000,
        stipple_iterations=50,
        closed=False,
        solution_limit=None,
        time_limit_minutes=1,
        logging=True,
        verbose=False,
        background=(255, 255, 255),
        foreground=(0, 0, 0),
        line_width=2
):
    if logging:
        print(f"Stippling with {stipple_points} points over {stipple_iterations} iterations...", file=sys.stderr)
    points = stipple(
        grayscale_array,
        points=stipple_points,
        iterations=stipple_iterations
    )

    if logging:
        print(f"Solving with  a time limit of {int(round(time_limit_minutes * 60 * 1000))} ms"
              f"minutes and a solution limit of {solution_limit}...", file=sys.stderr)
    route = solve(
        points=points,
        closed=closed,
        solution_limit=solution_limit,
        time_limit_minutes=time_limit_minutes,
        logging=logging,
        verbose=verbose
    )

    return draw_route(
        points,
        route,
        size=grayscale_array.shape,
        background=background,
        foreground=foreground,
        line_width=line_width
    )


def transform_cmyk(
        rgb_array,
        stipple_points=5000,
        stipple_iterations=50,
        closed=False,
        solution_limit=None,
        time_limit_minutes=1,
        logging=True,
        verbose=False,
        line_width=2
):
    size = rgb_array.shape[:2][::-1]

    cmyk = split_cmyk(rgb_array)

    colors = (
        ("cyan", (255, 0, 0)),
        ("magenta", (0, 255, 0)),
        ("yellow", (0, 0, 255)),
        ("black", (255, 255, 255))
    )

    channel_images = []
    for idx, channel in enumerate(cmyk):
        color_name, color = colors[idx]

        if logging:
            print(f"\n\nProcesssing {color_name} channel ({idx+1}/{len(cmyk)})...\n", file=sys.stderr)

        channel_image = transform(
            grayscale_array=channel,
            stipple_points=stipple_points,
            stipple_iterations=stipple_iterations,
            closed=closed,
            solution_limit=solution_limit,
            time_limit_minutes=time_limit_minutes,
            logging=logging,
            verbose=verbose,
            background=(0, 0, 0),
            foreground=color,
            line_width=line_width
        )

        channel_images.append(channel_image)

    final_image = Image.new(mode="RGB", size=size, color=(255, 255, 255))
    for channel_image in channel_images:
        final_image = ImageChops.subtract(final_image, channel_image)

    return final_image
