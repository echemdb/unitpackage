---
jupytext:
  formats: ipynb,md:myst
  text_representation:
    extension: .md
    format_name: myst
    format_version: 0.13
    jupytext_version: 1.16.6
kernelspec:
  display_name: Python 3 (ipykernel)
  language: python
  name: python3
---

# Load and Save

`unitpackage` Entries and Collections can be loaded from different sources and stored as datapackages (CSV and JSON) to a specified output directory.

## Load collections

### From local files

A local collection of datapackages can be created by collecting datapackages recursively, which are stored in a specific folder in the file system.

```{code-cell} ipython3
from unitpackage.collection import Collection

db = Collection.from_local("../files")
db
```

<!-- We might want to reinclude this part, if we have specific examples. The CV module is now deprecated-->
<!-- In case your files have a specific structure or contain a specific type of data, such as cyclic voltammograms, use the respective class to create your collection instead, such as

```{code-cell} ipython3
from unitpackage.cv.cv_collection import CVCollection

cv_db = CVCollection.from_local("../files")
cv_db
```

```{note}
Without providing any argument to the `Collection` class, the data from [echemdb.org](https://www.echemdb.org/cv) will be downloaded and stored as collection instead.
```
-->

### From URL

A collection of datapackages can be created by collecting datapackages recursively from a url to a ZIP file. The data is extracted to a temporary directory.

```{note}
Without providing the argument `url` to the `from_remote` method, the data shown on [echemdb.org](https://www.echemdb.org/cv) will be downloaded from the
[echemdb data repository](https://github.com/echemdb/electrochemistry-data) and stored as collection instead.
```

```{code-cell} ipython3
from unitpackage.collection import Collection

db = Collection.from_remote()
db
```

Providing an output directory with the parameter `outdir` allows saving the packages in a specific output directory.
A parameter `data` allows specifying the folder within the ZIP containing the datapackages.

```{code-cell} ipython3
from unitpackage.collection import Collection

db = Collection.from_remote(data='data', outdir='generated/from_url')
```

## Load entries

An individual entry can be loaded from a local datapackage.

```{code-cell} ipython3
from unitpackage.entry import Entry

db = Entry.from_local("../files/demo_package.json")
db
```

Alternatively, entries can be created from CSV or pandas datframes.
In these cases, metadata and descriptors for the columns in the CSV can be added upon evoking the entry.

Metadata should be provided as Python dictionary and the fields must be a list, as illustrated in the example below.
The individual fields must have a name.
For a CSV

```{code-cell} ipython3
from unitpackage.entry import Entry

metadata = {'user': 'Max Doe'}
fields = [{'name': 't', 'unit':'s'},{'name': 'j', 'unit':'mA/cm²'}]

csv_entry = Entry.from_csv("../files/demo_package.csv", metadata=metadata, fields=fields)
```

In a similar way an entry can be created from a pandas resource.

```{code-cell} ipython3
import pandas as pd
from unitpackage.entry import Entry

data = {'x': [1,2,3], 'v': [1,3,2]}
df = pd.DataFrame(data)

metadata = {'user': 'Max Doe'}
fields = [{'name': 'x', 'unit':'m'},{'name': 'v', 'unit':'m/s', 'description': 'velocity'}]

df_entry = Entry.from_df(df, basename='df_data', metadata=metadata, fields=fields)
```

## Save entries

Entries can be saved as JSON and CSV in a specified folder either directly from collection

```{code-cell} ipython3
from unitpackage.collection import Collection

db = Collection.from_local("../files")
db.save_entries(outdir="../generated/files")
```

or from a single entry.

```{code-cell} ipython3
from unitpackage.entry import Entry

entry = Entry.from_local("../files/demo_package.json")
entry.save(outdir="../generated/files/saved_entry")
```

The basename of the entry can be modified

```{code-cell} ipython3
entry.save(basename=entry.identifier + "_r" , outdir="../generated/files/saved_entry")
```

## Create local unitpackages

Local Frictionless datapackages (JSON and CSV) can be created by combining the methods to load and save entries above.

Following is an example for a CSV, where the metadata and the field description are stored in a separate metadata file.

```{code-cell} ipython3
import yaml

with open("../files/demo_package.csv.yaml", "rb") as f:
    metadata = yaml.load(f, Loader=yaml.SafeLoader)

fields = metadata["figureDescription"]["fields"]

entry = Entry.from_csv(csvname="../files/demo_package.csv", metadata=metadata, fields=fields)
entry.save(outdir="../generated/files/csv_entry/")
```
