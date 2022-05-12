project = 'echemdb'
copyright = '2022, the echemdb authors'
author = 'the echemdb authors'

release = '0.2.0'

extensions = ["sphinx.ext.autodoc", "sphinx.ext.todo", "myst_nb"]

source_suffix = [".rst", ".md"]

templates_path = ['_templates']

exclude_patterns = ['generated', 'Thumbs.db', '.DS_Store', 'README.md', 'news', '.ipynb_checkpoints', '*.ipynb', '**/*.ipynb']

todo_include_todos = True

html_theme = 'sphinx_rtd_theme'

execution_timeout = 90

html_static_path = []

# We render some demo notebooks as part of the documentation. These notebooks try to load plotly through RequireJS (which is how Jupyter notebooks load dependencies) so we need to ship this with our Sphinx documentation.
html_js_files = ["https://cdnjs.cloudflare.com/ajax/libs/require.js/2.3.4/require.min.js"]

# Add Edit on GitHub links
html_context = {
    'display_github': True,
    'github_user': 'echemdb',
    'github_repo': 'echemdb',
    'github_version': 'main/doc/',
}
