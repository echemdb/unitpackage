**Added:**

* Added `entry.fields` as a property to access the list of fields in the entry's schema (`entry.resource.schema.fields`).
* Added `entry.rename_field(field_name, new_name, keep_original_name_as=None)` for renaming a single field.
* Added `entry.remove_column(field_name)` for removing a single column.
* Added `_modify_field_name()` helper method for modifying a single field's name.

**Changed:**

* Changed `entry.remove_columns()`, `entry.add_columns()`, and `entry.update_fields()` to use frictionless Schema's built-in methods (`schema.remove_field()`, `schema.add_field()`, `schema.update_field()`).
* Changed `entry.rename_fields()` to internally use `entry.rename_field()` for each field, improving efficiency.
* Changed `entry.remove_columns()` to internally use `entry.remove_column()` for each column, improving efficiency.
* Changed `_modify_fields()` to `_modify_fields_names()` for clearer naming, and updated its parameter names (`original` → `fields`, `alternative` → `name_mappings`).
* Changed `update_fields()` in `unitpackage.local` to use frictionless `schema.update_field()` instead of manual field dictionary manipulation.
* Changed `create_unitpackage()` in `unitpackage.local` to use frictionless `schema.update_field()` directly instead of calling the `update_fields()` helper function.
* Changed all docstrings referencing `entry.resource.schema.fields` to use the simpler `entry.fields` property.

**Performance:**

* Improved field handling performance by having singular methods (`rename_field`, `remove_column`) do the core work, with plural methods composing multiple singular operations instead of duplicating logic.
