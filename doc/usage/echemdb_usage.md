---
jupytext:
  formats: md:myst,ipynb
  text_representation:
    extension: .md
    format_name: myst
    format_version: 0.13
    jupytext_version: 1.17.2
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

An entry can be rescaled to these original units.

```{code-cell} ipython3
original_entry = entry.rescale('original')
original_entry.df.head(5)
```

```{code-cell} ipython3
original_entry.mutable_resource.schema
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
