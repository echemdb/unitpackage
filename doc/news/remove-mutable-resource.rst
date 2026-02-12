**Added:**

* Added `_create_new_df_resource()`, which returns a new pandas resource when the schema of the resource changed.
* Added `_df_resource()`, which transforms a tabular_resource into a pandas resource when the data or schema is modified.

**Removed:**

* Removed `entry.mutable_resource`.
