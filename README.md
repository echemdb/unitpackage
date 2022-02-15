The [echemdb repository](https://github.com/echemdb/website) 
contains high quality experimental and 
theoretical data on electrochemical systems. 
The standardized and validated data displayed on the [projects website](https://echemdb.github.io/website/) so far is from the community and publications aiming at fullfilling the [FAIR principles](https://www.go-fair.org/fair-principles/). 

The repository consists of two interdependent parts:
1. a Python library
2. pages and tools to build the website

In the following we provide installation instructions for the echemdb module and a short summary of the basic usage of the Python API. For detailed installation instructions, description of the modules, advanced usage examples, including local database creation, and building the website locally, is provided in our [documentation](https://echemdb.github.io/website/doc/html/index.md).

# Installation instructions

<!-- I hope we can publish soon on PyPI then this section reduces to 
```
pip install echemdb
```
-->

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

Clone the repository and install echemdb

```
git clone https://github.com/echemdb/website.git
cd website
pip install -e .
```

# Python API

The current state of the website can be downloaded and stored in a database.

```python
>>> from echemdb.data.cv.database import Database
>>> db = Database()
```

Filtering the database for entries having specific properties, i.e., containing Pt as working electrode material, returns a new database.

```python
>>> db_filtered = db.filter(lambda entry: entry.electrochemical_system.electrodes.working_electrode.material == 'Pt')
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

Among other metadata, the entry also has information on the original figure properties (`entry.figure_description`) and the `entry.electrochemical_system` in general.

The data related to an entry can be returned as a [pandas](https://pandas.pydata.org/) dataframe (values are provided in SI units) and can be stored as CSV file (or any other format supported by pandas).

```python
>>> entry.df() 
           t	        E	       j
0	0.000000	-0.196962	0.043009
1	0.011368	-0.196393	0.051408
...
# Custom or original figure axes units can be set specifically 
# entry.df(xunit='original', yunit='mA / m2')
>>> entry.df().to_csv('../testtesttest.csv', index=False)
```

The reference electrode to the potential axis `E` is provided in the `entry.data_description`
```python
>>> entry.data_description.axes.E.reference
'RHE'
```

The data can be visualized in a plotly figure, with preferred axis units (default is SI):

```python
>>> entry.plot(xunit='V', yunit='original')
```
<!-- ![doc/images/readme_demo_plot.png](doc/images/readme_demo_plot.png)-->
<img src=doc/images/readme_demo_plot.png style="width:400px">


# License

The contents of this repository are licensed under the [GNU General Public
License v3.0](./LICENSE) or, at your option, any later version.  The contents
of [data/](./data/) and [literature/](./literature/) are additionally licensed
under the [Creative Commons Attribution 4.0 International
License](https://creativecommons.org/licenses/by/4.0/).
