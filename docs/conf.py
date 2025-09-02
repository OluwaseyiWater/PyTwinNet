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
    "python": ("https://docs.python.org/3", {}),
    "numpy": ("https://numpy.org/doc/stable/", {}),
    "matplotlib": ("https://matplotlib.org/stable/", {}),
}

myst_enable_extensions = ["colon_fence", "deflist", "fieldlist"]

templates_path = ["_templates"]
exclude_patterns = []
html_theme = "sphinx_rtd_theme"
html_static_path = ["_static"]
html_theme_options = {"collapse_navigation": False, "navigation_depth": 3, "display_version": True}
