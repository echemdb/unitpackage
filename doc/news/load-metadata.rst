**Added:**

* Added `Entry.remove_columns()`, which removes both a column from the dataframe and the fields.
* Added `Entry.load_metadata()` for loading metadata from YAML or JSON files with method chaining support.
* Added `MetadataDescriptor` class for enhanced metadata handling with dict and attribute-style access.
* Added `Entry.default_metadata_key` class attribute to control metadata access patterns in subclasses.
* Added `Entry._default_metadata` property to access the appropriate metadata subset.
* Added `encoding`, `header_lines`, `column_header_lines`, `decimal`, and `delimiters` parameters to `Entry.from_csv()` for handling complex CSV formats.
* Added `create_tabular_resource_from_csv()` to create resources from CSV files with auto-detection of standard vs. complex formats.
* Added `create_df_resource_from_csv()` for creating pandas dataframe resources from CSV files with custom formats.
* Added `create_df_resource_from_df()` for creating resources directly from pandas DataFrames.
* Added `create_df_resource_from_tabular_resource()` for converting tabular resources to pandas dataframe resources.
* Added `update_fields()` function to update schema fields with additional information.

**Changed:**

* Changed `Entry.field_unit()` to return an empty string instead of raising a KeyError when a field does not have a unit.
* Changed `Entry.from_df()` to no longer require the `outdir` parameter.
* Changed `Entry.from_df()` to directly create entries from pandas DataFrames without temporary CSV files.
* Changed `Entry.from_df()` to require `basename` as a keyword-only argument.
* Changed `Entry.save()` to automatically convert pandas resources to CSV format.
* Changed `Entry.metadata` to return a `MetadataDescriptor` object supporting enhanced metadata operations.
* Changed workflows to use pixi v0.63.2.

**Removed:**

* Removed deprecated module `cv_collection`.
* Removed deprecated module `cv_entry`.

**Fixed:**

* Fixed creating plots from entries without units in the fields (#128).
* Fixed resource naming when importing complex CSV files with multiple headers.
