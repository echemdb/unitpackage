r"""
Utilities to work with remote data packages.
"""

# ********************************************************************
#  This file is part of unitpackage.
#
#        Copyright (C) 2021-2024 Albert Engstfeld
#        Copyright (C)      2021 Johannes Hermann
#        Copyright (C) 2021-2022 Julian Rüth
#        Copyright (C)      2021 Nicolas Hörmann
#
#  unitpackage is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  unitpackage is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with unitpackage. If not, see <https://www.gnu.org/licenses/>.
# ********************************************************************

import os.path
from functools import cache

ECHEMDB_DATABASE_URL = os.environ.get(
    "ECHEMDB_DATABASE_URL",
    "https://github.com/echemdb/electrochemistry-data/releases/download/0.1.0-alpha.2/data-0.1.0-alpha.2.zip",
)

@cache
def collect_zipfile_from_url(url=ECHEMDB_DATABASE_URL):
    r"""
    Download a ZIP file from ``url`` and return it as a temporary object to
    extract contents from.
    """
    from urllib.request import urlopen

    with urlopen(url) as response:
        from io import BytesIO
        from zipfile import ZipFile

        return ZipFile(BytesIO(response.read()))


@cache
def collect_datapackages(data=None, url=ECHEMDB_DATABASE_URL, outdir=None):
    r"""
    Return a list of data packages defined in a remote location.

    The default is to download the packages currently available on `echemdb <https://www.echemdb.org/cv>`_
    which are retrieved from `the echemdb electrochemistry-data repository <https://github.com/echemdb/electrochemistry-data>`_
    and extract them to a temporary directory.

    To retrieve data from a subdirectory within the zip, provide the location in ``data``.

    EXAMPLES::

        >>> packages = collect_datapackages()  # doctest: +REMOTE_DATA

    """
    if outdir is None:
        import atexit
        import shutil
        import tempfile

        outdir = tempfile.mkdtemp()
        atexit.register(shutil.rmtree, outdir)

    compressed = collect_zipfile_from_url(url)

    compressed.extractall(
        outdir,
        members=[
            name
            for name in compressed.namelist()
            if name.endswith(".json") or name.endswith(".csv")
        ],
    )

    import unitpackage.local

    return unitpackage.local.collect_datapackages(
        os.path.join(outdir, data) if data else outdir
    )
