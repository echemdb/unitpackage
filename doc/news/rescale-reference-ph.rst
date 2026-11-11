**Fixed:**

* Fixed `EchemdbEntry.rescale_reference()` failing for entries without a pH in their metadata, even when the conversion does not involve RHE, and when the pH was provided as a plain number. (`#171 <https://github.com/echemdb/unitpackage/issues/171>`_)
