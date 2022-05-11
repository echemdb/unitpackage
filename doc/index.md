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

Welcome to echemdb's documentation!
========================================
[![Binder](https://mybinder.org/badge_logo.svg)](https://mybinder.org/v2/gh/echemdb/echemdb/0.1.3?urlpath=tree%2Fdoc%2Fusage%2Fentry_interactions.md) 
[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.6502901.svg)](https://doi.org/10.5281/zenodo.6502901)

This echemdb module provides a Python library to interact with a database of 
[frictionless datapackages](https://frictionlessdata.io/)
containing electrochemical data following [echemdb's metadata schema](https://github.com/echemdb/metadata-schema).
Such a database can be generated from the data schown on [echemdb.org](https://www.echemdb.org) 
or it can be created from local files which have the same file structure.

+++

Examples
========

The currently available data shown on [echemdb.org](https://www.echemdb.org) can be downloaded and stored in a database.

```{code-cell} ipython3
from echemdb.cv.database import Database
db = Database()
db.describe()
```

Filtering the database for entries having specific properties, e.g., containing Pt as working electrode material, returns a new database.

```{code-cell} ipython3
db_filtered = db.filter(lambda entry: entry.system.electrodes.working_electrode.material == 'Pt')
db_filtered.describe()
```

A single entry can be retrieved with the identifiers provided on the website
(see for example [engstfeld_2018_polycrystalline_17743_f4b_1](https://echemdb.github.io/website/cv/entries/engstfeld_2018_polycrystalline_17743_f4b_1/))

```{code-cell} ipython3
entry = db['engstfeld_2018_polycrystalline_17743_f4b_1']
```

Each entry has a set of descriptors which contain information about its `source`, the electrochemical system `system`, or the original publication's figure properties `entry.figure_description`.

```{code-cell} ipython3
entry.source # or entry['source']
```

The data related to an entry can be returned as a [pandas](https://pandas.pydata.org/) dataframe (values are provided in SI units).

```{code-cell} ipython3
entry.df.head()
```

```{code-cell} ipython3
entry.field_unit('E')
```

The dataframe can be returned with custom or original figure axes' units by rescaling the entry.

```{code-cell} ipython3
entry.rescale({'E' : 'mV', 'j' : 'uA / m2'}).df.head()
```

```{code-cell} ipython3
original_entry = entry.rescale('original')
original_entry.df.head()
```

The data can be visualized in a plotly figure:

```{code-cell} ipython3
original_entry.plot()
```

Installation
=========

The package is hosted on [PiPY](https://pypi.org/project/echemdb/) and can be installed via pip

```sh .noeval
pip install echemdb
```
or via conda

```sh .noeval
conda install echemdb
```

Read the [installation instructions](installation.md) on further details if you want to contribute to the project.

+++

```{toctree}
:maxdepth: 2
:caption: "Contents:"
:hidden:
installation.md
usage/database_interactions.md
usage/entry_interactions.md
usage/bibliography.md
usage/local_database.md
api.md
```
