---
jupytext:
  formats: md:myst,ipynb
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

# Bibliography

The bibliography to all entries is stored as a pybtex database `db.bibliography`, 
which basically contains bibtex entries.

```{code-cell} ipython3
from echemdb.cv.database import Database
db = Database()
```

Each database is associated with a [Pybtex](https://docs.pybtex.org/api/index.html) bibliography.

```{code-cell} ipython3
db.bibliography
```

Individual entries can be accessed with the citation key found in echemdbs' entries

```{code-cell} ipython3
entry = db['alves_2011_electrochemistry_6010_f1a_solid']
bibtex_key = entry.source.citation_key
bibtex_key
```

```{code-cell} ipython3
citation_entry = db.bibliography.entries[bibtex_key]
citation_entry
```

Individiual `fields` are accessible, such as year or title:

```{code-cell} ipython3
citation_entry.fields['year']
```

```{code-cell} ipython3
citation_entry.fields['title']
```

The authors are accessible via `persons`. Read more in the [pybtex documentation](https://docs.pybtex.org/api/parsing.html?highlight=persons#pybtex.database.Entry.persons).

```{code-cell} ipython3
citation_entry.persons['author']
```

```{code-cell} ipython3
citation_entry.persons['author'][0]
```

```{code-cell} ipython3
print(citation_entry.persons['author'][0])
```
