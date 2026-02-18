[![Binder](https://static.mybinder.org/badge_logo.svg)](https://mybinder.org/v2/gh/echemdb/unitpackage/0.12.0?labpath=tree%2Fdoc%2Findex.md)
[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.15644101.svg)](https://zenodo.org/records/15644101)

# unitpackage

A Python library to create, interact with, and store collections of [frictionless Data Packages](https://frictionlessdata.io/) whose tabular resources carry **unit-aware field metadata**. Each data package pairs a CSV file with a JSON descriptor containing schema information (column names, types, units) and arbitrary nested metadata.

## Key features

- **Unit-aware fields** — columns carry unit metadata (e.g. `V`, `A / m2`, `s`) and can be rescaled to compatible units.
- **Collections** — load, filter, slice, and iterate over sets of data packages from local directories or remote sources.
- **Metadata access** — nested metadata is accessible via attribute-style or dict-style access.
- **Plotting** — built-in 2D plotting with plotly.
- **Domain extensions** — subclass `Collection` and `Entry` for domain-specific features (e.g. electrochemistry via `Echemdb`).

## Quick example

```python
>>> from unitpackage.collection import Collection
>>> db = Collection.from_local('./doc/files')
>>> entry = db['demo_package_cv']
>>> entry.echemdb.description
'Sample data for the unitpackage module'
```

Access field units and rescale data:

```python
>>> entry.field_unit('j')
'A / m2'
>>> entry.rescale({'E' : 'mV', 'j' : 'uA / m2'}).df
          t           E             j
0  0.000000 -196.961730  43008.842162
1  0.011368 -196.393321  51408.199892
...
```

Plot directly from an entry:

```python
>>> entry.plot()
```

<img src=https://raw.githubusercontent.com/echemdb/unitpackage/main/doc/images/readme_demo_plot.png style="width:400px">

Rescale an entire collection at once:

```python
>>> rescaled = db.rescale({'E': 'mV', 'j': 'uA / m2'})
>>> rescaled[0].field_unit('E')
'mV'
```

Detailed usage examples, including local collection creation and metadata handling, are provided in the [documentation](https://echemdb.github.io/unitpackage/).

# Installation

This package is available on [PyPI](https://pypi.org/project/unitpackage/) and can be installed with pip:

```sh .noeval
pip install unitpackage
```

The package is also available on [conda-forge](https://github.com/conda-forge/unitpackage-feedstock) and can be installed with conda

```sh .noeval
conda install -c conda-forge unitpackage
```

Please consult our [documentation](https://echemdb.github.io/unitpackage/) for
more detailed [installation instructions](https://echemdb.github.io/unitpackage/installation.html).

# License

The contents of this repository are licensed under the [GNU General Public
License v3.0](./LICENSE) or, at your option, any later version.
