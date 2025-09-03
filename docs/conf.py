from __future__ import annotations
import os, sys
from datetime import date

# Add repo root so autodoc can import pytwinnet
sys.path.insert(0, os.path.abspath(".."))
os.environ.setdefault("MPLBACKEND", "Agg")

project = "PyTwinNet"
author = "Oluwaseyi Giwa"
copyright = f"{date.today().year}, {author}"
release = os.environ.get("PYTWINNET_DOCS_VERSION", "latest")

extensions = [
    "myst_parser",
    "sphinx.ext.autodoc",
    "sphinx.ext.autosummary",
    "sphinx.ext.napoleon",
    "sphinx.ext.viewcode",
    "sphinx.ext.intersphinx",
    "sphinx.ext.mathjax",
    "sphinx_copybutton",
    "sphinx_autodoc_typehints",
    "sphinx_design",
]

autodoc_mock_imports = ["numba"]

autosummary_generate = True
autodoc_default_options = {"members": True, "undoc-members": False, "show-inheritance": True}
autodoc_typehints = "description"

intersphinx_mapping = {
    "python": ("https://docs.python.org/3", None),
    "numpy": ("https://numpy.org/doc/stable/", None),
    "matplotlib": ("https://matplotlib.org/stable/", None),
}

myst_enable_extensions = [
    "colon_fence", "deflist", "fieldlist",
    "dollarmath",           
    "amsmath",              
]
templates_path = ["_templates"] if os.path.isdir(os.path.join(os.path.dirname(__file__), "_templates")) else []
html_static_path = ["_static"] if os.path.isdir(os.path.join(os.path.dirname(__file__), "_static")) else []

html_theme = "sphinx_rtd_theme"
html_theme_options = {"collapse_navigation": False, "navigation_depth": 3, "display_version": True}

html_logo = "_static/img/pytwinnet-logo.svg"
html_favicon = "_static/img/favicon.svg"
html_css_files = ["css/custom.css"]
html_js_files = ["js/custom.js"]
extensions.append("sphinx_sitemap")
html_baseurl = "https://pytwinnet.readthedocs.io/en/latest/"
sitemap_url_scheme = "{link}"
html_extra_path = ["robots.txt"]


