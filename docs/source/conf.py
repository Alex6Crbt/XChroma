# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

import os
import sys

sys.path.insert(0, os.path.abspath('../../'))


# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

project = 'XChroma'
copyright = '2025, Alexis C'
author = 'Alexis C.'
release = '1.1'

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.autosummary",
    "sphinx.ext.viewcode",
    "sphinx.ext.napoleon",
    "sphinx_copybutton",
    "sphinx_design",
    "sphinx_favicon",
    ]

templates_path = ['_templates']
exclude_patterns = []
autodoc_mock_imports = ["pyqtgraph", "PyQt6"]

language = 'en'

# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = 'pydata_sphinx_theme'
html_static_path = ['_static']
html_logo = "_static/captX.png"
html_context = {
    "default_mode": "dark",
}
html_theme_options = {
  "show_nav_level": 2
}
html_theme_options = {
    "footer_start": ["copyright"],
    "footer_end": [],
    "logo": {
        "text": "XChroma",
        },
    "icon_links": [
    {
        "name": "GitHub",
        "url": "https://github.com/Alex6Crbt/XChroma",
        "icon": "fa-brands fa-github",
    },],
}
