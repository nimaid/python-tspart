# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

import os
import sys

base_path = os.path.realpath(os.path.sep.join([".." for _ in range(2)]))
src_path = os.path.join(base_path, "src")
sys.path.insert(
    0,
    src_path
)

project = 'TSP Art (tspart)'
copyright = '2023, Ella Jameson'
author = 'Ella Jameson'

version = None
version_prefix = "__version__ = "
with open(os.path.join(src_path, "tspart", "__init__.py")) as f:
    for line in f.readlines():
        line = line.strip("\n").strip("\r").strip()

        if line[:len(version_prefix)] == version_prefix:
            version = line.split("=")[1].split("#")[0].strip().replace("\"", "")
            break
assert version is not None
version = f"v{version}"

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = [
    'autoapi.extension',
    'sphinx_rtd_theme'
]

autoapi_dirs = [src_path]
autoapi_options = [
    'members',
    'undoc-members',
    #'private-members'
    'show-inheritance',
    'show-module-summary',
    #'special-members',
    'imported-members'
]
autoapi_add_toctree_entry = True


def skip_version(app, what, name, obj, skip, options):
    if ".__version__" in name:
        skip = True
    return skip


def setup(sphinx):
    sphinx.connect("autoapi-skip-member", skip_version)


templates_path = ['_templates']
exclude_patterns = []

# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = 'sphinx_rtd_theme'
html_theme_options = {
    'navigation_depth': 4,
    'display_version': True
}
html_static_path = ['_static']