from __future__ import annotations
import os, sys
from datetime import date

# Make package importable
sys.path.insert(0, os.path.abspath(".."))

# Headless plotting for safety
os.environ.setdefault("MPLBACKEND", "Agg")

project = "PyTwinNet"
author = "Your Name"
copyright = f"{date.today().year}, {author}"
# Keep in sync with pytwinnet/__about__.py if you want to display it
release = "0.1.2"

extensions = [
    "myst_parser",
    "sphinx.ext.autodoc",
    "sphinx.ext.autosummary",
    "sphinx.ext.napoleon",
    "sphinx.ext.viewcode",
    "sphinx.ext.intersphinx",
    "sphinx_copybutton",
    "sphinx_autodoc_typehints",
    "sphinx_design",
]

# --- Key safety settings ---
autosummary_generate = True
autodoc_default_options = {"members": True, "undoc-members": False, "show-inheritance": True}
autodoc_typehints = "description"
# If numba isn't available on RTD image, mock it to avoid import errors
autodoc_mock_imports = ["numba"]

intersphinx_mapping = {
    "python": ("https://docs.python.org/3", None),
    "numpy": ("https://numpy.org/doc/stable/", None),
    "matplotlib": ("https://matplotlib.org/stable/", None),
}


myst_enable_extensions = ["colon_fence", "deflist", "fieldlist"]

html_static_path = ["_static"] if os.path.isdir(os.path.join(os.path.dirname(__file__), "_static")) else []
templates_path = ["_templates"] if os.path.isdir(os.path.join(os.path.dirname(__file__), "_templates")) else []
exclude_patterns = []
html_theme = "sphinx_rtd_theme"
html_theme_options = {"collapse_navigation": False, "navigation_depth": 3, "display_version": True}
