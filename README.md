[![Binder](https://mybinder.org/badge_logo.svg)](https://mybinder.org/v2/gh/echemdb/echemdb/0.4.0?urlpath=tree%2Fdoc%2Fusage%2Fentry_interactions.md)
[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.6502901.svg)](https://doi.org/10.5281/zenodo.6502901)

The echemdb Python package can interact with a database of
[frictionless datapackages](https://frictionlessdata.io/)
containing electrochemical data following [echemdb's metadata schema](https://github.com/echemdb/metadata-schema).
Such a database can be generated from the data on [echemdb.org](https://www.echemdb.org)
or from local files.

Detailed installation instructions, description of the modules, advanced usage examples, including
local database creation, are provided in our
[documentation](https://echemdb.github.io/echemdb/).

# Installation instructions

Install the latest stable version of svgdigitizer from PyPI or conda.
```
pip install echemdb
```

```
conda install -c conda-forge echemdb
```

# Python API

The currently available data shown on [echemdb.org](https://www.echemdb.org) can be downloaded and stored in a database.

```python
>>> from echemdb.cv.database import Database
>>> db = Database()
```

Filtering the database for entries having specific properties, e.g., containing Pt as working electrode material, returns a new database.

```python
>>> db_filtered = db.filter(lambda entry: entry.system.electrodes.working_electrode.material == 'Pt')
```

A single entry can be retrieved with the identifiers provided on the website
(see for example [engstfeld_2018_polycrystalline_17743_f4b_1](https://echemdb.github.io/website/cv/entries/engstfeld_2018_polycrystalline_17743_f4b_1/))

```python
>>> entry = db['engstfeld_2018_polycrystalline_17743_f4b_1']
```

Each entry has a set of descriptors such as its ``source`` or the electrochemical ``system``.

```python
>>> entry.source # or entry['source']
{'citation key': 'engstfeld_2018_polycrystalline_17743', 'curve': 1, 'url': 'https://doi.org/10.1002/chem.201803418', 'figure': '4b', 'version': 1}
```

The data related to an entry can be returned as a [pandas](https://pandas.pydata.org/) dataframe (values are provided in SI units).

```python
>>> entry.df
           t	        E	       j
0	0.000000	-0.196962	0.043009
1	0.011368	-0.196393	0.051408
...
```

The dataframe can be returned with custom or original figure axes' units by rescaling the entry.

```python
>>> entry.rescale({'E' : 'mV', 'j' : 'uA / m2'}).df
          t           E             j
0  0.000000 -196.961730  43008.842162
1  0.011368 -196.393321  51408.199892
...
>>> entry.rescale('original').df
          t         E         j
0  0.000000 -0.196962  4.300884
1  0.011368 -0.196393  5.140820
...
```

The units and reference electrodes can be found in the resource schema. The units are updated upon rescaling an entry.

```python
>>> entry.package.get_resource('echemdb')['schema']
{'fields':
[{'name': 't', 'unit': 's', 'type': 'number'},
{'name': 'E', 'unit': 'V', 'reference': 'RHE', 'type': 'number'},
{'name': 'j', 'unit': 'A / m2', 'type': 'number'}]}
```

The data can be visualized in a plotly figure:

```python
>>> entry.plot()
```
<img src=https://raw.githubusercontent.com/echemdb/echemdb/main/doc/images/readme_demo_plot.png style="width:400px">

# License

The contents of this repository are licensed under the [GNU General Public
License v3.0](./LICENSE) or, at your option, any later version.
