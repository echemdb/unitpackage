---
jupytext:
  formats: md:myst,ipynb
  text_representation:
    extension: .md
    format_name: myst
    format_version: 0.13
    jupytext_version: 1.14.5
kernelspec:
  display_name: Python 3 (ipykernel)
  language: python
  name: python3
---

# Usage

Here we present the interaction of collections and entries created with `unitpackage` from specifically designed [datapackages](unitpackage.md).

## Collection Interaction

A collection can be generated from a [remote](../api/remote.md) or a [local](../api/local.md) source.

To illustrate the usage of `unitpackage`, we create a collection from the entries on [echemdb.org](https://www.echemdb.org):

```{code-cell} ipython3
from unitpackage.collection import Collection
db = Collection()
```

Type `db` to highlight the entries within the collection or show the number of entries in the collection with.

```{code-cell} ipython3
len(db)
```

You can iterate over these entries

```{code-cell} ipython3
next(iter(db))
```

The collection can be filtered for specific descriptors,
wherby a new collection is created.

```{code-cell} ipython3
filtered_db = db.filter(lambda entry: entry.experimental.tags == ['BCV','HER'])
len(filtered_db)
```

## Entry Interaction

Each entry consists of descriptors describing the data in the resource of the datapackage. Packages describing literature data can also contain a bibliography reference (see [Bibliography](bibliography.md)). The entry also has additional methods for descriptor representation, data manipulation and data visualization.

### Entry Creation

An entry can be created from a local package:

```{code-cell} ipython3
from unitpackage.local import collect_datapackages
from unitpackage.entry import Entry
local_entry = Entry(collect_datapackages('../files/')[2])
local_entry
```

Single entries can also be selected by their identifier from a collection. For our example database such identifiers can directly be inferred from [echemdb.org](https://www.echemdb.org) for each entry.

```{code-cell} ipython3
entry = db['engstfeld_2018_polycrystalline_17743_f4b_1']
entry
```

### Accessing Resource Metadata

The metadata associated with the resource is located in `db.package.get_resource('echemdb').custom['metadata']`.
From an `entry` such information can be retrieved by `entry['name']`,
where name is the respective descriptor in the metadata descriptor. Alternatively you can write `entry.name`
where all spaces should be replaced by underscores.

```{code-cell} ipython3
entry = db['engstfeld_2018_polycrystalline_17743_f4b_1']
entry['source']['citation key']
```

```{code-cell} ipython3
entry.source.citation_key
```

`entry.package` provides a full list of available descriptors.

+++

### Units and values

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

(data)=
### Accessing Data

The datapackage consists of two resources.

* The first resource has the entry's identifier as name. It describes the data in the CSV.
* The second resource is named "echemdb". It contains the data as a pandas dataframe used by the unitpackage module (see [Unitpackage Structure](unitpackage.md) for more details.

```{note}
The content of the CSV never changes unless it is explicitly overwritten.
Changes to the data with the unitpackage module are only applied to the `echemdb` resource.
```

```{code-cell} ipython3
entry.package.resource_names
```

The data can be returned as a pandas dataframe.

```{code-cell} ipython3
entry.df.head()
```

The description of the fields (column names) including units and/or other infromation are included in the resource schema.

```{code-cell} ipython3
entry.package.get_resource('echemdb').schema
```

The units of the dataframe can be rescaled.

```{code-cell} ipython3
rescaled_entry = entry.rescale({'t' : 'h', 'E': 'mV', 'j' : 'uA / cm2'})
rescaled_entry.df.head()
```

The units are updated in the package schema of the 'echemdb' resource.

```{code-cell} ipython3
rescaled_entry.package.get_resource('echemdb').schema
```

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

## Bibliography interaction

An entry can be associated with bibliography data. The bibliography must must be prvided as abibtex string nested in source.bib_data. The bibliography to all entries is stored as a [pybtex database](https://docs.pybtex.org/api) `db.bibliography`,
which contains bibtex entries.

```{code-cell} ipython3
len(db.bibliography.entries)
```

Each entry in the echemdb databse can be cited.

```{code-cell} ipython3
entry.citation(backend='text') # other available backends: 'latex' or 'markdown'. 'text' is default.
```

Individual `db.bibliography` entries can be accessed with the citation key associated with a unitpackage entry.

```{code-cell} ipython3
bibtex_key = entry.source.citation_key
bibtex_key
```

```{code-cell} ipython3
citation_entry = db.bibliography.entries[bibtex_key]
citation_entry
```

Individiual `fields` are accessible, such as `year` or `title`.

```{code-cell} ipython3
citation_entry.fields['year']
```

```{code-cell} ipython3
citation_entry.fields['title']
```

The authors are accessible via `persons`. Read more in the [pybtex documentation](https://docs.pybtex.org/api/parsing.html?highlight=persons#pybtex.database.Entry.persons).

```{code-cell} ipython3
citation_entry.persons['author']
```

```{code-cell} ipython3
citation_entry.persons['author'][0]
```

```{code-cell} ipython3
print(citation_entry.persons['author'][0])
```
