API
===

This API allows interacting with a collection of
[frictionless datapackages](https://frictionlessdata.io/), stored in a [specific format](usage/unitpackage.md), explore the content of its entries and visualize the underlying data.

A [`Collection`](api/collection.md) of datapackages, denoted as [`entries`](api/entry.md) can be created from [local](api/local.md) files or a [remote](api/remote.md) repository. The metadata describing the data are stored as [`descriptors`](api/descriptor.md). For collections containing a certain type of data, collections with specific methods can be created, such as with [`CVCollection`](api/cv/cv_collection.md). In a same way, specific types of entries can be created, such as with [`CVEntry`](api/cv/cv_entry.md)

```{toctree}
:caption: "Modules:"
api/collection.md
api/entry.md
api/descriptor.md
api/cv/cv_collection.md
api/cv/cv_entry.md
api/remote.md
api/local.md
```
