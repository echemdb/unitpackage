---
jupytext:
  formats: md:myst,ipynb
  text_representation:
    extension: .md
    format_name: myst
    format_version: 0.13
    jupytext_version: 1.18.1
kernelspec:
  name: python3
  display_name: Python 3 (ipykernel)
  language: python
---

# Usage

The `unitpackage` module allows interacting with collections and entries from specifically designed frictionless [Data Packages](unitpackage.md).

## Collection

A collection can be generated from a [remote](../api/remote.md) or a [local](../api/local.md) source.

To illustrate the usage of `unitpackage`, we create a collection from the entries shown on [echemdb.org](https://www.echemdb.org/cv),
which are retrieved from the [data repository](https://github.com/echemdb/electrochemistry-data):

```{code-cell} ipython3
from unitpackage.collection import Collection
db = Collection.from_remote()
```

Type `db` to highlight the entries within the collection or show the number of entries in the collection with.

```{code-cell} ipython3
len(db)
```

The identifiers can also be returned as a list.

+++

### Slice the collection

```{code-cell} ipython3
db.identifiers[0:3]
```

A new collection from an existing collection can be created from a list of selected identifiers

```{code-cell} ipython3
ids_db = db['engstfeld_2018_polycrystalline_17743_f4b_1','alves_2011_electrochemistry_6010_f1a_solid']
ids_db
```

a list of indices

```{code-cell} ipython3
ids_db = db[0,1]
ids_db
```

or a slice.

```{code-cell} ipython3
sliced_db = db[:2]
sliced_db
```

You can iterate over these entries

```{code-cell} ipython3
next(iter(db))
```

The collection can be filtered for specific descriptors,
whereby a new collection is created.

+++

### Filter the collection

```{code-cell} ipython3
filtered_db = db.filter(lambda entry: entry.echemdb.experimental.tags == ['BCV','HER'])
len(filtered_db)
```

Alternatively parse a custom filter.

```{code-cell} ipython3
def custom_filter(entry):
    for component in entry.echemdb.system.electrolyte.components:
        if 'ClO4' in component.name:
            return True
    return False

filtered_db = db.filter(custom_filter)
len(filtered_db)
```

## Entry

Each entry consists of descriptors describing the data in the resource of the datapackage.
The entry also has additional methods for descriptor representation, data manipulation, and data visualization.

Entries can be selected by their identifier from a collection. For our example database, such identifiers can directly be inferred from [echemdb.org/cv](https://www.echemdb.org/cv) for each entry.

```{code-cell} ipython3
entry = db['engstfeld_2018_polycrystalline_17743_f4b_1']
entry
```

Entries can also be created from their position in the db.

```{code-cell} ipython3
entry_pos = db[0]
entry_pos
```

Other approaches to create entries from CSV or pandas dataframes directly are described [here](load_and_save.md).

### Metadata

The metadata associated with a unitpackage entry is accessible via `entry.metadata`.
From an `entry` such information can be retrieved by `entry['key']`,
where `key` is the respective top-level descriptor in the metadata.
Nested descriptors can be accessed with chained bracket or attribute-style access.

```{code-cell} ipython3
entry = db['engstfeld_2018_polycrystalline_17743_f4b_1']
entry['echemdb']['source']['citationKey']
```

```{code-cell} ipython3
entry.echemdb.source.citationKey
```

`entry.metadata` provides a full list of available descriptors. See [Creating Unitpackages](create_unitpackage.md) for details on how to load and modify metadata.

+++

### Units and values

Entries containing both a unit and a value are returned as [astropy units or quantities](https://docs.astropy.org/en/stable/units/index.html).

```{code-cell} ipython3
entry.echemdb.figureDescription.scanRate
```

The unit and value can be accessed separately

```{code-cell} ipython3
entry.echemdb.figureDescription.scanRate.value
```

```{code-cell} ipython3
entry.echemdb.figureDescription.scanRate.unit
```

(data)=
### Data

The data can be returned as a pandas dataframe.

```{code-cell} ipython3
entry.df.head()
```

The description of the fields (column names) including units and/or other information are accessible via `entry.fields`.

```{code-cell} ipython3
entry.fields
```

### Data manipulation

+++

The units of the dataframe can be rescaled to different convertible units.

```{code-cell} ipython3
rescaled_entry = entry.rescale({'t' : 'h', 'E': 'mV', 'j' : 'uA / cm2'})
rescaled_entry.df.head()
```

The units are updated in the field descriptions.

```{code-cell} ipython3
rescaled_entry.fields
```

An offset can be applied to a certain axis.

```{code-cell} ipython3
offset_entry = entry.add_offset('E', 0.32, 'V')
offset_entry.df.head()
```

The offset is indicated in the field descriptions. For subsequent offsets, the value is updated.

```{code-cell} ipython3
offset_entry.resource.schema.get_field('E')
```

To add a computed column with proper field descriptions, use `entry.add_columns()`.
This ensures that the field metadata (such as units) is tracked correctly.

```{code-cell} ipython3
import pandas as pd
import astropy.units as u

df = pd.DataFrame()
df['P/A'] = entry.df['E'] * entry.df['j']

new_field_unit = u.Unit(entry.field_unit('E')) * u.Unit(entry.field_unit('j'))
new_entry = entry.add_columns(df['P/A'], new_fields=[{'name':'P/A', 'unit': new_field_unit}])
new_entry.df.head()
```

The new field is now included in the field descriptions.

```{code-cell} ipython3
new_entry.fields
```

Columns can also be removed with `entry.remove_column()`.

```{code-cell} ipython3
reduced_entry = new_entry.remove_column('P/A')
reduced_entry.fields
```

```{code-cell} ipython3
reduced_entry.df.head()
```

### Column information

+++

The units of a specific field can be retrieved.

```{code-cell} ipython3
rescaled_entry.field_unit('E')
```

### Plotting

The data can be visualized in a plotly figure. Without providing the dimensions of the x any y labels specifically the first two columns are plotted against each other or you can specify the dimensions.

```{code-cell} ipython3
entry.plot()
```

The dimensions of the axis can be specified explicitly.

```{code-cell} ipython3
entry.plot(x_label='t', y_label='j')
```

A plot with rescaled axis is obtained by rescaling the entry first.

```{code-cell} ipython3
entry.rescale({'E':'mV', 'j':'uA / cm2'}).plot(x_label='t', y_label='j')
```

We can also use the matplotlib interface.

```{code-cell} ipython3
import matplotlib.pyplot as plt

fig, ax = plt.subplots(1,1)

x = 'E'
y = 'j'

entry.df.plot(x, y, ax=ax)
plt.title(entry.identifier)
ax.set_xlabel(f"{x} [{entry.field_unit(x)}]")
ax.set_ylabel(f"{y} [{entry.field_unit(y)}]")
```
