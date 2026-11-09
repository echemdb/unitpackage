**Changed:**

* Changed the API documentation to no longer show the ``TESTS:`` sections of docstrings, which contain doctests that only serve as tests.

**Fixed:**

* Fixed loading local Data Packages with `Collection.from_local()`, `Collection.from_local_file()` and `Entry.from_local()` from absolute Windows paths with forward slashes such as `D:/data/`, which frictionless treated as URLs.
