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

# Unitpackage Structure

The `unitpackage` extends the Python API of the [frictionless framework](https://framework.frictionlessdata.io/).
To create a `unitpackage` entry or a `unitpackage` collection a frictionless datapackages must have a certain structure or follow a certain schema. We briefly illustrate the structure of the frictionless datapackages, describe which changes were necessary to adopt the schema to scientific data, and describe the structure of the datapackage for use with `unitpackage`.

## Frictionless Datapackage

The description of the frictionless datapackage presented here, is based on adapted examples found in the [frictionless documentation](https://specs.frictionlessdata.io/tabular-data-package/#language).

A minimal datapackage in your file system consists of two files:

```sh .noeval
data.csv
datapackage.json
```

The CSV file contains some data. For the unitpackge we focus on CSV files which contain numbers. Such data is usually found in natural sciences.

```sh .noeval
var1,var2,var3
1,2.1
3,4.5
```

In the corresponding JSON file the data in the CSV is described in a resource.

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

Tabular scientific data are often time series data, where one or more properties are recorded over a certain time scale, such as the temperature $T$ or pressure $p$ in a laboratory. In some cases one variable is changed with time and one or more variables are recorded to observe the change induced to a system. This could, for example, be the change in current $I$ in a load by varying a voltage $V$.

A CVS contains the underlying data.

```sh .noeval
t,U,I
1,2.1
3,4.5
```

```{warning}
The `unitpackage` currently only supports CSV files with a single header line. CSV files with headers, including additional information must be converted before. (see #23)
```

The units are often not included in the filed/column names. These can be included in the datapackage in the resource schema.

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

Additional metadata describing the underlying data or its origin is stored in the resource `metadata` descriptor. The `metadata` can contain a list with metadata descriptors following different kinds of metadata schemas. This allows storing metadata in different formats or from different sources.

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
The `unitpackage` module currently only provides direct access to the resource metadata stored within the `echemdb` descriptor. (see #20)
```

The above example can be found [here](https://raw.githubusercontent.com/echemdb/unitpackage/main/doc/files) named `demo_package_metadata`. To demonstrate how the different properties of the datapackage can be accessed we load the specific entry.

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
entry.package.get_resource("demo_package_metadata").custom["metadata"]["generic"]
```

## Unitpackage Interface

Upon closer inspection of the entry created with `unitpackage` you notice that it actually contains two resources.

```{code-cell} ipython3
entry.package
```

One resource is named according to the CSV filename. The units provided in that resource are describing the data within that CSV.

The second resource is called `unitpackage_resource`. It is created upon loading a datapackage with the `unitpackage` module and stores the data of the CSV as a pandas dataframe. The dataframe is directly accessible from the entry and shows the data from the `unitpackage_resource` resource. Upon loading the data, both the numbers and units in the CSV and pandas dataframe are identical.

```{code-cell} ipython3
entry.df.head(3)
```

The reason for the separation into two resources is as follows. With unitpackage we can transform the values within the dataframe to new units. This process leaves the data in CSV unchanged. The pandas dataframe in turn is adapted, as well as the units of the different fields of the `unitpackage_resource` resource.

```{code-cell} ipython3
rescaled_entry = entry.rescale({'U': 'V', 'I': 'mA'})
rescaled_entry.df.head(3)
```

```{code-cell} ipython3
rescaled_entry.package.get_resource('unitpackage_resource')
```

Refer to the [usage section](unitpackage_usage.md) for a more detailed description of the `unitpackage` API.
