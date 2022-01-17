r"""
A Database of Cyclic Voltammograms.

EXAMPLES:

Create a database from local data packages in the `data/` directory::

    >>> from echemdb.data.local import collect_datapackages
    >>> database = Database(collect_datapackages('data/'))

Create a database from the data packages published in the echemdb::

    >>> database = Database()  # doctest: +REMOTE_DATA

Search the database for a single publication::

    >>> database.filter(lambda entry: entry.source.doi == 'https://doi.org/10.1039/C0CP01001D')  # doctest: +REMOTE_DATA
    [Entry('alves_2011_electrochemistry_6010_p2_2a_solid')]

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
import logging

logger = logging.getLogger("echemdb")


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
    def __init__(self, data_packages=None, bibliography=None):
        if data_packages is None:
            import os.path
            import echemdb.data.remote
            data_packages = echemdb.data.remote.collect_datapackages(os.path.join('website-gh-pages', 'data', 'generated', 'svgdigitizer'))

            if bibliography is None:
                bibliography = echemdb.data.remote.collect_bibliography(os.path.join('website-gh-pages', 'Literature'))

        if bibliography is None:
            bibliography = []

        from collections.abc import Iterable
        if isinstance(bibliography, Iterable):
            from pybtex.database import BibliographyData
            bibliography = BibliographyData(entries={
                entry.key: entry for entry in bibliography
            })

        self._packages = data_packages
        self._bibliography = bibliography

    @classmethod
    def create_example(self):
        r"""
        Return a sample database for use in automated tests.

        EXAMPLES::

            >>> Database.create_example()
            [Entry('alves_2011_electrochemistry_6010_p2_2a_solid'), Entry('engstfeld_2018_polycrystalline_17743_4b_1')]

        """
        from echemdb.data.cv.entry import Entry
        entries = Entry.create_examples("alves_2011_electrochemistry_6010") + \
                        Entry.create_examples("engstfeld_2018_polycrystalline_17743")

        return Database([entry.package for entry in entries], [entry.bibliography for entry in entries])

    @property
    def bibliography(self):
        r"""
        Return a pybtex database of all bibtex bibliography files.
        
        EXAMPLES::

            >>> database = Database.create_example()
            >>> database.bibliography
            BibliographyData(
              entries=OrderedCaseInsensitiveDict([
                ('alves_2011_electrochemistry_6010', Entry('article',
                ...
                ('engstfeld_2018_polycrystalline_17743', Entry('article',
                ...

        """
        from pybtex.database import BibliographyData

        return BibliographyData({
            entry.bibliography.key: entry.bibliography for entry in self if entry.bibliography
        })


    def filter(self, predicate):
        r"""
        Return the subset of the database that satisfies predicate.

        EXAMPLES::

            >>> database = Database.create_example()
            >>> database.filter(lambda entry: entry.source.doi == 'https://doi.org/10.1039/C0CP01001D')
            [Entry('alves_2011_electrochemistry_6010_p2_2a_solid')]

        The filter predicate can use properties that are not present on all
        entries in the database. If a property is missing the element is
        removed from the database::

            >>> database.filter(lambda entry: entry.non.existant.property)
            []

        """
        def catching_predicate(entry):
            try:
                return predicate(entry)
            except (KeyError, AttributeError) as e:
                logger.debug(f"Filter removed entry {entry} due to error: {e}")
                return False

        return Database(data_packages=[entry.package for entry in self if catching_predicate(entry)], bibliography=self._bibliography)

    def __iter__(self):
        r"""
        Return an iterator over the entries in this database.

        EXAMPLES::

            >>> database = Database.create_example()
            >>> next(iter(database))
            Entry('alves_2011_electrochemistry_6010_p2_2a_solid')

        """
        from echemdb.data.cv.entry import Entry

        def get_bibliography(package):
            bib = Entry(package, bibliography=None).source.bib
            return self._bibliography.entries.get(bib, None)

        return iter([Entry(package, bibliography=get_bibliography(package)) for package in self._packages])

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
