r"""
A Collection of Cyclic Voltammograms. It provides additional functionalities compared to
the :class:`Collection` specific to Cyclic Voltammograms and electrochemical data.

EXAMPLES:

Create a collection from local `frictionless data packages <https://framework.frictionlessdata.io/>`__
in the `data/` directory::

    >>> from unitpackage.local import collect_datapackages
    >>> collection = CVCollection(collect_datapackages('data/'))

Create a collection from the data packages published in the `echemdb <https://www.echemdb.org/cv>`_::

    >>> collection = CVCollection()  # doctest: +REMOTE_DATA

Search the collection for entries from a single publication::

    >>> collection.filter(lambda entry: entry.source.url == 'https://doi.org/10.1039/C0CP01001D')  # doctest: +REMOTE_DATA
    [CVEntry('alves_2011_electrochemistry_6010_f1a_solid'), ...

"""

# ********************************************************************
#  This file is part of unitpackage.
#
#        Copyright (C) 2021-2023 Albert Engstfeld
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

from unitpackage.collection import Collection

logger = logging.getLogger("unitpackage")


class CVCollection(Collection):
    r"""
    A collection of `frictionless data packages <https://github.com/frictionlessdata/framework>`__.

    Essentially this is just a list of data packages with some additional
    convenience wrap for use in the `echemdb <https://www.echemdb.org/cv>`_.

    EXAMPLES:

    An empty collection::

        >>> collection = CVCollection([])
        >>> len(collection)
        0

    """

    from unitpackage.cv.cv_entry import CVEntry

    Entry = CVEntry

    def materials(self):
        r"""
        Return the substrate materials in the collection.

        EXAMPLES::

            >>> collection = CVCollection.create_example()
            >>> collection.materials() == {'Cu', 'Ru'}
            True

        """
        import pandas as pd

        return set(
            pd.unique(pd.Series([entry.get_electrode("WE").material for entry in self]))
        )

    def describe(self):
        r"""
        Return some statistics about the collection.

        EXAMPLES::

            >>> collection = CVCollection.create_example()
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
