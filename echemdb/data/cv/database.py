r"""
A Database of Cyclic Voltammograms.

EXAMPLES:

Create a database from local data packages in the `data/` directory::

    >>> from echemdb.data.local import collect_datapackages
    >>> database = Database(collect_datapackages('data/'))

Create a database from the data packages published in the echemdb::

    >>> database = Database()

Search the database for a single publication::

    >>> database.filter(lambda entry: entry.source.doi == 'https://doi.org/10.1002/chem.201803418')
    [Entry('Engstfeld_2018_polycrystalline_17743_4b_1')]

"""
# ********************************************************************
#  This file is part of echemdb.
#
#        Copyright (C) 2021 Albert Engstfeld
#        Copyright (C) 2021 Johannes Hermann
#        Copyright (C) 2021 Julian Rüth
#        Copyright (C) 2021 Nicolas Hörmann
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

class Database:
    r"""
    A collection of [data packages](https://github.com/frictionlessdata/datapackage-py).

    Essentially this is just a list of data packages with some additional
    convenience wrap for use in the echemdb.

    EXAMPLES:

    An empty database::

        >>> database = Database([])
        >>> len(database)
        0

    """
    def __init__(self, data_packages=None):
        if data_packages is None:
            import os.path
            import echemdb.data.remote
            data_packages = echemdb.data.remote.collect_datapackages(os.path.join('website-gh-pages', 'data', 'generated', 'svgdigitizer'))
        self._packages = data_packages

    @classmethod
    def create_example(self):
        r"""
        Return a sample database for use in automated tests.

        EXAMPLES::

            >>> Database.create_example()
            [Entry('Engstfeld_2018_polycrystalline_17743_4b_1'), Entry('alves_2011_electrochemistry_6010_p2_2a_solid')]

        """
        from echemdb.data.cv.entry import Entry
        entries = Entry.create_examples("Engstfeld_2018_polycristalline_17743") + \
            Entry.create_examples("alves_2011_electrochemistry_6010")

        return Database([entry.package for entry in entries])

    def filter(self, predicate):
        r"""
        Return the subset of the database that satisfies predicate.

        EXAMPLES::

            >>> database = Database.create_example()
            >>> database.filter(lambda entry: entry.source.doi == 'https://doi.org/10.1002/chem.201803418')
            [Entry('Engstfeld_2018_polycrystalline_17743_4b_1')]

        """
        return Database([entry.package for entry in self if predicate(entry)])

    def __iter__(self):
        r"""
        Return an iterator over the entries in this database.

        EXAMPLES::

            >>> database = Database.create_example()
            >>> next(iter(database))
            Entry('Engstfeld_2018_polycrystalline_17743_4b_1')

        """
        from echemdb.data.cv.entry import Entry
        return iter([Entry(package) for package in self._packages])

    def __len__(self):
        r"""
        Return the number of entries in this database.

        EXAMPLES::

            >>> database = Database.create_example()
            >>> len(database)
            2

        """
        return len(self._packages)

    def __repr__(self):
        r"""
        Return a printable representation of this database.

        EXAMPLES::

            >>> Database([])
            []

        """
        return repr(list(self))
