import io
import json
from PIL import Image

from tspart._helpers import ndarray_to_array_2d, image_to_array


def save_json(filename, obj, indent=2):
    with open(filename, "w") as f:
        json.dump(obj, f, indent=indent)


def load_json(filename):
    with open(filename, "r") as f:
        obj = json.load(f)

    return obj


def save_routes(filename, routes, size, indent=2):
    routes = ndarray_to_array_2d(routes)

    obj = {"size": size, "routes": routes}

    save_json(filename=filename, obj=obj, indent=indent)


def load_routes(filename):
    obj = load_json(filename)

    return obj["routes"], obj["size"]


def load_image_as_array(filename, mode="RGB"):
    img = Image.open(filename)
    return image_to_array(img, mode)


def save_tsplib(filename, points):
    with io.open(filename, "w", newline='\r\n') as f:
        f.write("NAME: tspart\n")
        f.write("TYPE: TSP\n")
        f.write(f"DIMENSION: {len(points)} 0\n")
        f.write("EDGE_WEIGHT_TYPE: EUC_2D\n")
        f.write("NODE_COORD_SECTION\n")

        for idx, (x, y) in enumerate(points):
            f.write(f"{idx + 1} {x:.6f} {y:.6f}\n")
