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
from functools import cached_property

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

    @cached_property
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

        A derived collection includes only the bibliographic entries of the remaining entries::

            >>> collection.filter(lambda entry: entry.source.citationKey != 'alves_2011_electrochemistry_6010').bibliography
            BibliographyData(
              entries=OrderedCaseInsensitiveDict([
                ('engstfeld_2018_polycrystalline_17743', Entry('article',
                ...

        A collection with entries without bibliography::

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

    def __getitem__(self, key):
        r"""
        Return either
        * an entry with the given identifier or index in the collection, such as db['id'] or db[0].
        * a new collection with the entries selected by the slice or list of identifiers,
        such as db[1:2], db['id1', 'id2'], db[['id1', 'id2']].

        To return a collection with a single entry, provide a single identifier as a list or tuple,
        such as db[['id1']].

        EXAMPLES:

        An entry from an identifier::

            >>> collection = Collection.create_example()
            >>> collection['alves_2011_electrochemistry_6010_f1a_solid']
            Entry('alves_2011_electrochemistry_6010_f1a_solid')

            >>> collection['invalid_key']
            Traceback (most recent call last):
            ...
            KeyError: "No collection entry with identifier 'invalid_key'."

        An entry from an integer::

            >>> collection[0]
            Entry('alves_2011_electrochemistry_6010_f1a_solid')

            >>> collection[-1]
            Traceback (most recent call last):
            ...
            IndexError: Index -1 out of range for collection with 3 entries.

        A collection with a single entry from a single identifier or index::

            >>> collection[['alves_2011_electrochemistry_6010_f1a_solid']]
            [Entry('alves_2011_electrochemistry_6010_f1a_solid')]

            >>> collection[[0]]
            [Entry('alves_2011_electrochemistry_6010_f1a_solid')]

        A new collection with entries selected by a slice::

            >>> collection[1:2]
            [Entry('engstfeld_2018_polycrystalline_17743_f4b_1')]

            >>> collection[:2]
            [Entry('alves_2011_electrochemistry_6010_f1a_solid'), Entry('engstfeld_2018_polycrystalline_17743_f4b_1')]

            >>> collection[-1:2]
            Traceback (most recent call last):
            ...
            IndexError: slice(-1, 2, None) out of range for collection.

        A new collection with entries selected by a list of identifiers::

            >>> collection['alves_2011_electrochemistry_6010_f1a_solid', 'engstfeld_2018_polycrystalline_17743_f4b_1']
            [Entry('alves_2011_electrochemistry_6010_f1a_solid'), Entry('engstfeld_2018_polycrystalline_17743_f4b_1')]

            >>> collection['alves_2011_electrochemistry_6010_f1a_solid', 'invalid_key']
            Traceback (most recent call last):
            ...
            KeyError: "The provided identifiers ['invalid_key'], are invalid for this collection."

            >>> collection[['alves_2011_electrochemistry_6010_f1a_solid', 'invalid_key']]
            Traceback (most recent call last):
            ...
            KeyError: "The provided identifiers ['invalid_key'], are invalid for this collection."

            >>> collection['invalid_key', 'invalid_key2']
            Traceback (most recent call last):
            ...
            KeyError: "The provided identifiers ['invalid_key', 'invalid_key2'], are invalid for this collection."

        A new collection with entries selected by a list of indices::

            >>> collection[0, 1]
            [Entry('alves_2011_electrochemistry_6010_f1a_solid'), Entry('engstfeld_2018_polycrystalline_17743_f4b_1')]

            >>> collection[[0, 1]]
            [Entry('alves_2011_electrochemistry_6010_f1a_solid'), Entry('engstfeld_2018_polycrystalline_17743_f4b_1')]

            >>> collection[[-1, 0, 1]]
            Traceback (most recent call last):
            ...
            IndexError: Index -1 out of range for collection.
        """
        identifiers = list(self.package.resource_names)

        # An integer or string returns an Entry object.
        if isinstance(key, int):
            return self._get_entry_by_int(key, identifiers)

        if isinstance(key, str):
            return self._get_entry_by_str(key, identifiers)

        # If the key is a slice, a new Collection is returned with the selected entries.
        if isinstance(key, slice):
            return self._get_collection_by_slice(key, identifiers)

        # If the key is a list or tuple, a new Collection is returned with the selected entries.
        if isinstance(key, (list, tuple)):
            if all(isinstance(k, int) for k in key):
                return self._get_collection_by_int_list(key, identifiers)
            if all(isinstance(k, str) for k in key):
                return self._get_collection_by_str_list(key, identifiers)

        raise TypeError(
            f"{key} of type {type(key)} is invalid. Expected int, str, slice, "
            "list (with identifiers) or tuple (with identifiers)."
        )

    def _get_entry_by_int(self, index, identifiers):
        """
        Retrieve an Entry by integer index.

        Raises IndexError if the index is out of bounds.

        Examples::

            >>> collection = Collection.create_example()
            >>> collection._get_entry_by_int(0, list(collection.package.resource_names))
            Entry('alves_2011_electrochemistry_6010_f1a_solid')

            >>> collection._get_entry_by_int(-1, list(collection.package.resource_names))
            Traceback (most recent call last):
            ...
            IndexError: Index -1 out of range for collection with 3 entries.
        """
        if index < 0 or index >= len(identifiers):
            raise IndexError(
                f"Index {index} out of range for collection with {len(identifiers)} entries."
            )

        return self.Entry(self.package.get_resource(identifiers[index]))

    def _get_entry_by_str(self, identifier, identifiers):
        """
        Retrieve an Entry by string identifier.

        Raises KeyError if the identifier is not found.

        Examples::

            >>> collection = Collection.create_example()
            >>> collection._get_entry_by_str('alves_2011_electrochemistry_6010_f1a_solid', list(collection.package.resource_names))
            Entry('alves_2011_electrochemistry_6010_f1a_solid')

            >>> collection._get_entry_by_str('invalid_key', list(collection.package.resource_names))
            Traceback (most recent call last):
            ...
            KeyError: "No collection entry with identifier 'invalid_key'."
        """
        if identifier not in identifiers:
            raise KeyError(f"No collection entry with identifier '{identifier}'.")

        return self.Entry(self.package.get_resource(identifier))

    def _get_collection_by_slice(self, slc, identifiers):
        """
        Return a new Collection with entries selected by slice.

        Raises IndexError if slice bounds are invalid.

        Examples::

            >>> collection = Collection.create_example()
            >>> new_coll = collection._get_collection_by_slice(slice(1, 2), list(collection.package.resource_names))
            >>> [entry.identifier for entry in new_coll]
            ['engstfeld_2018_polycrystalline_17743_f4b_1']

            >>> collection._get_collection_by_slice(slice(-1, 2), list(collection.package.resource_names))
            Traceback (most recent call last):
            ...
            IndexError: slice(-1, 2, None) out of range for collection.

            >>> new_coll = collection._get_collection_by_slice(slice(None, 2), list(collection.package.resource_names))
            >>> [entry.identifier for entry in new_coll]
            ['alves_2011_electrochemistry_6010_f1a_solid', 'engstfeld_2018_polycrystalline_17743_f4b_1']

        """
        if slc.start is not None and slc.start < 0:
            raise IndexError(f"{slc} out of range for collection.")
        if slc.stop is not None and slc.stop > len(identifiers):
            raise IndexError(f"{slc} out of range for collection.")
        selected_identifiers = identifiers[slc]
        package = Package()
        for identifier in selected_identifiers:
            package.add_resource(self.package.get_resource(identifier))
        return type(self)(package=package)

    def _get_collection_by_int_list(self, indices, identifiers):
        """
        Return a new Collection with entries selected by a list of integer indices.

        Raises IndexError if any index is out of bounds.

        Examples::

            >>> collection = Collection.create_example()
            >>> new_coll = collection._get_collection_by_int_list([0, 1], list(collection.package.resource_names))
            >>> [entry.identifier for entry in new_coll]
            ['alves_2011_electrochemistry_6010_f1a_solid', 'engstfeld_2018_polycrystalline_17743_f4b_1']

            >>> collection._get_collection_by_int_list([-1, 0, 1], list(collection.package.resource_names))
            Traceback (most recent call last):
            ...
            IndexError: Index -1 out of range for collection.
        """
        package = Package()
        for index in indices:
            if index < 0 or index >= len(identifiers):
                raise IndexError(f"Index {index} out of range for collection.")
            package.add_resource(self.package.get_resource(identifiers[index]))
        return type(self)(package=package)

    def _get_collection_by_str_list(self, names, identifiers):
        """
        Return a new Collection with entries selected by a list or tuple of string identifiers.

        Raises KeyError if none of the provided identifiers are valid.
        Logs a warning for each invalid identifier.

        Examples::

            >>> collection = Collection.create_example()
            >>> new_coll = collection._get_collection_by_str_list(
            ...     ['alves_2011_electrochemistry_6010_f1a_solid', 'engstfeld_2018_polycrystalline_17743_f4b_1'],
            ...     list(collection.package.resource_names))
            >>> [entry.identifier for entry in new_coll]
            ['alves_2011_electrochemistry_6010_f1a_solid', 'engstfeld_2018_polycrystalline_17743_f4b_1']

            >>> new_coll_partial = collection._get_collection_by_str_list(
            ...     ['alves_2011_electrochemistry_6010_f1a_solid', 'invalid_key'],
            ...     list(collection.package.resource_names))
            Traceback (most recent call last):
            ...
            KeyError: "The provided identifiers ['invalid_key'], are invalid for this collection."

            >>> collection._get_collection_by_str_list(['invalid_key1', 'invalid_key2'], list(collection.package.resource_names))
            Traceback (most recent call last):
            ...
            KeyError: "The provided identifiers ['invalid_key1', 'invalid_key2'], are invalid for this collection."
        """
        package = Package()
        invalid = []
        for name in names:
            if name not in identifiers:
                invalid.append(name)
            else:
                package.add_resource(self.package.get_resource(name))
        if len(invalid) != 0:
            raise KeyError(
                f"The provided identifiers {invalid}, are invalid for this collection."
            )
        return type(self)(package=package)

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

        package = Package(filename)

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

    @property
    def identifiers(self):
        """Return a list of identifiers of the collection,
        i.e., the names of the resources in the datapackage.

        This method is basically equivalent to `package.resource_names`.

        EXAMPLES::

            >>> collection = Collection.create_example()
            >>> len(collection.identifiers)
            3

        """
        return self.package.resource_names
