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

The bibliography to all entries is stored as a pybtex database `db.bibliography`, which is based on bibtex entries.
Each entry has a citation key, which is not identical to its identifier (but is part of it), since several entries can be found in the same source.
Both the citation key and the pybtex bibliography entry are accessible from the entry. 

```python
from echemdb.data.cv.database import Database
db = Database()
entry = db['alves_2011_electrochemistry_6010_p2_f2a_solid']
entry
```

```python
entry.source.citation_key
```

```python
entry.bibliography
```

With that key the bibliography can be retrieved from the db.bibliography

<!-- #raw -->
db.bibliography['alves_2011_electrochemistry_6010']
<!-- #endraw -->

```python

```

<!-- #raw -->
entry = db['alves_2011_electrochemistry_6010_p2_f2a_solid']
<!-- #endraw -->

<!-- #raw -->
entry.bibliography()
<!-- #endraw -->

<!-- #raw -->
entry.source.citation_key
<!-- #endraw -->

```python

```

## 
