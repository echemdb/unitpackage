project = 'unitpackage'
copyright = '2022-2023, the unitpackage authors'
author = 'the unitpackage authors'

release = '0.9.2'

extensions = ["sphinx.ext.autodoc", "sphinx.ext.todo", "myst_nb"]

source_suffix = [".rst", ".md"]

templates_path = ['_templates']

exclude_patterns = ['generated', 'Thumbs.db', '.DS_Store', 'README.md', 'news', '.ipynb_checkpoints', '*.ipynb', '**/*.ipynb']

myst_enable_extensions = ["amsmath", "dollarmath"]

todo_include_todos = True

html_theme = 'sphinx_rtd_theme'

nb_execution_timeout = 90

html_static_path = []

myst_heading_anchors = 2

# a warning is raised which is treated as an error when plotly plots are rendered.
# The plots are created even when the warning is ignored.
# Warning, treated as error:
# X:\github\unitpackage\doc\index.md:82:skipping unknown output mime type: application/vnd.plotly.v1+json [mystnb.unknown_mime_type]
suppress_warnings = ["mystnb.unknown_mime_type"]

# We render some demo notebooks as part of the documentation. These notebooks try to load plotly through RequireJS (which is how Jupyter notebooks load dependencies) so we need to ship this with our Sphinx documentation.
html_js_files = ["https://cdnjs.cloudflare.com/ajax/libs/require.js/2.3.4/require.min.js"]

# Add Edit on GitHub links
html_context = {
    'display_github': True,
    'github_user': 'echemdb',
    'github_repo': 'unitpackage',
    'github_version': 'main/doc/',
}

# Ignore the link to the GNU General Public License v3.0
# This is because checking results in a timeout.
linkcheck_ignore = [
    "https://www.gnu.org/licenses/gpl-3.0.html*",
]
