import json

from tspart._helpers import ndarray_to_array_2d


def save_json(filename, obj, indent=2):
    with open(filename, "w") as f:
        json.dump(obj, f, indent=indent)


def load_json(filename):
    with open(filename, "r") as f:
        obj = json.load(f)

    return obj


def save_cmyk_routes(filename, cmyk_routes, size, indent=2):
    cmyk_routes = ndarray_to_array_2d(cmyk_routes)

    obj = {"size": size, "cmyk_routes": cmyk_routes}

    save_json(filename=filename, obj=obj, indent=indent)
