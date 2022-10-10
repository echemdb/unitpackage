r"""
A Database of Cyclic Voltammograms.

EXAMPLES:

Create a database from local data packages in the `data/` directory::

    >>> from echemdb.local import collect_datapackages
    >>> database = CVDatabase(collect_datapackages('data/'))

Create a database from the data packages published in the echemdb::

    >>> database = CVDatabase()  # doctest: +REMOTE_DATA

Search the database for a single publication::

    >>> database.filter(lambda entry: entry.source.url == 'https://doi.org/10.1039/C0CP01001D')  # doctest: +REMOTE_DATA
    [CVEntry('alves_2011_electrochemistry_6010_f1a_solid'), ...

"""
# ********************************************************************
#  This file is part of echemdb.
#
#        Copyright (C) 2021-2022 Albert Engstfeld
#        Copyright (C) 2021      Johannes Hermann
#        Copyright (C) 2021-2022 Julian Rüth
#        Copyright (C) 2021      Nicolas Hörmann
#
#  echemdb is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  echemdb is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with echemdb. If not, see <https://www.gnu.org/licenses/>.
# ********************************************************************
import logging

from echemdb.database import Database

logger = logging.getLogger("echemdb")


class CVDatabase(Database):
    r"""
    A collection of [data packages](https://github.com/frictionlessdata/datapackage-py).

    Essentially this is just a list of data packages with some additional
    convenience wrap for use in the echemdb.

    EXAMPLES:

    An empty database::

        >>> database = CVDatabase([])
        >>> len(database)
        0

    """
    from echemdb.cv.cv_entry import CVEntry

    Entry = CVEntry

    def materials(self):
        r"""
        Return the substrate materials in the database.

        EXAMPLES::

            >>> database = CVDatabase.create_example()
            >>> database.materials()
            ['Ru', 'Cu']

        """
        import pandas as pd

        return set(
            pd.unique(
                pd.Series(
                    [
                        entry.system.electrodes.working_electrode.material
                        for entry in self
                    ]
                )
            )
        )

    def describe(self):
        r"""
        Returns some statistics about the database.

        EXAMPLES::

            >>> database = CVDatabase.create_example()
            >>> database.describe() # doctest: +NORMALIZE_WHITESPACE
            {'number of references': 2,
            'number of entries': 2,
            'materials': ['Ru', 'Cu']}

        """
        return {
            "number of references": len(self.bibliography.entries),
            "number of entries": len(self),
            "materials": self.materials(),
        }
