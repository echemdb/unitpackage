---
jupytext:
  formats: md:myst,ipynb
  text_representation:
    extension: .md
    format_name: myst
    format_version: 0.13
    jupytext_version: 1.18.1
kernelspec:
  display_name: Python 3 (ipykernel)
  language: python
  name: python3
---

# echemdb

The electrochemical data shown on the [echemdb.org](https://www.echemdb.org/cv) website can be downloaded from the [echemdb data repository](https://github.com/echemdb/electrochemistry-data) and stored in a collection.

```{code-cell} ipython3
from unitpackage.database.echemdb import Echemdb
db = Echemdb.from_remote()
type(db)
```

## Collection

In contrast to the `Collection` object described in the [usage section](unitpackage_usage.md), `Echemdb` provides data specific functionality.
All other functionalities of the base class are still applicable.

For example, statistics of the collection can be shown.

```{code-cell} ipython3
db.describe()
```

## Metadata

The entries have properties which allow for more convenient filtering of the collection.

```{code-cell} ipython3
db_filtered = db.filter(lambda entry: entry.get_electrode('WE').material == 'Pt')
db_filtered.describe()
```

Single entries can be selected by their identifier provided on [echemdb.org/cv](https://www.echemdb.org/cv) for each entry.

```{code-cell} ipython3
entry = db['engstfeld_2018_polycrystalline_17743_f4b_1']
type(entry)
```

`entry.package` provides a full list of available descriptors.

As indicated above, electrodes used to record the data are listed in the `system.electrodes` descriptor and are accessible with

```{code-cell} ipython3
entry.get_electrode('WE')
```

```{note}
Usually measurements are performed in a three electrode configuration, with a working electrode `WE`, a counter electrode `CE`, and a reference electrode `REF`.
```

## Data

In a freshly created collection all values of in the dataframe are in SI units.

```{code-cell} ipython3
entry.df.head(5)
```

The original units in the published figure are stored as metadata.
For data digitized with [svgdigitizer](https://echemdb.github.io/svgdigitizer/) a time axis is only present, when a scan rate was given in the SVG.

```{code-cell} ipython3
entry.figureDescription.fields
```

```{code-cell} ipython3
entry.figureDescription.scanRate
```

### Changing column units

+++

An entry can be rescaled to new units.

```{code-cell} ipython3
rescaled_entry = entry.rescale({'E': 'mV', 'j': 'A / m2' })
rescaled_entry.df.head(5)
```

The information is updated in the field description of the mutable resource.

```{code-cell} ipython3
rescaled_entry.mutable_resource.schema
```

An entry can be rescaled to its original units.

```{code-cell} ipython3
original_entry = rescaled_entry.rescale('original')
original_entry.df.head(5)
```

The information in the mutable resource is updated accordingly.

```{code-cell} ipython3
original_entry.mutable_resource.schema
```

### Shifting reference scales

A key issue for comparing electrochemical current potential traces is that data can be recorded with different reference electrodes. Hence direct comparison of the potential data is not straight forward unless the data is shifted to a common reference scale. The shift to a different reference scale depends on how the value of that reference electrode vs the standard hydrogen electrode (SHE) is determined and sometimes depends on the source of the reported data. 

#### Separate consideration

To mitigate this issue, the `unitpackage.electrochemistry.reference_electrode` module, contains a collection of commonly used reference electrodes that can be accessed by its API.

```{code-cell} ipython3
from unitpackage.electrochemistry.reference_electrode import _reference_electrodes

_reference_electrodes.keys()
```

A `ReferenceElectrode` object can be created by providing the corresponding acronym.

```{code-cell} ipython3
from unitpackage.electrochemistry.reference_electrode import ReferenceElectrode

ref = ReferenceElectrode('CE-sat')
ref
```

A certain `ReferenceElectrode` can contain multiple entries with values from different sources. For the echemdb standard data values were chosen based on the discussion of the specified reference electrodes in the literature.

```{code-cell} ipython3
ref.standard_data
```

The shift a certain reference electrode vs that of another known reference electrode can be inferrred. 
The resulting value is always in `V`!

```{code-cell} ipython3
ref.shift(to='CE-1M')
```

The shift can also be calculated for a specific potential.

```{code-cell} ipython3
ref.shift(to='CE-1M', potential = 0.564)
```

For conversion to and from the RHE scale, the pH is required.

```{code-cell} ipython3
ref.shift(to='RHE', potential = 0.564, ph=13)
```

#### unitpackage implementation

If the reference scale is given for a certain entry, the potentials can directly be shifted

```{code-cell} ipython3
entry_mse = entry.rescale_reference('MSE-sat')
entry_mse.df.head()
```

If a pH value is provided in the metadata, conversion to RHE is straight forward. In other cases the pH must be provide as additional argument.

```{code-cell} ipython3
entry.system.electrolyte.ph
```

```{code-cell} ipython3
entry.get_electrode('REF')
```

```{code-cell} ipython3
entry.df.head()
```

```{code-cell} ipython3
entry_rhe = entry.rescale_reference('SHE')
entry_rhe.df.head()
```

## Plotting

The default plot to present the data is `j` vs. `E` (or `I` vs. `E`).
The curve label consists of the figure number in the original publication followed by a unique identifier.

```{code-cell} ipython3
entry.plot()
```

The dimensions of the axis can still be specified explicitly.

```{code-cell} ipython3
entry.plot(x_label='t', y_label='j')
```

## Bibliography

All entries within the `Echemdb` collection are referenced and included in a bibtex bibliography.

```{code-cell} ipython3
len(db.bibliography.entries)
```

Each entry in the `Echemdb` collection can be cited.

```{code-cell} ipython3
entry = db['engstfeld_2018_polycrystalline_17743_f4b_1']
entry.citation(backend='text') # other available backends: 'latex' or 'markdown'. 'text' is default.
```
