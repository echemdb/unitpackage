**Fixed:**

* Fixed CLI metadata loading for the `unitpackage csv` command by applying parsed YAML metadata via `entry.metadata.from_dict(...)`.
* Fixed `create_unitpackage(...)` to always store metadata as a dictionary when no metadata is provided.
* Fixed metadata aliasing when creating derived resources by deep-copying metadata in `Entry._create_new_df_resource(...)`.
