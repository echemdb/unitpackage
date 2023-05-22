---
jupytext:
  formats: ipynb,md:myst
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

# Collection From Local Packages

A local collection of datapackages can be created by collecting datapackages recursively, which are stored in a specific folder in your file system.

```{code-cell} ipython3
from unitpackage.collection import Collection
from unitpackage.local import collect_datapackages

db = Collection(data_packages=collect_datapackages("../files"))
db
```

All functionalities to interact with a collection or specific entries within the collection are now available to your local files (see [usage section](unitpackage_usage.md)).

```{note}
Without providing the argument `data_packages=collect_datapackages("../packages_folder")` to the `Collection` class, the data from [echemdb.org](https:///www.echemdb.org/cv) will be downloaded and stored as collection instead.
```

In case your files have a specific structure or contain a specific type of data, such as cyclic voltammograms, use the respective class to create your collection, such as

```{code-cell} ipython3
from unitpackage.cv.cv_collection import CVCollection
from unitpackage.local import collect_datapackages

cv_db = CVCollection(data_packages=collect_datapackages("../files"))
cv_db
```
