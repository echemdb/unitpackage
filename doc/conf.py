project = 'echemdb'
copyright = '2022, the echemdb website authors'
author = 'the echemdb authors'

release = '0.0.0'


extensions = ["sphinx.ext.autodoc", "sphinx.ext.todo", "myst_nb"]

source_suffix = {
    '.rst': 'restructuredtext',
    '.ipynb': 'myst-nb',
    '.myst': 'myst-nb',
}

templates_path = ['_templates']

exclude_patterns = ['generated', 'Thumbs.db', '.DS_Store', 'README.md', 'news', '.ipynb_checkpoints', '*.ipynb', '**/*.ipynb']

todo_include_todos = True

html_theme = 'sphinx_rtd_theme'

html_static_path = []

# TODO: Add linkchecke. See #131
#
# linkcheck_ignore = [
#     r'http://localhost:\d+/', 
#     r'https://github.com/echemdb/website/blob/main/doc\d+/',
# ]
# 
# html_context = {
#     'display_github': True,
#     'github_user': 'echemdb',
#     'github_repo': 'website',
#     'github_version': 'main/doc/',
# }