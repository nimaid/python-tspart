import os

from . import paths

RESOURCE_PATH = os.path.join(paths.PATH, "resources")

# A dict to store icon locations
ICON_PATHS = {
    "program": os.path.join(RESOURCE_PATH, "icon.png"),
}
