---
jupytext:
  cell_metadata_filter: tags,-all
  formats: ipynb,md:myst
  text_representation:
    extension: .md
    format_name: myst
    format_version: 0.13
    jupytext_version: 1.13.7
kernelspec:
  display_name: Python 3 (ipykernel)
  language: python
  name: python3
---

# Entry interactions

<!-- #endregion -->

```{todo}
* add link to YAML Files and other resources related to data standardization.
```

Each entry consits of decsriptors with metadata describing the entry, wmong those:

* `source`: details on the respective publication and the figure from which the data was generated.
* `figure description`: details about the original figures axis properties and other measurements linked to the published data.
* `data description`: details on the axes properties of the associated CSV files.
* `electrochemical system`: experimental details on the underlying electrochemical system.

## Basic interactions

The underlying information can be retrieved by `entry['name']`, 
where name is the respective descriptor. Alternatively you can write `entry.name` 
where all spaces should be replaced by underscores.

```{code-cell} ipython3
from echemdb.data.cv.database import Database
db = Database()
entry = db['alves_2011_electrochemistry_6010_p2_f2a_solid']
entry
```

```{code-cell} ipython3
entry['source']
```

```{code-cell} ipython3
entry.source
```

Specific information can be retrieved by selecting the desired descriptor

```{code-cell} ipython3
entry.electrochemical_system.electrodes.working_electrode.material
```

## Units and values

Entries containing a unit and a value are nicely rendered

```{code-cell} ipython3
entry.figure_description.scan_rate
```

The unit and value can be accessed separately

```{code-cell} ipython3
entry.figure_description.scan_rate.value
```

```{code-cell} ipython3
entry.figure_description.scan_rate.unit
```

All units are compatible with [astropy units](https://docs.astropy.org/en/stable/units/index.html) to create quantities and make simple unit transformations or multiplications with [astropy units](https://docs.astropy.org/en/stable/units/index.html) or [atropy constants](https://docs.astropy.org/en/stable/constants/index.html).

```{code-cell} ipython3
from astropy import units as u
rate = entry.figure_description.scan_rate.value * u.Unit(entry.figure_description.scan_rate.unit)
rate
```

```{code-cell} ipython3
type(rate)
```

```{code-cell} ipython3
rate.to('mV / h')
```

```{code-cell} ipython3
from astropy import constants as c # c: speed of light
rate * 25 * u.m * c.c
```

+++ {"tags": []}

## Dataframes

The data of an entry can be returned a pandas dataframe.

```{code-cell} ipython3
entry.df().head(3)
```

Custom or original figure axes' units can be requested explicitly

```{code-cell} ipython3
entry.df(xunit='original', yunit='mA / m2').head(3)
```

## Plots

The data can be visualized in a plotly figure, with preferred axis units (default is SI):

```{code-cell} ipython3
entry.plot(xunit='V', yunit='original')
```
