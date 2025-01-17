**Added:**

* Added the property `collection.package` returning a frictionless Data Package for this collection.
* Added the property `entry.internal_resource`, which is a virtual modifiable copy of the original resource excluding its metadata.
* Added `unitpackage.local.collect_resources`, which collects all resources from a list of frictionless Data Packages.

**Changed:**

* Changed `unitpackage.entry.Entry` from being a frictionless Data Package into a frictionless Resource.
* Changed `unitpackage.collection.Collection` from being a collection of frictionless Data Packages into a collection of frictionless Resources.
* Changed the virtual `echemdb` Resource into an `entry.internal_resource`.
* Changed `unitpackage.local.create_df_resource` to create a resource from an actual frictionless Resource instead of a frictionless Data Package.

**Fixed:**

* Fixed parsing of arguments `data` and `outdir` for `collection.from_remote` downloading data from the default remote url.


**Performance:**

* Improved loading collections via `collection.from_local` or `collection.from_remote` and entries via `entry.from_local`. In contrast to the previous version, dataframes are now only loaded when a method or property is called that requires access to the resource's data. This also increases the speed for filtering the data based on metadata predicates.
