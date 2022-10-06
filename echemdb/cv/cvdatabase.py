r"""
A Database of Cyclic Voltammograms.

EXAMPLES:

Create a database from local data packages in the `data/` directory::

    >>> from echemdb.local import collect_datapackages
    >>> database = CVdatabase(collect_datapackages('data/'))

Create a database from the data packages published in the echemdb::

    >>> database = CVdatabase()  # doctest: +REMOTE_DATA

Search the database for a single publication::

    >>> database.filter(lambda entry: entry.source.url == 'https://doi.org/10.1039/C0CP01001D')  # doctest: +REMOTE_DATA
    [Entry('alves_2011_electrochemistry_6010_f1a_solid'), ...

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


class CVdatabase(Database):
    r"""
    A collection of [data packages](https://github.com/frictionlessdata/datapackage-py).

    Essentially this is just a list of data packages with some additional
    convenience wrap for use in the echemdb.

    EXAMPLES:

    An empty database::

        >>> database = CVdatabase([])
        >>> len(database)
        0

    """
    from echemdb.cv.cventry import CVentry
    Entry = CVentry

    def materials(self):
        r"""
        Return the substrate materials in the database.

        EXAMPLES::

            >>> database = CVdatabase.create_example()
            >>> database.materials()
            ['Ru', 'Cu']

        """
        import pandas as pd

        return list(
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

            >>> database = CVdatabase.create_example()
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

    @classmethod
    def create_example(cls):
        r"""
        Return a sample database for use in automated tests.

        EXAMPLES::

            >>> CVdatabase.create_example()
            [CVentry('alves_2011_electrochemistry_6010_f1a_solid'), CVentry('engstfeld_2018_polycrystalline_17743_f4b_1')]

        """
        from echemdb.cv.cventry import CVentry

        entries = CVentry.create_examples(
            "alves_2011_electrochemistry_6010"
        ) + CVentry.create_examples("engstfeld_2018_polycrystalline_17743")

        return CVdatabase(
            [entry.package for entry in entries],
            [entry.bibliography for entry in entries],
        )
