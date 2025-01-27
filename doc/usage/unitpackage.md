---
jupytext:
  formats: md:myst,ipynb
  text_representation:
    extension: .md
    format_name: myst
    format_version: 0.13
    jupytext_version: 1.16.1
kernelspec:
  display_name: Python 3 (ipykernel)
  language: python
  name: python3
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

The CSV file contains some data. For the unitpackge we focus on CSV files containing only numbers.
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

A CVS contains the underlying data.

```sh .noeval
t,U,I
0,1,0
1,2,1
3,4,5
```

```{warning}
The `unitpackage` currently only supports CSV files with a single header line. CSV files with headers, including additional information must be converted before. (see #23)
```

The units are often not included in the filed/column names. These can be included in the Data Package in the field description of the resource schema.

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
            "type": "integer",
            "unit": "s"
          },
          {
            "name": "U",
            "type": "integer",
            "unit": "mV"
          },
          {
            "name": "I",
            "type": "integer",
            "unit": "uA"
          }
        ]
      }
    }
  ]
}
```

Additional metadata describing the underlying data or its origin is stored in the resource `metadata` descriptor. The `metadata` can contain a list with metadata descriptors following different kinds of metadata schemas. This allows metadata to be stored in different formats or from different sources.

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
                        "type": "integer",
                        "unit": "s"
                    },
                    {
                        "name": "U",
                        "type": "integer",
                        "unit": "mV"
                    },
                    {
                        "name": "I",
                        "type": "integer",
                        "unit": "uA"
                    }
                ]
            },
            "metadata": {
                "echemdb": {
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
                "generic": {
                    "description": "Sample data for the unitpackage module.",
                    "experimentalist": "John Doe",
                    "laboratory": "Institute of Good Scientific Practice",
                    "date recorded": "2021-07-09"
                }
            }
        }
    ]
}
```

```{warning}
The `unitpackage` module only provides direct access to the resource metadata stored within the `echemdb` descriptor. (see #20)
```

The above example can be found [here](https://raw.githubusercontent.com/echemdb/unitpackage/main/doc/files) named `demo_package_metadata`.
To demonstrate how the different properties of the resource can be accessed, we load the specific entry.

```{code-cell} ipython3
from unitpackage.collection import Collection

db = Collection.from_local('../files/')
entry = db['demo_package_metadata']
entry
```

The keys within the `echemdb` metadata descriptor are directly accessible as properties from the main `entry`.

```{code-cell} ipython3
entry.curation
```

Other metadata schemas are currently only accessible via the frictionless framework.

```{code-cell} ipython3
entry.resource.custom["metadata"]["generic"]
```

## Unitpackage Interface

A Collection consists of entries, which are resources collected from Data Packages.

Upon closer inspection of the entry created with `unitpackage`, you notice that an additional resource `MutableResource` is included in the original resource.

```{code-cell} ipython3
entry.resource
```

The main resource is named according to the CSV filename. The units provided in that resource describe the data within that CSV.

The included `MutableResource`, is created once the data is loaded. In case of tabular data, a pandas dataframe resource is created.
The dataframe is directly accessible from the entry and shows the data from the `MutableResource`.
Upon loading the data, both the numbers and units in the CSV and pandas dataframe are identical.

```{code-cell} ipython3
entry.df.head(3)
```

The reason for the separation into two resources is as follows.
With unitpackage we can, for example, transform the values within the dataframe to new units.
This process leaves the data in the original CSV unchanged.
The pandas dataframe resource, in turn, is adapted, as well as the units of the different fields of the `MutableResource` resource.

```{code-cell} ipython3
rescaled_entry = entry.rescale({'U': 'V', 'I': 'mA'})
rescaled_entry.df.head(3)
```

```{code-cell} ipython3
rescaled_entry.mutable_resource
```

Refer to the [usage section](unitpackage_usage.md) for a more detail description of the `unitpackage` API.
