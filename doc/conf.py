project = 'echemdb'
copyright = '2022, the echemdb authors'
author = 'the echemdb authors'

release = '0.1.3'

extensions = ["sphinx.ext.autodoc", "sphinx.ext.todo", "myst_nb"]

source_suffix = [".rst", ".md"]

templates_path = ['_templates']

exclude_patterns = ['generated', 'Thumbs.db', '.DS_Store', 'README.md', 'news', '.ipynb_checkpoints', '*.ipynb', '**/*.ipynb']

todo_include_todos = True

html_theme = 'sphinx_rtd_theme'

execution_timeout = 90

html_static_path = []

# Add Edit on GitHub links
html_context = {
    'display_github': True,
    'github_user': 'echemdb',
    'github_repo': 'echemdb',
    'github_version': 'main/doc/',
}
