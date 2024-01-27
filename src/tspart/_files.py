import json
import numpy as np
from PIL import Image

from tspart._helpers import ndarray_to_array_2d, array_to_ndarray_2d, image_to_array, array_to_image


class TsplibSyntaxError(SyntaxError):
    pass


def save_json(filename, obj, indent=2):
    with open(filename, "w") as f:
        json.dump(obj, f, indent=indent)


def load_json(filename):
    with open(filename, "r") as f:
        obj = json.load(f)

    return obj


def make_tspart(points, size, factors=None):
    points = ndarray_to_array_2d(points)
    if factors is not None:
        factors = [list(_) for _ in factors]

    return {"points": points, "factors": factors, "size": size}


def save_tspart(filename, points, size, factors=None, indent=2):
    obj = make_tspart(
        points=points,
        size=size,
        factors=factors
    )

    save_json(filename=filename, obj=obj, indent=indent)


def load_tspart(filename):
    obj = load_json(filename)

    points = array_to_ndarray_2d(obj["points"])
    size = obj["size"]
    if obj["factors"] is not None:
        factors = [np.array(_) for _ in obj["factors"]]
    else:
        factors = None

    return {"points": points, "factors": factors, "size": size}


def load_image_as_array(filename, mode="RGB"):
    img = Image.open(filename)
    return image_to_array(img, mode)


def save_array_as_image(filename, array, mode="RGB"):
    array_to_image(array, mode).save(filename)


def make_tsplib(points, name="tspart"):
    result = f"NAME: {name}\r\n"
    result += "TYPE: TSP\r\n"
    result += f"DIMENSION: {len(points)}\r\n"
    result += "EDGE_WEIGHT_TYPE: EUC_2D\r\n"
    result += "NODE_COORD_SECTION\r\n"

    for idx, (x, y) in enumerate(points):
        result +=f"{idx + 1} {x:.6f} {y:.6f}\r\n"

    return result


def save_tsplib(filename, points):
    with open(filename, "w") as f:
        f.write(make_tsplib(points))


def decode_tsplib(text):
    lines = text.split("\n")
    lines = [_.strip().strip("\r").strip() for _ in lines]

    lines = [_ for _ in lines if _ != ""]

    start_string = "EDGE_WEIGHT_TYPE: EUC_2D"
    if start_string not in lines:
        raise TsplibSyntaxError(f"Invalid format, string '{start_string}' not found")

    start_idx = lines.index(start_string) + 1

    points = []
    for line in lines[start_idx:]:
        split_line = line.split(" ")
        if not all([_.isnumeric() for _ in split_line]):
            break

        points.append(np.array([split_line[1], split_line[2]]))

    return points


def load_tsplib(filename):
    with open(filename, "r") as f:
        text = f.read()

    return decode_tsplib(text)


def save_cyc_tour(filename, tour):
    with open(filename, "w") as f:
        for idx in tour:
            f.write(f"{idx}\n")


def load_cyc_tour(filename):
    with open(filename, "r") as f:
        tour = [int(_.strip()) for _ in f.readlines() if _.strip() != ""]

    return tour


def save_jobs(filename, jobs):
    save_json(filename, {"jobs": jobs})


def load_jobs(filename):
    return load_json(filename)["jobs"]
