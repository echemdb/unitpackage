---
jupytext:
  formats: ipynb,md:myst
  text_representation:
    extension: .md
    format_name: myst
    format_version: 0.13
    jupytext_version: 1.13.7
kernelspec:
  display_name: Python 3 (ipykernel)
  language: python
  name: python3
---

+++ {"tags": []}

# Database interaction

+++

The entries on [EchemDB Website](https://echemdb.github.io/website) can be downloaded into a local database.

```{code-cell} ipython3
from echemdb.data.cv.database import Database
db = Database()
```

The number of entries in the databse are

```{code-cell} ipython3
len(db)
```

You can iterate over these entries

```{code-cell} ipython3
next(iter(db))
```

The database can be filtered for specific descriptors (see below), 
wherby a new database is created.


```{code-cell} ipython3
db_filtered = db.filter(lambda entry: entry.system.electrodes.working_electrode.material == 'Pt')
print(f'{len(db_filtered)} entries contain Pt as working electrode material.')
```

Single entries can be selected by their identifier provided on the [echemDB website](https://echemdb.github.io/website) for each entry.

```{code-cell} ipython3
entry = db['alves_2011_electrochemistry_6010_p2_f2a_solid']
entry
```
