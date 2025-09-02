
from __future__ import annotations
import os, sys
from datetime import date

# Add project root so autodoc finds pytwinnet
sys.path.insert(0, os.path.abspath(".."))

project = "PyTwinNet"
author = "Oluwaseyi Giwa"
copyright = f"{date.today().year}, {author}"
# Keep in sync with pytwinnet/__about__.py if you want it shown
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

autosummary_generate = True
autodoc_default_options = {"members": True, "undoc-members": False, "show-inheritance": True}
autodoc_typehints = "description"

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
