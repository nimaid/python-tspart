import scipy.spatial


def solve(points, closed=False):
    distance_matrix = scipy.spatial.distance.cdist(points, points)

    if not closed:
        distance_matrix[:, 0] = 0



    return order, distance
