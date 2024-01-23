import sys

from tspart._stippler import stipple
from tspart._tsp import solve_ortools
from tspart._helpers import map_points_to_route
from tspart._image import split_cmyk


def transform(
        grayscale_array,
        stipple_points=5000,
        stipple_iterations=50,
        closed=False,
        time_limit_minutes=1,
        logging=True,
        verbose=False,
        routing=True
):
    if logging:
        print(f"Stippling with {stipple_points} points over {stipple_iterations} iterations...", file=sys.stderr)
    points = stipple(
        grayscale_array,
        points=stipple_points,
        iterations=stipple_iterations
    )

    if routing:
        if logging:
            print(f"Solving with a time limit of {int(round(time_limit_minutes * 60 * 1000))} ms...", file=sys.stderr)
        route = solve_ortools(
            points=points,
            closed=closed,
            time_limit_minutes=time_limit_minutes,
            logging=logging,
            verbose=verbose
        )

        return map_points_to_route(points, route)
    else:
        return points


def transform_cmyk(
        rgb_array,
        stipple_points=5000,
        stipple_iterations=50,
        closed=False,
        time_limit_minutes=1,
        logging=True,
        verbose=False,
        routing=True
):
    cmyk = split_cmyk(rgb_array)

    colors = ("cyan", "magenta", "yellow", "black")

    cmyk_routes = []
    for idx, channel in enumerate(cmyk):
        if logging:
            print(f"\n\nProcesssing {colors[idx]} channel ({idx+1}/{len(cmyk)})...\n", file=sys.stderr)

        channel_image = transform(
            grayscale_array=channel,
            stipple_points=stipple_points,
            stipple_iterations=stipple_iterations,
            closed=closed,
            time_limit_minutes=time_limit_minutes,
            logging=logging,
            verbose=verbose,
            routing=routing
        )

        cmyk_routes.append(channel_image)

    return cmyk_routes
