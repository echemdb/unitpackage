**Changed:**

* Changed the CSV loader to emit a warning instead of raising a ``ValueError`` when the number of fields in data rows is inconsistent with column headers. Extra columns are auto-labeled as ``unknown 1``, ``unknown 2``, etc., and missing values are represented as ``NaN``.
