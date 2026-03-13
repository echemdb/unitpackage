**Fixed:**

* Fixed CLI metadata loading for the `unitpackage csv` command by applying parsed YAML metadata via `entry.metadata.from_dict(...)`.
* Fixed `create_unitpackage(...)` to always store metadata as a dictionary when no metadata is provided.
