import sys

from tspart import stipple, solve, split_cmyk, map_points_to_route


def transform(
        grayscale_array,
        stipple_points=5000,
        stipple_iterations=50,
        closed=False,
        solution_limit=None,
        time_limit_minutes=1,
        logging=True,
        verbose=False
):
    if logging:
        print(f"Stippling with {stipple_points} points over {stipple_iterations} iterations...", file=sys.stderr)
    points = stipple(
        grayscale_array,
        points=stipple_points,
        iterations=stipple_iterations
    )

    if logging:
        print(f"Solving with a time limit of {int(round(time_limit_minutes * 60 * 1000))}"
              f" ms and a solution limit of {solution_limit}...", file=sys.stderr)
    route = solve(
        points=points,
        closed=closed,
        solution_limit=solution_limit,
        time_limit_minutes=time_limit_minutes,
        logging=logging,
        verbose=verbose
    )

    return map_points_to_route(points, route)


def transform_cmyk(
        rgb_array,
        stipple_points=5000,
        stipple_iterations=50,
        closed=False,
        solution_limit=None,
        time_limit_minutes=1,
        logging=True,
        verbose=False
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
            solution_limit=solution_limit,
            time_limit_minutes=time_limit_minutes,
            logging=logging,
            verbose=verbose
        )

        cmyk_routes.append(channel_image)

    return cmyk_routes
