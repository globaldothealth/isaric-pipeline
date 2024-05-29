# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

import os
import sys

# Add root dir so that adtl module is visible to Sphinx
sys.path.insert(0, os.path.abspath(".."))
sys.path.insert(0, os.path.abspath("."))

project = "fhirflat"
copyright = "2024, Global.health"
release = "0.1.0"

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.coverage",
    "sphinx.ext.napoleon",
    "myst_parser",
]

templates_path = ["_templates"]
exclude_patterns = ["_build", "Thumbs.db", ".DS_Store", ".venv"]


# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = "furo"
html_static_path = ["_static"]

html_theme_options = {
    "light_css_variables": {
        "color-brand-primary": "#0e7569",
        "color-problematic": "#0e7569",
        "color-brand-content": "#0e7569",
        "color-background-secondary": "#ecf3f0",
        "color-background-hover": "#cfe6db",
    },
    "dark_css_variables": {
        "color-brand-primary": "#d2d9d6",
        "color-problematic": "#d2d9d6",
        "color-brand-content": "#d2d9d6",
        "color-background-secondary": "#0b5950",
    },
}