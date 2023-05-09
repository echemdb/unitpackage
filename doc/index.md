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

Welcome to unitpackage's documentation!
========================================
[![Binder](https://mybinder.org/badge_logo.svg)](https://mybinder.org/v2/gh/echemdb/unitpackage/0.6.0?urlpath=tree%2Fdoc%2Fusage%2Fentry_interactions.md)
[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.6502901.svg)](https://doi.org/10.5281/zenodo.6502901)

This module provides a Python library to interact with a collection of
[frictionless datapackages](https://frictionlessdata.io/). Such datapackages consist of a CSV (data) file which is annotated with a JSON file.
This allows storing additional information such as units used in the columns of a CSV or store metadata describing the underlying (scientific) data. With these information the data become machine readable, searchable and interoperable with other systems. An example demonstrating the usage of a collection of datapackages along with the `unitpackage` Python library is [echemdb.org](https://www.echemdb.org), which shows a collection of electrochemical data following following [echemdb's metadata schema](https://github.com/echemdb/metadata-schema).

A collection of datapackages can be generated from the data on [echemdb.org](https://www.echemdb.org) or from local files. To illustrate the usage of `unitpackage` we use in the following examples data available on [echemdb.org](https://www.echemdb.org).

Examples
========

The currently available data shown on [echemdb.org](https://www.echemdb.org) can be downloaded and stored in a collection. Information on how to load local datapackages can be found [here](usage/local_collection.md).

```{code-cell} ipython3
from unitpackage.cv.cv_collection import CVCollection
db = CVCollection()
db.describe()
```

````{note}
A collection of any kind of data is usually invoked via
```python
from unitpackage.collection import Collection
```
`CVCollection` class has functionalities specific for cyclic voltammetry data.
````

Filtering the collection for entries having specific properties, e.g., containing Pt as working electrode material, returns a new collection.

```{code-cell} ipython3
db_filtered = db.filter(lambda entry: entry.get_electrode('WE').material == 'Pt')
db_filtered.describe()
```

A single entry can be retrieved with the identifiers provided on the website
(see for example [engstfeld_2018_polycrystalline_17743_f4b_1](https://echemdb.github.io/website/cv/entries/engstfeld_2018_polycrystalline_17743_f4b_1/))

```{code-cell} ipython3
entry = db['engstfeld_2018_polycrystalline_17743_f4b_1']
```

Each entry has a set of descriptors such as its ``source`` or the electrochemical ``system``.

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
============

This package is available on [PiPY](https://pypi.org/project/unitpackage/) and can be installed with pip:

```sh .noeval
pip install unitpackage
```

The package is also available on [conda-forge](https://github.com/conda-forge/unitpackage-feedstock) an can be installed with conda

```sh .noeval
conda install -c conda-forge unitpackage
```

or mamba

```sh .noeval
mamba install -c conda-forge unitpackage
```

See the [installation instructions](installation.md) for further details.

License
=======

The contents of this repository are licensed under the [GNU General Public
License v3.0](https://www.gnu.org/licenses/gpl-3.0.html) or, at your option, any later version.

+++

```{toctree}
:maxdepth: 2
:caption: "Contents:"
:hidden:
installation.md
usage/collection_interactions.md
usage/entry_interactions.md
usage/bibliography.md
usage/local_collection.md
api.md
```
