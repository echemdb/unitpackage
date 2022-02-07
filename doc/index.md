---
jupyter:
  jupytext:
    formats: md,ipynb
    text_representation:
      extension: .md
      format_name: markdown
      format_version: '1.3'
      jupytext_version: 1.13.6
  kernelspec:
    display_name: Python 3 (ipykernel)
    language: python
    name: python3
---

Welcome to echemdb's documentation!
========================================

```{todo}
* what is echemdb and what is our aim.
* then refer to installation, cli, api and cv.
```

The echemdb module provides direct access to the database and the entries presented on the EchemDB Website.

A database can also be created from local files which have the same file structure.

The entries found on [EchemDB Website](https://echemdb.github.io/website) can be stored in a local database.

```python
from echemdb.data.cv.database import Database
db = Database()
```

```{toctree}
:maxdepth: 2
:caption: "Contents:"
:hidden:
installation.md
usage/database_interactions.md
usage/entry_interactions.md
usage/bibliography.md
usage/local_database.md
```
