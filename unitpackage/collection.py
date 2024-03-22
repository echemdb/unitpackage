r"""
A collection of datapackages with units.

EXAMPLES:

Create a collection from local `frictionless data packages <https://framework.frictionlessdata.io/>`_
in the `data/` directory::

    >>> collection = Collection.from_local('data/')

Create a collection from the data packages published in the on `echemdb <https://www.echemdb.org/cv>`_::

    >>> collection = Collection.from_remote()  # doctest: +REMOTE_DATA

Search the collection for entries from a single publication::

    >>> collection.filter(lambda entry: entry.source.url == 'https://doi.org/10.1039/C0CP01001D')  # doctest: +REMOTE_DATA
    [Entry('alves_2011_electrochemistry_6010_f1a_solid'), ...

"""

# ********************************************************************
#  This file is part of unitpackage.
#
#        Copyright (C) 2021-2024 Albert Engstfeld
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

logger = logging.getLogger("unitpackage")


class Collection:
    r"""
    A collection of [frictionless data packages](https://github.com/frictionlessdata/datapackage-py).

    EXAMPLES:

    An empty collection::

        >>> collection = Collection([])
        >>> len(collection)
        0

    """

    from unitpackage.entry import Entry

    # Entries of this collection are created from this type. Subclasses can replace this with a specialized entry type.
    Entry = Entry

    def __init__(self, data_packages=None):
        self._packages = data_packages

    @classmethod
    def create_example(cls):
        r"""
        Return a sample collection for use in automated tests.

        EXAMPLES::

            >>> Collection.create_example()  # doctest: +NORMALIZE_WHITESPACE
            [Entry('alves_2011_electrochemistry_6010_f1a_solid'),
            Entry('engstfeld_2018_polycrystalline_17743_f4b_1'),
            Entry('no_bibliography')]

        """

        entries = (
            cls.Entry.create_examples("alves_2011_electrochemistry_6010")
            + cls.Entry.create_examples("engstfeld_2018_polycrystalline_17743")
            + cls.Entry.create_examples("no_bibliography")
        )

        return cls(
            [entry.package for entry in entries],
        )

    @property
    def bibliography(self):
        r"""
        Return a pybtex database of all bibtex bibliography files.

        EXAMPLES::

            >>> collection = Collection.create_example()
            >>> collection.bibliography
            BibliographyData(
              entries=OrderedCaseInsensitiveDict([
                ('alves_2011_electrochemistry_6010', Entry('article',
                ...
                ('engstfeld_2018_polycrystalline_17743', Entry('article',
                ...

        A collection with entries without bibliography.

            >>> collection = Collection.create_example()["no_bibliography"]
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

    def filter(self, predicate):
        r"""
        Return the subset of the collection that satisfies predicate.

        EXAMPLES::

            >>> collection = Collection.create_example()
            >>> collection.filter(lambda entry: entry.source.url == 'https://doi.org/10.1039/C0CP01001D')
            [Entry('alves_2011_electrochemistry_6010_f1a_solid')]


        The filter predicate can use properties that are not present on all
        entries in the collection. If a property is missing the element is
        removed from the collection::

            >>> collection.filter(lambda entry: entry.non.existing.property)
            []

        """

        def catching_predicate(entry):
            try:
                return predicate(entry)
            except (KeyError, AttributeError) as e:
                logger.debug(f"Filter removed entry {entry} due to error: {e}")
                return False

        return type(self)(
            data_packages=[
                entry.package for entry in self if catching_predicate(entry)
            ],
        )

    def __iter__(self):
        r"""
        Return an iterator over the entries in this collection.

        EXAMPLES::

            >>> collection = Collection.create_example()
            >>> next(iter(collection))
            Entry('alves_2011_electrochemistry_6010_f1a_solid')

        """
        # Return the entries sorted by their identifier. There's a small cost
        # associated with the sorting but we do not expect to be managing
        # millions of identifiers and having them show in sorted order is very
        # convenient, e.g., when doctesting.
        return iter(
            [
                self.Entry(package)
                for package in sorted(self._packages, key=lambda p: p.resources[0].name)
            ]
        )

    def __len__(self):
        r"""
        Return the number of entries in this collection.

        EXAMPLES::

            >>> collection = Collection.create_example()
            >>> len(collection)
            3

        """
        return len(self._packages)

    def __repr__(self):
        r"""
        Return a printable representation of this collection.

        EXAMPLES::

            >>> Collection([])
            []

        """
        return repr(list(self))

    def __getitem__(self, identifier):
        r"""
        Return the entry with this identifier.

        EXAMPLES::

            >>> collection = Collection.create_example()
            >>> collection['alves_2011_electrochemistry_6010_f1a_solid']
            Entry('alves_2011_electrochemistry_6010_f1a_solid')

            >>> collection['invalid_key']
            Traceback (most recent call last):
            ...
            KeyError: "No collection entry with identifier 'invalid_key'."

        """
        entries = [entry for entry in self if entry.identifier == identifier]

        if len(entries) == 0:
            raise KeyError(f"No collection entry with identifier '{identifier}'.")
        if len(entries) > 1:
            raise KeyError(
                f"The collection has more than one entry with identifier '{identifier}'."
            )
        return entries[0]

    def save_entries(self, outdir=None):
        r"""
        Save the entries of this collection as datapackages (CSV and JSON)
        to the output directory :param outdir:.

        EXAMPLES::

            >>> db = Collection.create_example()
            >>> db.save_entries(outdir='test/generated/saved_collection')
            >>> import glob
            >>> glob.glob('test/generated/saved_collection/**.json') # doctest: +NORMALIZE_WHITESPACE
            ['test...

        """
        for entry in self:
            entry.save(outdir=outdir)

    @classmethod
    def from_local(cls, datadir):
        r"""
        Create a collection from local datapackages.

        EXAMPLES::

            >>> from unitpackage.collection import Collection
            >>> collection = Collection.from_local('./examples')
            >>> collection  # doctest: +NORMALIZE_WHITESPACE
            [Entry('alves_2011_electrochemistry_6010_f1a_solid'),
            Entry('engstfeld_2018_polycrystalline_17743_f4b_1'),
            Entry('no_bibliography')]

        """
        import unitpackage.local

        packages = unitpackage.local.collect_datapackages(datadir)
        return cls(data_packages=packages)

    @classmethod
    def from_remote(cls, url=None, data=None, outdir=None):
        r"""
        Create a collection from a url containing a zip.

        When no url is provided a collection is created from the data packages published
        on `echemdb <https://www.echemdb.org/cv>`_.

        EXAMPLES::

            >>> from unitpackage.collection import Collection
            >>> collection = Collection.from_remote()  # doctest: +REMOTE_DATA

        The folder containing the data in the zip can be specified with the :param data:.
        An output directory for the extracted data can be specified with the :param outdir:.
        """
        import unitpackage.remote

        if url is None:
            return cls(data_packages=unitpackage.remote.collect_datapackages())

        data_packages = unitpackage.remote.collect_datapackages(
            url=url, data=data, outdir=outdir
        )
        return cls(data_packages=data_packages)
