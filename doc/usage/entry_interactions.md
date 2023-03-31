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

Each entry consists of

1. descriptors describing the data in the datapackage.
2. a bibliography reference (see [Bibliography](bibliography.md)).
3. functions for descriptor representation, data manipulation and data visualization.

## Basic interactions

The underlying information can be retrieved by `entry['name']`,
where name is the respective descriptor. Alternatively you can write `entry.name`
where all spaces should be replaced by underscores.

```{code-cell} ipython3
from echemdb.cv.cv_database import CVDatabase
db = CVDatabase()
entry = db['engstfeld_2018_polycrystalline_17743_f4b_1']
entry
```

```{code-cell} ipython3
entry['source']
```

```{code-cell} ipython3
entry.source
```

```{code-cell} ipython3
entry.source.citation_key
```

Specific information can be retrieved by selecting the desired descriptor

```{code-cell} ipython3
entry.system.electrodes.working_electrode.material
```

`entry.package` provides a full list of available descriptors including the `echemdb` resource ([see below](#data)).

+++ {"tags": []}

## Data

The datapackage consists of two resources.

* The first resource has the entry's identifier as name. It describes the data in the CSV.
* The second resource is named "echemdb". It contains the data used by the echemdb module.

```{note}
The content of the CSV never changes unless it is explicitly overwritten.
Changes to the data with the echemdb module are only applied to the `echemdb` resource.
```

```{code-cell} ipython3
entry.package.resource_names
```

The data can be returned as a pandas dataframe.

```{code-cell} ipython3
entry.df.head()
```

The units (and possible reference potentials) of the data are included in the resource schema.

```{code-cell} ipython3
entry.package.get_resource('echemdb').schema
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

<!--
The following line should read
original_entry = rescaled_entry.rescale('original')

However, the conversion does not seem to work, when the entry was rescaled before. (see #53)
-->
```{code-cell} ipython3
original_entry = entry.rescale('original')
original_entry.df.head()
```

The units (and possible reference potentials) of the data are included in the resource schema.

```{code-cell} ipython3
entry.figure_description.fields
```

+++ {"tags": []}

## Plots

The data can be visualized in a plotly figure.
The default plot is `j` vs. `E` (or `I` vs. `E`).
The curve label consits of the figure number in the original publication followed by a unique identifier.

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

Entries containing both a unit and a value are returned as [astropy units or quantities](https://docs.astropy.org/en/stable/units/index.html).

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

```{todo}
add link to YAML Files and other resources related to data standardization.
```
