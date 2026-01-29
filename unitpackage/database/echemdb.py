r"""
A Collection of data from the `echemdb data repository
<https://github.com/echemdb/electrochemistry-data>`_ displayed on the `echemdb website
<https://www.echemdb.org/cv>`_. It provides additional functionalities compared to
the :class:`Collection` specific to the data in the echemdb repository.

EXAMPLES:

Create a collection from the Data Packages published in the `echemdb data repository
<https://github.com/echemdb/electrochemistry-data>`_ displayed on the `echemdb website
<https://www.echemdb.org/cv>`_.::

    >>> collection = Echemdb.from_remote()  # doctest: +REMOTE_DATA

Search the collection for entries from a single publication::

    >>> collection.filter(lambda entry: entry.source.url == 'https://doi.org/10.1039/C0CP01001D')  # doctest: +REMOTE_DATA
    [Echemdb('alves_2011_electrochemistry_6010_f1a_solid'), ...

"""

# ********************************************************************
#  This file is part of unitpackage.
#
#        Copyright (C) 2021-2026 Albert Engstfeld
#        Copyright (C) 2021      Johannes Hermann
#        Copyright (C) 2021-2022 Julian Rüth
#        Copyright (C) 2021      Nicolas Hörmann
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
import logging
from functools import cached_property

from unitpackage.collection import Collection

logger = logging.getLogger("unitpackage")


class Echemdb(Collection):
    r"""
    A collection of `frictionless Data Packages <https://github.com/frictionlessdata/framework>`__.

    Essentially this is just a list of data packages with some additional
    convenience wrap for use in the `echemdb data repository <https://github.com/echemdb/electrochemistry-data>`_
    displayed on the `echemdb website <https://www.echemdb.org/cv>`_.

    EXAMPLES:

    An example collection::

        >>> collection = Collection.create_example()
        >>> collection.package.resource_names  # doctest: +NORMALIZE_WHITESPACE
        ['alves_2011_electrochemistry_6010_f1a_solid',
        'engstfeld_2018_polycrystalline_17743_f4b_1',
        'no_bibliography']

    """

    from unitpackage.database.echemdb_entry import EchemdbEntry

    Entry = EchemdbEntry

    def materials(self):
        r"""
        Return the substrate materials in the collection.

        EXAMPLES::

            >>> from unitpackage.database.echemdb import Echemdb
            >>> collection = Echemdb.create_example()
            >>> collection.materials() == {'Cu', 'Ru'}
            True

        """
        import pandas as pd

        # pylint: disable=R0801
        return set(
            pd.unique(pd.Series([entry.get_electrode("WE").material for entry in self]))
        )

    def describe(self):
        r"""
        Return some statistics about the echemdb database.

        EXAMPLES::

            >>> from unitpackage.database.echemdb import Echemdb
            >>> collection = Echemdb.create_example()
            >>> collection.describe() == \
            ... {'number of references': 2,
            ... 'number of entries': 3,
            ... 'materials': {'Cu', 'Ru'}}
            True

        """
        return {
            "number of references": (
                0
                if isinstance(self.bibliography, str)
                else len(self.bibliography.entries)
            ),
            "number of entries": len(self),
            "materials": self.materials(),
        }

    @cached_property
    def bibliography(self):
        r"""
        Return a pybtex database of all bibtex bibliography files,
        associated with the entries.

        EXAMPLES::

            >>> from unitpackage.database.echemdb import Echemdb
            >>> collection = Echemdb.create_example()
            >>> collection.bibliography
            BibliographyData(
              entries=OrderedCaseInsensitiveDict([
                ('alves_2011_electrochemistry_6010', Entry('article',
                ...
                ('engstfeld_2018_polycrystalline_17743', Entry('article',
                ...

        A derived collection includes only the bibliographic entries of the remaining entries::

            >>> collection.filter(lambda entry: entry.source.citationKey != 'alves_2011_electrochemistry_6010').bibliography
            BibliographyData(
              entries=OrderedCaseInsensitiveDict([
                ('engstfeld_2018_polycrystalline_17743', Entry('article',
                ...

        A collection with entries without bibliography::

            >>> collection = Echemdb.create_example()["no_bibliography"]
            >>> collection.bibliography
            ''

        """
        from pybtex.database import BibliographyData

        bib_data = BibliographyData(
            {
                entry.bibliography.key: entry.bibliography
                for entry in self
                if entry.bibliography
            }
        )

        if isinstance(bib_data, str):
            return bib_data

        # Remove duplicates from the bibliography
        bib_data_ = BibliographyData()

        for key, entry in bib_data.entries.items():
            if key not in bib_data_.entries:
                bib_data_.add_entry(key, entry)

        return bib_data_
