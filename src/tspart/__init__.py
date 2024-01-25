"""TSP Art Module for Python"""

__version__ = "0.4.2"


import tspart.voronoi
import tspart.tsp
import tspart.neos

from tspart._draw import draw_route, draw_cmyk_routes
from tspart._image import split_rgb, split_cmyk
from tspart._helpers import (
    image_to_array, map_points_to_tour, map_points_to_tour_multi, image_array_size, factors_from_image,
    factors_from_image_multi
)
from tspart._files import (
    save_tspart, load_tspart, load_image_as_array, save_tsplib, decode_tsplib, load_tsplib, load_cyc_tour
)
