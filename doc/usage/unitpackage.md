---
jupytext:
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

# Unitpackage Structure

To create a `unitpackage` entry or a `unitpackage` collection, the frictionless datapackages must have a certain structure or follow a certain schema. We briefly illustrate the structure of the frictionless datapackages, describe which changes were necessary to adopt the schema to scientific data, and describe the structure of the datapackage for use with `unitpackage`.

## Frictionless Datapackage

To understand the unitpackage structure (not the module), we briefly highlight key properties of the frictionless datapackage, based on adapted examples found in the frictionless documentation.

A minimal datapackage in your file system consists of two files:

```sh
data.csv
datapackage.json
```

The CSV file contains some data, where we focus on data which can have a unit. Such data is usually found in natural sciences.

```csv
var1,var2,var3
1,2.1
3,4.5
```

The corresponding JSON file, describes the data in the CSV.

```json
{
  "profile": "tabular-data-package",
  "name": "my-dataset",
  // here we list the data files in this dataset
  "resources": [
    {
      "path": "data.csv",
      "name": "data",
      "profile": "tabular-data-resource",
      "schema": {
        "fields": [
          {
            "name": "var1",
            "type": "string"
          },
          {
            "name": "var2",
            "type": "integer"
          },
          {
            "name": "var3",
            "type": "number"
          }
        ]
      }
    }
  ]
}
```

A frictionless datapackage can have multiple resources.

```json
{
  "profile": "tabular-data-package",
  "name": "my-dataset",
  // here we list the data files in this dataset
  "resources": [
    {
      "path": "data.csv",
      "name": "data",
      "profile": "tabular-data-resource",
      "schema": {
        "fields": [
          ...
        ]
      }
    },
    {
      "path": "data2.csv",
      "name": "data2",
      "profile": "tabular-data-resource",
      "schema": {
        "fields": [
          ...
        ]
      }
    }
  ]
}
```

## Requirements for Scientific Data

Tabular Scientific data are often so called time series data, where one or more properties are recorded over a certain time scale, such as the temperature $T$ or pressure $p$ in a laboratory. It some cases one variable is changed with time and one or more variables are recorded based on the induced changes, such as measuring the change in current $I$ in a load by varying a voltage $V$.

A CVS contains the underlying data but unfortunately often not the units.

```csv
t,U,I
1,2.1
3,4.5
```

The units are at this point usually unknown, but they can be included in the datapackage in the resource schema.

```{note}
The units should be provided as following the [astropy unit](https://docs.astropy.org/en/stable/units/index.html) notation.
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
            "type": "string",
            "unit": "s"
          },
          {
            "name": "U",
            "type": "integer",
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

Additional metadata describing the underlying data or its origin is stored in the resource `metadata` key. The `metadata` can contain a list with metadata objects following different kinds of metadata schemas.

```json
{
    "resources": [
        {
            "name": "demo_package",
            "type": "table",
            "path": "demo_package.csv",
            "scheme": "file",
            "format": "csv",
            "mediatype": "text/csv",
            "encoding": "utf-8",
            "schema": {
                "fields": [
                    {
                        "name": "t",
                        "type": "string",
                        "unit": "s"
                    },
                    {
                        "name": "U",
                        "type": "integer",
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
The `unitpackage` module currently provides direct access to metadata stored within the key `echemdb`.
```

The above example can be found [here](https://raw.githubusercontent.com/echemdb/unitpackage/main/doc/files) names `demo_package_metadata`. To demonstrate how the different properties of the datapackage can be accessed we load the specific entry.

```{code-cell} ipython3
from unitpackage.collection import Collection
from unitpackage.local import collect_datapackages
db = Collection(data_packages=collect_datapackages('./doc/files'))
entry = db['demo_package_metadata']
entry
```
