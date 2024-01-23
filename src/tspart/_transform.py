import sys

from tspart._stippler import stipple
from tspart._tsp import heuristic_solve
from tspart._helpers import map_points_to_route
from tspart._image import split_cmyk


def transform(
        grayscale_array=None,
        points=None,
        stipple_points=5000,
        stipple_iterations=50,
        closed=False,
        time_limit_minutes=1,
        logging=True,
        verbose=False,
        routing=True
):
    if grayscale_array is not None:
        if logging:
            print(f"Stippling with {stipple_points} points over {stipple_iterations} iterations...", file=sys.stderr)
        points = stipple(
            grayscale_array,
            points=stipple_points,
            iterations=stipple_iterations
        )
    elif grayscale_array is not None and points is not None:
        raise ValueError("Must provide only 1 of grayscale_array or points")
    if points is None:
        raise ValueError("Must provide either grayscale_array or points")

    if routing:
        if logging:
            print(f"Solving with a time limit of {int(round(time_limit_minutes * 60 * 1000))} ms...", file=sys.stderr)
        route = heuristic_solve(
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
        rgb_array=None,
        cmyk_points=None,
        stipple_points=5000,
        stipple_iterations=50,
        closed=False,
        time_limit_minutes=1,
        logging=True,
        verbose=False,
        routing=True
):
    colors = ("cyan", "magenta", "yellow", "black")

    if rgb_array is not None:
        cmyk = split_cmyk(rgb_array)

        cmyk_routes = []
        for idx, channel in enumerate(cmyk):
            if logging:
                print(f"\n\nProcesssing {colors[idx]} channel ({idx + 1}/{len(cmyk)})...\n", file=sys.stderr)

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
    elif cmyk_points is not None:
        cmyk_routes = []
        for idx, channel in enumerate(cmyk_points):
            if logging:
                print(f"\n\nProcesssing {colors[idx]} channel ({idx + 1}/{len(cmyk_points)})...\n", file=sys.stderr)

            channel_image = transform(
                points=channel,
                stipple_points=stipple_points,
                stipple_iterations=stipple_iterations,
                closed=closed,
                time_limit_minutes=time_limit_minutes,
                logging=logging,
                verbose=verbose,
                routing=routing
            )

            cmyk_routes.append(channel_image)
    elif rgb_array is not None and cmyk_points is not None:
        raise ValueError("Must provide only 1 of rgb_array or cmyk_routes")
    else:
        raise ValueError("Must provide either rgb_array or cmyk_routes")

    return cmyk_routes
