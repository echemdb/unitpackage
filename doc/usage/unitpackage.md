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

# Unitpackage Structure

The `unitpackage` extends the Python API of the [frictionless framework](https://framework.frictionlessdata.io/),
allowing for exploring frictionless resources extracted from frictionless Data Packages.
To create a `unitpackage` entry or a `unitpackage` collection, frictionless resources must have a specific structure or follow a certain schema. We briefly illustrate the structure of the frictionless Data Packages, describe which changes were necessary to adopt the schema to scientific data, and describe the structure of the datapackage for use with `unitpackage`.

## Frictionless Datapackage

The frictionless Data Package description is based on examples from the [frictionless documentation](https://specs.frictionlessdata.io/tabular-data-package/#language).

A minimal datapackage in your file system consists of two files:

```sh .noeval
data.csv
datapackage.json
```

The CSV file contains some data. For the unitpackage we focus on CSV files containing only numbers.
Such data is usually found in natural sciences.

```sh .noeval
var1,var2,var3
1,2,1
3,4,5
```

In the corresponding JSON file the data in the CSV is described in a resource.

```json
{
  "profile": "tabular-data-package",
  "name": "my-dataset",
  "resources": [
    {
      "path": "data.csv",
      "name": "data",
      "profile": "tabular-data-resource",
      "schema": {
        "fields": [
          {
            "name": "var1",
            "type": "integer"
          },
          {
            "name": "var2",
            "type": "integer"
          },
          {
            "name": "var3",
            "type": "integer"
          }
        ]
      }
    }
  ]
}
```

A frictionless Data Package can have multiple resources.

```json
{
  "profile": "tabular-data-package",
  "name": "my-dataset",
  "resources": [
    {
      "path": "data.csv",
      "name": "data",
      "profile": "tabular-data-resource",
      "schema": {
        "fields": [
            {
          "...":"..."
            }
        ]
      }
    },
    {
      "path": "data2.csv",
      "name": "data2",
      "profile": "tabular-data-resource",
      "schema": {
        "fields": [
            {
          "...":"..."
            }
        ]
      }
    }
  ]
}
```

## Requirements for Scientific Data

Tabular scientific data are often time series data, where one or more properties are recorded over a specific time scale, such as the temperature $T$ or pressure $p$ in a laboratory.
In some cases, one variable is changed with time, and one or more variables are recorded to observe the change induced to a system.
This could, for example, be the change in current $I$ in a load by varying a voltage $V$.

A CSV contains the underlying data.

```sh .noeval
t,U,I
0,1,0
1,2,1
3,4,5
```

```{note}
The `unitpackage` currently only supports CSV files with a single header line. CSV files with more complex header structures can be loaded using [device-specific loaders](loaders.md), which convert the data into the standard format.
```

The units are often not included in the field/column names. These can be included in the Data Package in the field description of the resource schema.

```{note}
We suggest providing the units according to the [astropy unit](https://docs.astropy.org/en/stable/units/index.html) notation.
```

```json
{
  "profile": "tabular-data-package",
  "name": "my-dataset",
  "resources": [
    {
      "path": "data.csv",
      "name": "data",
      "profile": "tabular-data-resource",
      "schema": {
        "fields": [
          {
            "name": "t",
            "type": "number",
            "unit": "s"
          },
          {
            "name": "U",
            "type": "number",
            "unit": "mV"
          },
          {
            "name": "I",
            "type": "number",
            "unit": "uA"
          }
        ]
      }
    }
  ]
}
```

Additional metadata describing the underlying data or its origin is stored in the resource `metadata` descriptor. The `metadata` can contain metadata descriptors following different kinds of metadata schemas. This allows metadata to be stored in different formats or from different sources, and also allows validation of the metadata subsets independently.

```json
{
    "resources": [
        {
            "name": "demo_package_metadata",
            "type": "table",
            "path": "demo_package_metadata.csv",
            "scheme": "file",
            "format": "csv",
            "mediatype": "text/csv",
            "encoding": "utf-8",
            "schema": {
                "fields": [
                    {
                        "name": "t",
                        "type": "number",
                        "unit": "s"
                    },
                    {
                        "name": "U",
                        "type": "number",
                        "unit": "mV"
                    },
                    {
                        "name": "I",
                        "type": "number",
                        "unit": "uA"
                    }
                ]
            },
            "metadata": {
                "genericSchema1": {
                    "description": "Sample data for the unitpackage module.",
                    "curation": {
                        "process": [
                            {
                                "role": "experimentalist",
                                "name": "John Doe",
                                "laboratory": "Institute of Good Scientific Practice",
                                "date": "2021-07-09"
                            }
                        ]
                    }
                },
                "genericSchema2": {
                    "description": "Sample data for the unitpackage module.",
                    "experimentalist": "John Doe",
                    "laboratory": "Institute of Good Scientific Practice",
                    "dateRecorded": "2021-07-09"
                }
            }
        }
    ]
}
```

The above example can be found [here](https://github.com/echemdb/unitpackage/tree/main/doc/files) named `demo_package_metadata`.
To demonstrate how the different properties of the resource can be accessed, we load the specific entry.

```{code-cell} ipython3
from unitpackage.collection import Collection

db = Collection.from_local('../files/')
entry = db['demo_package_metadata']
entry
```

The metadata of an entry is accessible via `entry.metadata`, which supports both dict-style and attribute-style access.

```{code-cell} ipython3
entry.metadata
```

The top-level keys of the metadata correspond to the different metadata schemas stored in the resource.
These keys are also directly accessible as attributes from the entry itself.

```{code-cell} ipython3
entry.genericSchema1.curation
```

```{code-cell} ipython3
entry.metadata['genericSchema2']
```

## Unitpackage Interface

A Collection consists of entries, which are resources collected from Data Packages.
The fields of the resource's schema describe the columns in the CSV, including their units.

```{code-cell} ipython3
entry.fields
```

The dataframe is directly accessible from the entry.

```{code-cell} ipython3
entry.df.head(3)
```

With `unitpackage` we can transform the values within the dataframe to new units.
This creates a new entry with rescaled data and updated field units, while leaving the original entry unchanged.

```{code-cell} ipython3
rescaled_entry = entry.rescale({'U': 'V', 'I': 'mA'})
rescaled_entry.df.head(3)
```

The updated units are reflected in the entry's fields.

```{code-cell} ipython3
rescaled_entry.fields
```

Refer to the [usage section](unitpackage_usage.md) for a more detailed description of the `unitpackage` API.
