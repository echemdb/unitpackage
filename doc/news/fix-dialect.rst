**Fixed:**

* Fixed CSV-to-dataframe reconstruction from tabular resources to honor frictionless descriptor dialect and encoding metadata, avoiding silent misparsing for non-default delimiters.
* Fixed the CSV loader API by replacing the ambiguous `delimiters` argument with explicit `delimiter` and `candidate_delimiters` parameters.

