**Added:**

* Added `_create_new_df_resource()`, which returns a new pandas resource when the schema of the resource changed.
* Added `_df_resource` as a cached property, which transforms a tabular_resource into a pandas resource when first accessed and caches the result for improved performance.

**Removed:**

* Removed `entry.mutable_resource`.
