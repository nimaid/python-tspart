import numpy as np
import scipy.misc
import scipy.ndimage
from etatime import EtaBar

from tspart.voronoi import centroids as voronoi_centroids


def normalize(D):
    Vmin, Vmax = D.min(), D.max()
    if Vmax - Vmin > 1e-5:
        D = (D - Vmin) / (Vmax - Vmin)
    else:
        D = np.zeros_like(D)
    return D


def initialization(n, D):
    """
    Return n points distributed over [xmin, xmax] x [ymin, ymax]
    according to (normalized) density distribution.

    with xmin, xmax = 0, density.shape[1]
         ymin, ymax = 0, density.shape[0]

    The algorithm here is a simple rejection sampling.
    """

    samples = []
    while len(samples) < n:
        # X = np.random.randint(0, D.shape[1], 10*n)
        # Y = np.random.randint(0, D.shape[0], 10*n)
        X = np.random.uniform(0, D.shape[1], 10 * n)
        Y = np.random.uniform(0, D.shape[0], 10 * n)
        P = np.random.uniform(0, 1, 10 * n)
        index = 0
        while index < len(X) and len(samples) < n:
            x, y = X[index], Y[index]
            x_, y_ = int(np.floor(x)), int(np.floor(y))
            if P[index] < D[y_, x_]:
                samples.append([x, y])
            index += 1
    return np.array(samples)


def stipple(
        grayscale_array,
        points=5000,
        iterations=50
):
    # We want (approximately) 500 pixels per voronoi region
    zoom = (points * 500) / (grayscale_array.shape[0] * grayscale_array.shape[1])
    density = scipy.ndimage.zoom(grayscale_array, zoom, order=0)

    density = 1.0 - normalize(density)
    #density = density[::-1, :]
    density_P = density.cumsum(axis=1)
    density_Q = density_P.cumsum(axis=1)

    # Initialization
    points = initialization(points, density)

    for i in EtaBar(range(iterations)):
        regions, points = voronoi_centroids(points, density, density_P, density_Q)

    return points / zoom
