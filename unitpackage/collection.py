r"""
A collection of frictionless Resources that can be accessed and stored as
    a [frictionless Data Package](https://github.com/frictionlessdata/datapackage-py).

EXAMPLES:

Create a collection from frictionless Resources stored within local
`frictionless Data Packages <https://framework.frictionlessdata.io/>`_
in the `data/` directory::

    >>> collection = Collection.from_local('data/')

Create a collection from the Data Packages published in the `echemdb data repository
<https://github.com/echemdb/electrochemistry-data>`_, and
that are displayed on the `echemdb website
<https://www.echemdb.org/cv>`_.::

    >>> collection = Collection.from_remote()  # doctest: +REMOTE_DATA

Search the collection for entries, for example,
from a single publication providing its DOI::

    >>> collection.filter(lambda entry: entry.source.url == 'https://doi.org/10.1039/C0CP01001D')  # doctest: +REMOTE_DATA
    [Entry('alves_2011_electrochemistry_6010_f1a_solid'), ...

"""

# ********************************************************************
#  This file is part of unitpackage.
#
#        Copyright (C) 2021-2025 Albert Engstfeld
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

from frictionless import Package

logger = logging.getLogger("unitpackage")


class Collection:
    r"""
    A collection of frictionless Resources,
    that can be accessed and stored as
    a [frictionless Data Package](https://github.com/frictionlessdata/datapackage-py).

    EXAMPLES:

    An empty collection::

        >>> collection = Collection([])
        >>> collection
        []

    An example collection (only available from the development environment)::

        >>> collection = Collection.create_example()
        >>> collection.package.resource_names  # doctest: +NORMALIZE_WHITESPACE
        ['alves_2011_electrochemistry_6010_f1a_solid',
        'engstfeld_2018_polycrystalline_17743_f4b_1',
        'no_bibliography']

    Collections must contain Resources with unique identifiers::

        >>> db = Collection.from_local("./examples/duplicates")
        Traceback (most recent call last):
        ...
        ValueError: Collection contains duplicate entries: ['duplicate']

    """

    from unitpackage.entry import Entry

    # Entries of this collection are created from this type.
    # Subclasses can replace this with a specialized entry type.
    Entry = Entry

    def __init__(self, package=None):
        if not isinstance(package, Package):
            package = Package()

        from iteration_utilities import duplicates, unique_everseen

        duplicates = list(unique_everseen(duplicates(package.resource_names)))

        if duplicates:
            raise ValueError(f"Collection contains duplicate entries: {duplicates}")

        self.package = package

    @classmethod
    def create_example(cls):
        r"""
        Return a sample collection for use in automated tests
        (only accessible from the development environment).

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

        package = Package()

        for entry in entries:
            package.add_resource(entry.resource)

        return cls(
            package=package,
        )

    @property
    def bibliography(self):
        r"""
        Return a pybtex database of all bibtex bibliography files,
        associated with the entries.

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

        package = Package()

        for entry in self:
            if catching_predicate(entry):
                package.add_resource(entry.resource)

        return type(self)(
            package=package,
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
                self.Entry(resource)
                for resource in sorted(self.package.resources, key=lambda p: p.name)
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
        return len(self.package.resources)

    def __repr__(self):
        r"""
        Return a printable representation of this collection.

        EXAMPLES::

            >>> collection = Collection.create_example()
            >>> collection # doctest: +NORMALIZE_WHITESPACE
            [Entry('alves_2011_electrochemistry_6010_f1a_solid'),
            Entry('engstfeld_2018_polycrystalline_17743_f4b_1'),
            Entry('no_bibliography')]

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
        if not identifier in self.package.resource_names:
            raise KeyError(f"No collection entry with identifier '{identifier}'.")

        return self.Entry(self.package.get_resource(identifier))

    def save_entries(self, outdir=None):
        r"""
        Save the entries of this collection as Data Packages (CSV and JSON)
        to the output directory :param outdir:.

        EXAMPLES::

            >>> db = Collection.create_example()
            >>> db.save_entries(outdir='./test/generated/saved_collection')
            >>> import glob
            >>> glob.glob('test/generated/saved_collection/**.json') # doctest: +NORMALIZE_WHITESPACE
            ['test...

        """
        for entry in self:
            entry.save(outdir=outdir)

    @classmethod
    def from_local(cls, datadir):
        r"""
        Create a collection from local Data Packages.

        EXAMPLES::

            >>> from unitpackage.collection import Collection
            >>> collection = Collection.from_local('./examples/local/')
            >>> collection  # doctest: +NORMALIZE_WHITESPACE
            [Entry('alves_2011_electrochemistry_6010_f1a_solid'),
            Entry('engstfeld_2018_polycrystalline_17743_f4b_1'),
            Entry('no_bibliography')]

        """
        import unitpackage.local

        packages = unitpackage.local.collect_datapackages(datadir)
        resources = unitpackage.local.collect_resources(packages)
        package = Package()

        for resource in resources:
            package.add_resource(resource)

        return cls(package=package)

    @classmethod
    def from_local_file(cls, filename):
        r"""
        Create a collection from a local Data Package.

        EXAMPLES::

            >>> from unitpackage.collection import Collection
            >>> collection = Collection.from_local_file('./examples/local/engstfeld_2018_polycrystalline_17743/engstfeld_2018_polycrystalline_17743_f4b_1.json')
            >>> collection  # doctest: +NORMALIZE_WHITESPACE
            [Entry('engstfeld_2018_polycrystalline_17743_f4b_1')]

        """
        from unitpackage.local import collect_datapackage

        package = collect_datapackage(filename)

        return cls(package=package)

    @classmethod
    def from_remote(cls, url=None, data=None, outdir=None):
        r"""
        Create a collection from a url containing a zip.

        When no url is provided a collection is created from the Data Packages published
        on the `echemdb data repository <https://github.com/echemdb/electrochemistry-data>`_
        displayed on the `echemdb website <https://www.echemdb.org/cv>`_.

        EXAMPLES::

            >>> from unitpackage.collection import Collection
            >>> collection = Collection.from_remote()  # doctest: +REMOTE_DATA
            >>> collection.filter(lambda entry: entry.source.url == 'https://doi.org/10.1039/C0CP01001D')   # doctest: +REMOTE_DATA
            [Entry('alves_2011_electrochemistry_6010_f1a_solid'), Entry('alves_2011_electrochemistry_6010_f2_red')]

        The folder containing the data in the zip can be specified with the :param data:.
        An output directory for the extracted data can be specified with the :param outdir:.
        """
        import unitpackage.local
        import unitpackage.remote

        package = Package()

        if url is None:
            data_packages = unitpackage.remote.collect_datapackages(
                data=data, outdir=outdir
            )
            resources = unitpackage.local.collect_resources(data_packages)

            for resource in resources:
                package.add_resource(resource)

            return cls(package=package)

        data_packages = unitpackage.remote.collect_datapackages(
            url=url, data=data, outdir=outdir
        )
        resources = unitpackage.local.collect_resources(data_packages)

        for resource in resources:
            package.add_resource(resource)

        return cls(package=package)
