"""
Configuration file for the Sphinx documentation builder.

For the full list of built-in configuration values, see the documentation:
https://www.sphinx-doc.org/en/master/usage/configuration.html

@author "Daniel Mizsak" <info@pythonvilag.hu>
sphinx-build -b html docs/source/ docs/build/html
"""

from datetime import UTC, datetime

from private_lecture_automation import __version__

# Project
author = "Daniel Mizsak"
project = "private-lecture-automation"
copyright = f"{datetime.now(tz=UTC).year} {author}"  # noqa: A001
version = __version__

# General
master_doc = "index"
source_suffix = ".rst"
extensions = [
    "sphinx.ext.autodoc",
    "sphinx_copybutton",
]
nitpicky = True

# HTML
html_theme = "furo"
html_title = "private-lecture-automation"
pygments_style = "sphinx"
pygments_dark_style = "monokai"
html_static_path = ["_static"]
