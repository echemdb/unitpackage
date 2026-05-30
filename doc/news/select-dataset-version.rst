**Added:**

* Added ``Echemdb.from_remote(version=...)`` to download a specific version of the echemdb database. The version is defined as ``ECHEMDB_DATABASE_VERSION`` in ``remote.py`` and serves as the single source of truth.

**Changed:**

* Changed ``Collection.from_remote`` to log the URL it downloads data from.
* Changed argument order in ``Collection.from_remote``, ``Echemdb.from_remote``, and ``collect_datapackages``: ``outdir`` now comes before ``data``.

**Removed:**

* Removed ``ECHEMDB_DATABASE_URL`` module-level constant from ``remote.py``; use ``get_echemdb_database_url()`` instead.
