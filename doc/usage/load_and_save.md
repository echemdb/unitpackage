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

entry = Entry.from_local("../files/demo_package.json")
entry
```

Alternatively, entries can be created from CSV files or pandas DataFrames.
Metadata and field descriptors can be added after creation using `update_fields()` and `metadata.from_dict()`.

From a CSV file:

```{code-cell} ipython3
from unitpackage.entry import Entry

csv_entry = Entry.from_csv(csvname="../files/demo_package.csv")
csv_entry
```

For CSV files with more complex structures, additional arguments can be provided:

- `header_lines` — number of header lines to skip before the data
- `column_header_lines` — number of lines containing column headers (multiple lines are flattened and separated by ` / `)
- `decimal` — decimal separator (e.g., `','` for European-style numbers)
- `delimiters` — column delimiter (auto-detected if not specified)
- `encoding` — file encoding

For example, a CSV with multiple header lines:

```{code-cell} ipython3
csv_entry = Entry.from_csv(csvname='../../examples/from_csv/from_csv_multiple_headers.csv', column_header_lines=2)
csv_entry.fields
```

For even more complex file formats from laboratory equipment, see the [Loaders](loaders.md) section.

From a pandas DataFrame:

```{code-cell} ipython3
import pandas as pd
from unitpackage.entry import Entry

data = {'x': [1,2,3], 'v': [1,3,2]}
df = pd.DataFrame(data)

df_entry = Entry.from_df(df, basename='df_data')
df_entry
```

For more details on adding metadata and field descriptions, see [Creating Unitpackages](create_unitpackage.md).

## Save entries

Entries can be saved as JSON and CSV in a specified folder either directly from a collection

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

The basename of the entry can be modified.

```{code-cell} ipython3
entry.save(basename=entry.identifier + "_r" , outdir="../generated/files/saved_entry")
```
