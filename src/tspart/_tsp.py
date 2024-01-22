import random
import numpy as np
import scipy.spatial
from ortools.constraint_solver import pywrapcp, routing_enums_pb2


# See https://developers.google.com/optimization/routing/tsp
def solve(points, closed=False):
    distance_matrix = scipy.spatial.distance.cdist(points, points)

    '''
    if not closed:
        distance_matrix[:, 0] = 0
    '''

    if closed:
        manager = pywrapcp.RoutingIndexManager(len(distance_matrix), 1, 0)
    else:
        end = random.choice([_ for _ in range(1, len(points))])
        manager = pywrapcp.RoutingIndexManager(len(distance_matrix), 1, [0], [end])

    routing = pywrapcp.RoutingModel(manager)

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

    search_parameters.log_search = True

    solution = routing.SolveWithParameters(search_parameters)

    index = routing.Start(0)
    route = np.ndarray([manager.IndexToNode(index)])
    while not routing.IsEnd(index):
        index = solution.Value(routing.NextVar(index))
        np.append(route, manager.IndexToNode(index))

    return route
