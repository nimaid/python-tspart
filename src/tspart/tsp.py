import sys
import scipy.spatial
from ortools.constraint_solver import pywrapcp, routing_enums_pb2

from tspart._helpers import get_bounding_corners as _get_bounding_corners
from tspart._helpers import nearest_point_index as _nearest_point_index
from tspart._helpers import map_points_to_tour as _map_points_to_tour


# See https://developers.google.com/optimization/routing/tsp
def heuristic_solve(points, time_limit_minutes=60, symmetric=True, logging=True, verbose=False):
    distance_matrix = scipy.spatial.distance.cdist(points, points).round().astype(int)
    num_points = len(points)

    if symmetric:
        manager = pywrapcp.RoutingIndexManager(num_points, 1, 0)
    else:
        size = (_get_bounding_corners(points)[1] + 1)

        h_middle = int(round(size[0] / 2))
        start = _nearest_point_index(points, [h_middle, 0])
        end = _nearest_point_index(points, [h_middle, size[1]])

        manager = pywrapcp.RoutingIndexManager(num_points, 1, [start], [end])

    routing_parameters = pywrapcp.DefaultRoutingModelParameters()
    if logging and verbose:
        routing_parameters.solver_parameters.trace_propagation = True
        routing_parameters.solver_parameters.trace_search = True

    routing = pywrapcp.RoutingModel(manager, routing_parameters)

    def distance_callback(from_idx, to_idx):
        from_node = manager.IndexToNode(from_idx)
        to_node = manager.IndexToNode(to_idx)
        return distance_matrix[from_node][to_node]
    transit_callback_index = routing.RegisterTransitCallback(distance_callback)

    routing.SetArcCostEvaluatorOfAllVehicles(transit_callback_index)

    search_parameters = pywrapcp.DefaultRoutingSearchParameters()
    search_parameters.first_solution_strategy = (
        routing_enums_pb2.FirstSolutionStrategy.PATH_CHEAPEST_ARC
    )

    search_parameters.local_search_metaheuristic = (
        routing_enums_pb2.LocalSearchMetaheuristic.GUIDED_LOCAL_SEARCH)
    if time_limit_minutes:
        search_parameters.time_limit.seconds = int(round(time_limit_minutes * 60))

    if logging:
        search_parameters.log_search = True

    solution = routing.SolveWithParameters(search_parameters)

    if solution:
        index = routing.Start(0)
        tour = [manager.IndexToNode(index)]

        while not routing.IsEnd(index):
            index = solution.Value(routing.NextVar(index))
            tour.append(manager.IndexToNode(index))

        route = _map_points_to_tour(points, tour)

        return route
    else:
        return None


def heuristic_solves(points_list, time_limit_minutes=60, symmetric=True, logging=True, verbose=False):
    result = []
    for idx, points in enumerate(points_list):
        print(f"Solving image {idx + 1}/{len(points_list)}", file=sys.stderr)
        r = heuristic_solve(
            points=points,
            time_limit_minutes=time_limit_minutes,
            symmetric=symmetric,
            logging=logging,
            verbose=verbose
        )

        result.append(r)

    return result
