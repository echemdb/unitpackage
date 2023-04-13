**Added:**

* Added method `get_electrode(name)` in `CVEntry`.
* Added property `_metadata` in `Entry`.

**Changed:**

* Adapted to a new echemdb datapackge metadata schema. The metadata describing the data is now part of the resource and no longer a top level key of the datapackage. The `electrodes` key used for electrochemical systems is now a `list`` instead of a `dict`. The bibtex bibliography key is now part of the `source` key.
