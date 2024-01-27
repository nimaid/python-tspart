"""TSP Art Module for Python"""

__version__ = "0.6.10"


import tspart.voronoi
import tspart.tsp
import tspart.neos
import tspart.studio

from tspart._draw import draw_route, draw_cmyk_routes, draw_rgb_routes
from tspart._image import split_rgb, split_cmyk, rgb_to_grayscale, image_to_base64, base64_to_image
from tspart._helpers import (
    image_to_array, array_to_image, map_points_to_tour, map_points_to_tour_multi, image_array_size, factors_from_image,
    factors_from_image_multi, filter_white_points, filter_white_points_multi
)
from tspart._files import (
    make_tspart, save_tspart, load_tspart, save_array_as_image, load_image_as_array, make_tsplib, decode_tsplib,
    save_tsplib, load_tsplib, save_cyc_tour, load_cyc_tour, save_jobs, load_jobs
)
