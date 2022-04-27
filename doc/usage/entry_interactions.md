---
jupytext:
  cell_metadata_filter: tags,-all
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

# Entry interactions

<!-- #endregion -->

```{todo}
* add link to YAML Files and other resources related to data standardization.
```

Each entry consits of decsriptors with metadata describing the entry, among those:

* `source`: details on the respective publication and the figure from which the data was generated.
* `figure description`: details about the original figures axis properties and other measurements linked to the published data.
* `system`: experimental details on the underlying electrochemical system.

## Basic interactions

The underlying information can be retrieved by `entry['name']`, 
where name is the respective descriptor. Alternatively you can write `entry.name` 
where all spaces should be replaced by underscores.

```{code-cell} ipython3
from echemdb.cv.database import Database
db = Database()
entry = db['alves_2011_electrochemistry_6010_f1a_solid']
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
entry.system.electrodes.working_electrode.material
```

+++ {"tags": []}

## Data

The datapackage consists of two resources. 
* The first resource has the entry's identifier as name. It describes the data in the CSV.
* The second resource is named "echemdb". It contains the data used by the echemdb module.

```{code-cell} ipython3
entry.package.resource_names
```

The data can be returned as a pandas dataframe.

```{code-cell} ipython3
entry.df.head()
```

The units (and possible reference potentials) of the data are included in the resource schema.

```{code-cell} ipython3
entry.package.get_resource('echemdb')['schema']
```

The units of the dataframe can be rescaled.

```{code-cell} ipython3
rescaled_entry = entry.rescale({'t' : 'h', 'E': 'mV', 'j' : 'uA / cm2'})
rescaled_entry.df.head()
```

The units of a field are directly accessible via 

```{code-cell} ipython3
rescaled_entry.field_unit('E')
```

The dataframe can be restored to the original figure axes' units of the published figure.

```{code-cell} ipython3
original_entry = rescaled_entry.rescale('original')
original_entry.df.head()
```

The units (and possible reference potentials) of the data are included in the resource schema.

```{code-cell} ipython3
entry.figure_description.fields
```

+++ {"tags": []}

## Plots

The data can be visualized in a plotly figure. The default plot is j vs. E (or I vs. E)

```{code-cell} ipython3
entry.plot()
```

A plot with rescaled axis is obtained by rescaling the entry first.

```{code-cell} ipython3
entry.rescale({'E':'mV', 'j':'uA / cm2'}).plot()
```

The dimensions of the axis can be specified explicitly.

```{code-cell} ipython3
entry.plot(x_label='t', y_label='j')
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
