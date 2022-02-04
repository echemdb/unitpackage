---
jupyter:
  jupytext:
    formats: ipynb,md
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

<!-- #region tags=[] -->
## EchemDB Website content
<!-- #endregion -->

The content of [EchemDB Website](https://echemdb.github.io/) can be stored in a local database.

```python
from echemdb.data.cv.database import Database
db = Database()
```

### Database interaction


The number of entries in the databse

```python
len(db)
```

You can iterate over these entries

```python
next(iter(db))
```

The database can be filtered for specific descriptors (see below) which returns a new database.

```python
db_filtered = db.filter(lambda entry: entry.electrochemical_system.electrodes.working_electrode.material == 'Pt')
print(f'{len(db_filtered)} entries contain Pt as working electrode material.')
```

Single entries can be selected by their identifier provided on the [echemDB website](https://echemdb.github.io/) for each entry.

```python
entry = db['alves_2011_electrochemistry_6010_p2_f2a_solid']
entry
```
