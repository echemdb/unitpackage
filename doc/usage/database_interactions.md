---
jupytext:
  formats: ipynb,md:myst
  text_representation:
    extension: .md
    format_name: myst
    format_version: 0.13
    jupytext_version: 1.13.8
kernelspec:
  display_name: Python 3 (ipykernel)
  language: python
  name: python3
---

+++ {"tags": []}

# Database interaction

+++

A database can be generated from a remote or a local source.

You can create a database from the entries on [echemdb.org](https://www.echemdb.org):

```{code-cell} ipython3
from unitpackage.cv.cv_database import CVDatabase
db = CVDatabase()
```

Show statistics of the databse

```{code-cell} ipython3
db.describe()
```

You can iterate over these entries

```{code-cell} ipython3
next(iter(db))
```

The database can be filtered for specific descriptors,
wherby a new database is created.

```{code-cell} ipython3
db_filtered = db.filter(lambda entry: entry.system.electrodes.working_electrode.material == 'Pt')
db_filtered.describe()
```

Single entries can be selected by their identifier provided on the [echemdb.org](https://www.echemdb.org) for each entry.

```{code-cell} ipython3
entry = db['engstfeld_2018_polycrystalline_17743_f4b_1']
entry
```
