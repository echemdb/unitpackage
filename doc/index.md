---
jupytext:
  formats: md:myst,ipynb
  text_representation:
    extension: .md
    format_name: myst
    format_version: 0.13
    jupytext_version: 1.14.5
kernelspec:
  display_name: Python 3 (ipykernel)
  language: python
  name: python3
---

# Welcome to unitpackage's documentation!

[![Binder](https://static.mybinder.org/badge_logo.svg)](https://mybinder.org/v2/gh/echemdb/unitpackage/0.10.0?labpath=tree%2Fdoc%2Findex.md)
[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.15644101.svg)](https://zenodo.org/records/15644101)

Annotation of scientific data plays a crucial role in research data management workflows to ensure that the data is stored according to the FAIR principles. A simple CSV file recorded during an experiment usually does, for example, not provide any information on the units of the values within the CSV, nor does it provide information on what system has been investigated or who performed the experiment. Such information can be stored in [frictionless Data Packages](https://frictionlessdata.io/), which consist of a CSV (data) file which is annotated with a JSON (metadata) file.
The `unitpackage` module provides a Python library to interact with such Data Packages, which have a very [specific structure](usage/unitpackage.md).
An example of using a collection of datapackages containing several entries along with the `unitpackage` Python library is found on [echemdb.org](https://www.echemdb.org/cv).
The website shows a collection of electrochemical data stored following in the [electrochemistry-data repository](https://github.com/echemdb/electrochemistry-data/) according to [echemdb's metadata schema](https://github.com/echemdb/metadata-schema).

## Examples

A collection of [entries can be generated](usage/load_and_save.md) from local files or from a remote repository, such as [echemdb.org](https://www.echemdb.org). To illustrate the usage of `unitpackage`,
we collect the data to [echemdb.org](https://www.echemdb.org/cv) from the data repository, which is downloaded by default when the method `from_remote()` does not receive a URL argument.

```{note}
For simplicity, we denote the collection as `db` (database), even though it is not a database in that sense.
```

```{code-cell} ipython3
from unitpackage.collection import Collection
db = Collection.from_remote()
```

A single entry can be retrieved with an identifier available in the database.

```{code-cell} ipython3
entry = db['engstfeld_2018_polycrystalline_17743_f4b_1']
```

The metadata of the entry is available from `entry.resource`.

The data related to an entry can be returned as a [pandas](https://pandas.pydata.org/) dataframe.

```{code-cell} ipython3
entry.df.head()
```

The units of the columns can be retrieved.

```{code-cell} ipython3
entry.field_unit('j')
```

The values in the dataframe can be changed to other compatible units.

```{code-cell} ipython3
rescaled_entry = entry.rescale({'E' : 'mV', 'j' : 'uA / m2'})
rescaled_entry.df.head()
```

The data can be visualized in a plotly figure.

```{code-cell} ipython3
entry.plot('E', 'j')
```

## Specific Collections

For certain datasets, the `unitpackage` module can be extended by additional modules. Such a module is the `Echemdb` class, which loads a collection of entries containing cyclic voltammograms stored according to the echemdb metadata schema.
Such data is usually found in the field of energy conversion and storage, as illustrated on [echemdb.org](https://www.echemdb.org/cv).

```{code-cell} ipython3
from unitpackage.database.echemdb import Echemdb
db = Echemdb.from_remote()
db.describe()
```

Filtering the collection for entries having specific properties, e.g., containing Pt as working electrode (WE) material, returns a new collection.

```{code-cell} ipython3
db_filtered = db.filter(lambda entry: entry.get_electrode('WE').material == 'Pt')
db_filtered.describe()
```

```{note}
The filtering method is also available to the base class `Collection`.
```

## Further Usage

Frictionless Data Packages or unitpackges are perfectly machine-readable, making the underlying data and metadata reusable in many ways.

* The `unitpackage` API can be used to filter collections of similar data for certain properties, thus allowing for simple comparison of different data sets. For example, you could think of comparing local files recorded in the laboratory with data published in a repository.
* The content of datapackages can be included in other applications or the generation of a website. The latter has been demonstrated for electrochemical data on [echemdb.org](https://www.echemdb.org/cv). The datapackages could also be published with the [frictionless Livemark](https://livemark.frictionlessdata.io/) data presentation framework.

## Installation

This package is available on [PiPY](https://pypi.org/project/unitpackage/) and can be installed with pip:

```sh .noeval
pip install unitpackage
```

The package is also available on [conda-forge](https://github.com/conda-forge/unitpackage-feedstock) and can be installed with conda

```sh .noeval
conda install -c conda-forge unitpackage
```

or mamba

```sh .noeval
mamba install -c conda-forge unitpackage
```

See the [installation instructions](installation.md) for further details.

### Citing

You can cite this project as described [on our Zenodo page](https://zenodo.org/records/15644101),
or use [this publication (***DSJ***, **24** (2025) 13)](https://doi.org/10.5334/dsj-2025-013) illustrating our approach.

## License

The contents of this repository are licensed under the [GNU General Public
License v3.0](https://www.gnu.org/licenses/gpl-3.0.html) or, at your option, any later version.

+++

```{toctree}
:maxdepth: 2
:caption: "Contents:"
:hidden:
installation.md
usage/unitpackage.md
usage/unitpackage_usage.md
usage/echemdb_usage.md
usage/load_and_save.md
api.md
```
