import os
import sys
from datetime import datetime
from pathlib import Path
from typing import List

DOCS_DIR = Path(__file__).parent
sys.path.insert(0, os.path.abspath("../../src/biocontext_kb"))

# Project information
project = "BioContextAI KB"
author = "BioContextAI Team"
copyright = f"{datetime.now():%Y}, {author}."  # noqa: A001

# Configuration
templates_path = ["_templates"]
source_suffix = {
    ".rst": "restructuredtext",
    ".md": "markdown",
}
master_doc = "index"
default_role = "literal"

extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.coverage",
    "sphinx.ext.doctest",
    "sphinx.ext.intersphinx",
    "nbsphinx",
    "autoapi.extension",
    "sphinx.ext.napoleon",
    "sphinx_autodoc_typehints",
    "IPython.sphinxext.ipython_console_highlighting",
    "myst_parser",
    "sphinx.ext.viewcode",
]

# Myst parser settings
myst_enable_extensions = [
    "amsmath",
    "attrs_inline",
    "colon_fence",
    "deflist",
    "dollarmath",
    "fieldlist",
    "html_admonition",
    "html_image",
    "replacements",
    "smartquotes",
    "strikethrough",
    "substitution",
    "tasklist",
]

# Mapping for intersphinx extension
intersphinx_mapping = {
    "python": ("https://docs.python.org/3", None),
    # numpy=("https://numpy.org/doc/stable/", None),
    # matplotlib=("https://matplotlib.org/stable", None),
    # pandas=("https://pandas.pydata.org/pandas-docs/stable/", None),
    # anndata=("https://anndata.readthedocs.io/en/latest/", None),
    # scipy=("https://docs.scipy.org/doc/scipy", None),
    # sklearn=("https://scikit-learn.org/stable", None),
    # flowio=("https://flowio.readthedocs.io/en/latest/", None),
}

# don't run the notebooks
nbsphinx_execute = "never"

pygments_style = "sphinx"


exclude_trees = ["_build", "dist"]

exclude_patterns = [
    "_build",
    "Thumbs.db",
    ".DS_Store",
]

# Generate the API documentation when building
autoapi_type = "python"
autoapi_add_toctree_entry = False
autoapi_ignore: List[str] = ["_*.py"]
autoapi_dirs = ["../../src/biocontext_kb"]
autoapi_options = [
    "members",
    "undoc-members",
    "show-inheritance",
    "show-module-summary",
    "special-members",
    "imported-members",
]
autoapi_member_order = "alphabetical"

autosummary_generate = True

autodoc_member_order = "bysource"
autodoc_typehints = "description"

# Configuration of sphinx.ext.coverage
coverage_show_missing_items = True

# https://www.sphinx-doc.org/en/master/usage/extensions/napoleon.html
napoleon_google_docstring = True
napoleon_attr_annotations = True

# Configurate sphinx rtd theme
html_theme = "sphinx_book_theme"
html_theme_options = {
    "repository_url": "https://github.com/biocontext_ai/knowledgebase-mcp",
    "repository_branch": "main",
    "use_download_button": True,
    "use_fullscreen_button": False,
    "use_repository_button": True,
}
html_static_path = ["_static"]
html_show_sphinx = False
html_context = {
    "display_github": True,
    "github_user": "biocontext_ai",
    "github_repo": "server",
    "github_version": "main",
    "conf_py_path": "/docs/",
    "github_button": True,
    "show_powered_by": False,
}
html_title = "BioContextAI Knowledgebase MCP"
html_css_files = [
    "css/custom.css",
]
