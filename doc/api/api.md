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

The `echemdb` module provides direct access to the database and the entries presented on the [EchemDB Website](https://echemdb.github.io/). 

A database can also be created from local files which have the same file structure.

<!-- #region tags=[] -->
## Installation
<!-- #endregion -->

<!-- #raw -->
<!-- Detailed installation instructions can be found elsewhere -->
<!-- #endraw -->

The repository can be downloaded from the [EchemDB Github Repostory](https://github.com/echemdb/website) or via


```sh .noeval
git clone git@github.com:echemdb/website.git
```


Install all dependencies


```sh .noeval  
cd website
conda env create --file environment.yml
```


Switch to the correct environment and install echemdb:


```sh .noeval  
conda actiavte echemdb
pip install -e .
```

<!-- #region tags=[] -->
## EchemDB Website content
<!-- #endregion -->

The content of [EchemDB Website](https://echemdb.github.io/) can be stored in a local database.

```python
from echemdb.data.cv.database import Database
db = Database()
```

### Database interaction


The number of entries in the databse

```python
len(db)
```

You can iterate over these entries

```python
next(iter(db))
```

The database can be filtered for specific descriptors (see below) which returns a new database.

```python
db_filtered = db.filter(lambda entry: entry.electrochemical_system.electrodes.working_electrode.material == 'Pt')
print(f'{len(db_filtered)} entries contain Pt as working electrode material.')
```

Single entries can be selected by their identifier provided on the [echemDB website](https://echemdb.github.io/) for each entry.

```python
entry = db['alves_2011_electrochemistry_6010_p2_f2a_solid']
entry
```

<!-- #region tags=[] -->
## Entry interactions
<!-- #endregion -->

Each entry consits of a number of decsriptors containing metadata describing the entry, imported from the YAML files associated with the digitized data. For reference, the YAML files are located in the respective literature folders in the repository.
* `source`: details on the respective publication and the figure from which the data was generated
* `figure_description`: details about the original axis properties and other measurements linked to the published data
* `data_description`: details on the axes properties of the associated CSV files
* `electrochemical_system`: experimental details on the underlying electrochemical system

The underlying information can be retrieved by `entry.name` or `entry['name']`, where name is the respective descriptor.

```python
entry['source']
```

```python
entry.source
```

Specific information can be retrieved by selecting the desired descriptor

```python
entry.electrochemical_system.electrodes.working_electrode.material
```

### Units and values
Entries containing a unit and a value are nicely rendered

```python
entry.figure_description.scan_rate
```

The unit and valule can be accessed separately

```python
entry.figure_description.scan_rate.value
```

```python
entry.figure_description.scan_rate.unit
```

All units are compatible with [astropy units](https://docs.astropy.org/en/stable/units/index.html) to create quantities and make simple unit transformations or multiplications with [astropy units](https://docs.astropy.org/en/stable/units/index.html) or [atropy constants](https://docs.astropy.org/en/stable/constants/index.html).

```python
from astropy import units as u
rate = entry.figure_description.scan_rate.value * u.Unit(entry.figure_description.scan_rate.unit)
rate
```

```python
type(rate)
```

```python
rate.to('mV / h')
```

```python
from astropy import constants as c # c: speed of light
rate * 25 * u.m * c.c
```

<!-- #region tags=[] -->
### Basic interactions
<!-- #endregion -->

```python
entry.electrochemical_system.electrodes.working_electrode.material == 'Pt'
```

```python
entry.source
```

### Dataframes

```python

```

### Plots


## Bibliography


The bibliography to all entries is stored as a pybtex database `db.bibliography`, which is based on bibtex entries.
Each entry has a citation key, which is not identical to its identifier (but is part of it), since several entries can be found in the same source.
Both the citation key and the pybtex bibliography entry are accessible from the entry. 

```python
entry.source.citation_key
```

```python
entry.bibliography
```

```python
The bibliography to the key is 
```

With that key the bibliography can be retrieved from the db.bibliography

```python
db.bibliography['alves_2011_electrochemistry_6010']
```

```python

```

```python
entry = db['alves_2011_electrochemistry_6010_p2_f2a_solid']
```

```python
entry.bibliography()
```

```python
entry.source.citation_key
```

```python

```

## Create database locally

```python
a = 1
a
```

```python
print(a)
```

```python
import pandas as pd
```

```python
'test'
```

```python

```
