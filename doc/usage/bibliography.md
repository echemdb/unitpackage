---
jupytext:
  formats: md:myst,ipynb
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

# Bibliography

The bibliography to all entries is stored as a pybtex database `db.bibliography`, 
which basically contains bibtex entries.

```{code-cell} ipython3
from echemdb.data.cv.database import Database
db = Database()
```

Each entry is associated with a citation key.

```{code-cell} ipython3
entry = db['alves_2011_electrochemistry_6010_f2a_solid']
entry.source.citation_key
```

as well as the bibliographic details.

```{code-cell} ipython3
entry.bibliography
```

```{todo}
* show different possibilities to export the bibliography.
```

For comparison the the identifier to each entry contains the citation key. 

```{code-cell} ipython3
entry.identifier
```

The bibliography key of an entry can be used to retrieve the bibliograhy entry directly from the complete database

```{raw-cell}
db.bibliography['alves_2011_electrochemistry_6010']
```
