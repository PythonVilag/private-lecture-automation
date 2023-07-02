"""
Configuration file for the Sphinx documentation builder.
For the full list of built-in configuration values, see the documentation:
https://www.sphinx-doc.org/en/master/usage/configuration.html

@author "Dániel Lajos Mizsák" <info@pythonvilag.hu>
"""

from private_lecture_automation import __version__

# Project
project = "private-lecture-automation"
copyright = "2023 Dániel Lajos Mizsák"
author = "Dániel Lajos Mizsák"
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
