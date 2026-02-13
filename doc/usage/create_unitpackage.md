---
jupytext:
  formats: ipynb,md:myst
  text_representation:
    extension: .md
    format_name: myst
    format_version: 0.13
    jupytext_version: 1.17.3
kernelspec:
  display_name: Python (Pixi)
  language: python
  name: pixi-kernel-python3
---

# Creating Unitpackages

[Unitpackages](unitpackage.md) (frictionless Data Packages with unit-annotated fields and additional metadata describing the data) can be created from CSV files or pandas DataFrames.
After creation, metadata and field descriptions (including units) can be added to produce a complete, self-describing data package.

## Quick start

A typical workflow to create a complete unitpackage from a CSV file involves:

1. Creating an entry from the [CSV](#from-a-csv-file) or [pandas DataFrame](#from-a-pandas-dataframe)
2. [Adding metadata](#adding-metadata)
3. [Adding field descriptions](#adding-field-descriptions) (units)
4. Saving the result

```{code-cell} ipython3
from unitpackage.entry import Entry

# 1. Create entry from CSV
entry = Entry.from_csv(csvname="../files/demo_package.csv")

# 2. Load metadata from a YAML file
entry = entry.load_metadata("../files/demo_package.csv.yaml")

# 3. Update field descriptions (units)
fields = [{'name': 't', 'unit': 's'}, {'name': 'j', 'unit': 'A / cm2'}]
entry = entry.update_fields(fields=fields)

# 4. Save
entry.save(outdir="../generated/files/csv_entry/")
```

The saved entry now consists of a CSV and a JSON file in the output directory.

```{code-cell} ipython3
import os
os.listdir("../generated/files/csv_entry/")
```

The following sections describe each step in more detail.

## From a CSV file

An entry can be created directly from a CSV file.

```{code-cell} ipython3
from unitpackage.entry import Entry

entry = Entry.from_csv(csvname="../files/demo_package.csv")
entry
```

The entry's field descriptions are inferred from the CSV.

```{code-cell} ipython3
entry.fields
```

The data can be accessed as pandas dataframe

```{code-cell} ipython3
entry.df.head()
```

or from the resource data

```{code-cell} ipython3
entry.resource.schema.to_dict()
```

## From a pandas DataFrame

Similarly, an entry can be created from a pandas DataFrame.
A `basename` must be provided to name the entry.

```{code-cell} ipython3
import pandas as pd
from unitpackage.entry import Entry

data = {'x': [1, 2, 3], 'v': [1, 3, 2]}
df = pd.DataFrame(data)

entry = Entry.from_df(df, basename='df_data')
entry
```

## Adding field descriptions

Field descriptions such as units can be added or updated using `update_fields()`.
Only fields with matching names are updated; non-matching fields are ignored.

```{code-cell} ipython3
fields = [{'name': 'x', 'unit': 'm'}, {'name': 'v', 'unit': 'm / s', 'description': 'velocity'}]
entry = entry.update_fields(fields=fields)
entry.fields
```

```{note}
`update_fields()` returns a **new** entry — the original entry is not modified.
```

## Adding metadata

Metadata can be added to an entry in several ways.

### From a Python dictionary

```{code-cell} ipython3
entry.metadata.from_dict({'experimentInfo': {'user': 'Max Doe', 'date': '2021-07-09'}})
entry.metadata
```

### From a YAML or JSON file

Metadata can be loaded from a YAML file using `load_metadata()`, which supports method chaining.

```{code-cell} ipython3
entry = Entry.from_csv(csvname="../files/demo_package.csv")
entry = entry.load_metadata("../files/demo_package.csv.yaml")
entry.metadata
```

A `key` can be specified to store the loaded metadata under a specific key.
This is useful when metadata should be organized according to a certain schema, keeping different metadata sources separated.
See the [unitpackage structure description](unitpackage.md) for more details on how metadata schemas are organized within a resource.

```{code-cell} ipython3
entry = Entry.from_csv(csvname="../files/demo_package.csv")
entry = entry.load_metadata("../files/demo_package.csv.yaml", key="experiment")
entry.metadata['experiment']
```

The same works with a JSON file — the format is auto-detected from the file extension.

```{code-cell} ipython3
entry = Entry.from_csv(csvname="../files/demo_package.csv")
entry = entry.load_metadata("../files/demo_package.json", key="source")
entry.metadata['source']
```

```{note}
`metadata.from_dict()`, `metadata.from_yaml()`, and `metadata.from_json()` modify the entry's metadata **in-place**.
In contrast, `load_metadata()` is a convenience method on the entry that returns `self` for method chaining.
```
