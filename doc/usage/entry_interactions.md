---
jupyter:
  jupytext:
    cell_metadata_filter: tags,-all
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

# Entry interactions

<!-- #endregion -->

Each entry consits of a number of decsriptors containing metadata describing the entry, imported from the YAML files associated with the digitized data. For reference, the YAML files are located in the respective literature folders in the repository.

* `source`: details on the respective publication and the figure from which the data was generated
* `figure_description`: details about the original axis properties and other measurements linked to the published data
* `data_description`: details on the axes properties of the associated CSV files
* `electrochemical_system`: experimental details on the underlying electrochemical system

The underlying information can be retrieved by `entry.name` or `entry['name']`, where name is the respective descriptor.

```python
from echemdb.data.cv.database import Database
db = Database()
entry = db['alves_2011_electrochemistry_6010_p2_f2a_solid']
entry
```

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

## Units and values

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

## Basic interactions

<!-- #endregion -->

```python
entry.electrochemical_system.electrodes.working_electrode.material == 'Pt'
```

```python
entry.source
```

## Dataframes

```python

```

## Plots

```python

```
