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

# Bibliography

The bibliography to all entries is stored as a pybtex database `db.bibliography`, 
which basically contains bibtex entries.

```python
from echemdb.data.cv.database import Database
db = Database()
```

Each entry is associated with a citation key.

```python
entry = db['alves_2011_electrochemistry_6010_p2_f2a_solid']
entry.source.citation_key
```

as well as the bibliographic details.

```python
entry.bibliography
```

```{todo}
* show different possibilities to export the bibliography.
```

For comparison the the identifier to each entry contains the citation key. 

```python
entry.identifier
```

The bibliography key of an entry can be used to retrieve the bibliograhy entry directly from the complete database

<!-- #raw -->
db.bibliography['alves_2011_electrochemistry_6010']
<!-- #endraw -->
