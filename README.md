The [echemdb repository](https://echemdb.github.io/website/) contains high
quality experimental and theoretical data on electrochemical systems.

This module provides a Python library to interact with the data in the repository.

In the following we provide installation instructions for the echemdb module
and a short summary of the basic usage of the Python API. Detailed installation
instructions, description of the modules, advanced usage examples, including
local database creation, are provided in our
[documentation](https://echemdb.github.io/echemdb/).

# Installation instructions

<!-- TODO: Make echemdb pip installable, publish on PyPI and conda-forge. See #130
```
pip install echemdb
```


Create an environment with the required packages

```
conda config --add channels conda-forge
conda config --set channel_priority strict
conda env create --force -f environment.yml
```

Alternatively, if you want to install the required packages into an existing, environment use:

```
conda env update --name <your_env_name> --file environment.yml
```
-->

Clone the repository and install echemdb

```
pip install git+https://github.com/echemdb/echemdb.git
```

# Python API

The current state of the website can be downloaded and stored in a database.

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

Each entry has information about its source

```python
>>> entry.source # or entry['source']
{'citation key': 'engstfeld_2018_polycrystalline_17743', 'curve': 1, 'url': 'https://doi.org/10.1002/chem.201803418', 'figure': '4b', 'version': 1}
```

Among other metadata, the entry also has information on the original publication's figure properties (`entry.figure_description`) and the `entry.system` in general.

The data related to an entry can be returned as a [pandas](https://pandas.pydata.org/) dataframe (values are provided in SI units) and can be stored as a CSV file (or any other format supported by pandas).

```python
>>> entry.df
           t	        E	       j
0	0.000000	-0.196962	0.043009
1	0.011368	-0.196393	0.051408
...
>>> entry.df.to_csv('../testtesttest.csv', index=False)
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
