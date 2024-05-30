# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

import os
import sys

import better

# Add root dir so that adtl module is visible to Sphinx
sys.path.insert(0, os.path.abspath(".."))

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
toc_object_entries = False  # prevent classes from showing in toctree

# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = "better"
html_static_path = ["_static"]
html_theme_path=[better.better_theme_path]
html_short_title = "Home"

html_theme_options = {
    "rightsidebar": True,
    "sidebarwidth": "25rem",
    "cssfiles": ["_static/style.css"],
    "showheader": False,
}