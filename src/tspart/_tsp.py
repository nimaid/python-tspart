import random
import math
import numpy as np
import scipy.spatial
from ortools.constraint_solver import pywrapcp, routing_enums_pb2


# See https://developers.google.com/optimization/routing/tsp
def solve(points, closed=False, solution_limit=None, time_limit_minutes=1, logging=True, verbose=False):
    distance_matrix = scipy.spatial.distance.cdist(points, points).round().astype(int)
    num_points = len(points)

    if closed:
        manager = pywrapcp.RoutingIndexManager(num_points, 1, 0)
    else:
        end = random.choice([_ for _ in range(1, num_points)])
        manager = pywrapcp.RoutingIndexManager(num_points, 1, [0], [end])

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
    if solution_limit:
        search_parameters.solution_limit = solution_limit
    if time_limit_minutes:
        search_parameters.time_limit.seconds = int(round(time_limit_minutes * 60))

    if logging:
        search_parameters.log_search = True

    solution = routing.SolveWithParameters(search_parameters)

    if solution:
        index = routing.Start(0)
        route = [manager.IndexToNode(index)]

        while not routing.IsEnd(index):
            index = solution.Value(routing.NextVar(index))
            route.append(manager.IndexToNode(index))

        return route
    else:
        return None
