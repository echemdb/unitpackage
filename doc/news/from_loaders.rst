**Added:**

* Added `device` parameter to `Entry.from_csv()` to select instrument-specific loaders (e.g., ``device='eclab'`` for BioLogic MPT files, ``device='gamry'`` for Gamry DTA files).
* Added `BaseLoader.metadata` property, which returns file structure information (loader name, delimiter, decimal, header, column headers) stored as ``dsvDescription`` in the entry's metadata.
* Added `EchemdbEntry.from_mpt()` classmethod to load BioLogic EC-Lab MPT files with automatic field updates, renaming, and filtering.
* Added `eclab_fields.py` module (renamed from ``column_names.py``) containing ``biologic_fields`` and ``biologic_fields_alt_names`` for standardized electrochemistry field definitions.
