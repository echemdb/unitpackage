r"""
A frictionless tabular Resource describing tabulated data for which the units of the
column names (`pandas <https://pandas.pydata.org/>`_)
or fields (`frictionless <https://framework.frictionlessdata.io/>`_) are known
and the resource has additional metadata describing the underlying data.

A description of such resources can be found in the documentation
in :doc:`/usage/unitpackage`.

Resources are the individual elements of a :class:`~unitpackage.collection.Collection` and
are denoted as ``entry``.

EXAMPLES:

Metadata included in an entry is accessible as an attribute::

    >>> from unitpackage.entry import Entry
    >>> entry = Entry.create_examples()[0]
    >>> entry.echemdb.source # doctest: +ELLIPSIS +NORMALIZE_WHITESPACE
    {'citationKey': 'alves_2011_electrochemistry_6010',
    'url': 'https://doi.org/10.1039/C0CP01001D',
    'figure': '1a',
    'curve': 'solid',
    'bibdata': '@article{alves_2011_electrochemistry_6010,...}

The data of the entry can be called as a pandas dataframe::

    >>> entry = Entry.create_examples()[0]
    >>> entry.df
                  t         E         j
    0      0.000000 -0.103158 -0.998277
    1      0.020000 -0.102158 -0.981762
    ...

Entries can be created from from various sources, such as csv files or pandas dataframes::

    >>> entry = Entry.from_csv(csvname='examples/from_csv/from_csv.csv')
    >>> entry
    Entry('from_csv')

Information on the fields such as units can be updated::

    >>> fields = [{'name':'E', 'unit': 'mV'}, {'name':'I', 'unit': 'A'}]
    >>> entry = entry.update_fields(fields=fields)
    >>> entry.fields # doctest: +NORMALIZE_WHITESPACE
    [{'name': 'E', 'type': 'integer', 'unit': 'mV'},
    {'name': 'I', 'type': 'integer', 'unit': 'A'}]

Metadata to the resource can be updated in-place::

    >>> metadata = {'echemdb': {'source': {'citationKey': 'new_key'}}}
    >>> entry.metadata.from_dict(metadata)
    >>> entry.metadata
    {'echemdb': {'source': {'citationKey': 'new_key'}}}


"""

# ********************************************************************
#  This file is part of unitpackage.
#
#        Copyright (C) 2021-2026 Albert Engstfeld
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
import logging
import os.path

from unitpackage.descriptor import Descriptor
from unitpackage.metadata import MetadataDescriptor

logger = logging.getLogger("unitpackage")


class Entry:
    r"""
    A `frictionless Resource <https://github.com/frictionlessdata/frictionless-py>`_
    describing tabulated data.

    EXAMPLES:

    Entries can be directly created from a frictionless Data Package containing a single
    frictionless Resource::

        >>> from unitpackage.entry import Entry
        >>> entry = Entry.from_local('./examples/local/no_bibliography/no_bibliography.json')
        >>> entry
        Entry('no_bibliography')

    or directly form a frictionless Resource::

        >>> from unitpackage.entry import Entry
        >>> from frictionless import Resource
        >>> entry = Entry(Resource('./examples/local/no_bibliography/no_bibliography.json'))
        >>> entry
        Entry('no_bibliography')

    Entries can also be created by other means such as,
    a CSV ``Entry.from_csv`` or a pandas dataframe ``Entry.from_df``.

    Normally, entries are obtained by opening a :class:`~unitpackage.collection.Collection` of entries::

        >>> from unitpackage.collection import Collection
        >>> collection = Collection.create_example()
        >>> entry = next(iter(collection))

    """

    default_metadata_key = ""
    """Default metadata key to use when accessing the descriptor.
    If empty string, the entire metadata dict is used. Subclasses can override this."""

    def __init__(self, resource):
        self.resource = resource

    @property
    def metadata(self):
        r"""
        Access and manage entry metadata.

        Returns a MetadataDescriptor that supports both dict and attribute-style access.
        Allows loading metadata from various sources. Modifications are applied in-place.

        EXAMPLES::

            >>> entry = Entry.create_examples()[0]
            >>> entry.metadata['echemdb']['source']['citationKey']
            'alves_2011_electrochemistry_6010'

            >>> entry.metadata.echemdb['source']['citationKey']
            'alves_2011_electrochemistry_6010'

        Load metadata from a dict::

            >>> new_entry = Entry.create_examples()[0]
            >>> new_entry.metadata.from_dict({'echemdb': {'test': 'data'}})
            >>> new_entry.metadata['echemdb']['test']
            'data'

        """
        return MetadataDescriptor(self)

    def load_metadata(self, filename, file_format=None, key=None):
        r"""
        Load metadata from a file and return self for method chaining.

        The file format is auto-detected from the extension if not specified.
        Supported formats are 'yaml' and 'json'.

        EXAMPLES:

        Load metadata from a YAML file::

            >>> import os
            >>> import tempfile
            >>> import yaml
            >>> entry = Entry.create_examples()[0]
            >>> with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            ...     yaml.dump({'source': {'citationKey': 'chain_test'}}, f)
            ...     temp_path = f.name
            >>> entry.load_metadata(temp_path, key='echemdb').metadata.echemdb.source.citationKey
            'chain_test'
            >>> os.unlink(temp_path)

        Load metadata from a JSON file with auto-detection::

            >>> import os
            >>> import json
            >>> import tempfile
            >>> entry = Entry.create_examples()[0]
            >>> with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            ...     json.dump({'custom': {'data': 'value'}}, f)
            ...     temp_path = f.name
            >>> entry.load_metadata(temp_path).metadata.custom.data
            'value'
            >>> os.unlink(temp_path)


        """
        # Auto-detect format from file extension if not specified
        if file_format is None:
            if filename.endswith(".yaml") or filename.endswith(".yml"):
                file_format = "yaml"
            elif filename.endswith(".json"):
                file_format = "json"
            else:
                raise ValueError(
                    f"Cannot auto-detect format for '{filename}'. "
                    "Please specify file_format='yaml' or file_format='json'"
                )

        # Load metadata using the appropriate method
        if file_format == "yaml":
            self.metadata.from_yaml(filename, key=key)
        elif file_format == "json":
            self.metadata.from_json(filename, key=key)
        else:
            raise ValueError(
                f"Unsupported format '{file_format}'. Use 'yaml' or 'json'"
            )

        return self

    @property
    def identifier(self):
        r"""
        Return a unique identifier for this entry, i.e., its basename.

        EXAMPLES::

            >>> entry = Entry.create_examples()[0]
            >>> entry.identifier
            'alves_2011_electrochemistry_6010_f1a_solid'

        """
        return self.resource.name

    def __dir__(self):
        r"""
        Return the attributes of this entry.

        Implement to support tab-completion into the Resource's descriptor.

        EXAMPLES::

            >>> entry = Entry.create_examples()[0]
            >>> dir(entry) # doctest: +ELLIPSIS +NORMALIZE_WHITESPACE
            [... 'create_examples', 'default_metadata_key', 'df', 'echemdb', 'field_unit',
            'fields', 'from_csv', 'from_df', 'from_local', 'identifier', 'load_metadata',
            'metadata', 'plot', 'remove_column', 'remove_columns', 'rename_field', 'rename_fields',
            'rescale', 'resource', 'save', 'update_fields', 'yaml']

        """
        return list(set(dir(self._descriptor) + object.__dir__(self)))

    def __getattr__(self, name):
        r"""
        Return a property of the Resource's descriptor.

        EXAMPLES::

            >>> entry = Entry.create_examples()[0]
            >>> entry.echemdb.source # doctest: +ELLIPSIS +NORMALIZE_WHITESPACE
            {'citationKey': 'alves_2011_electrochemistry_6010',
            'url': 'https://doi.org/10.1039/C0CP01001D',
            'figure': '1a',
            'curve': 'solid',
            'bibdata': '@article{alves_2011_electrochemistry_6010,...}

        The returned descriptor can again be accessed in the same way::

            >>> entry.echemdb.system.electrolyte.components[0].name
            'H2O'

        """
        return getattr(self._descriptor, name)

    def __getitem__(self, name):
        r"""
        Return a property of the Resource's descriptor.

        EXAMPLES::

            >>> entry = Entry.create_examples()[0]
            >>> entry["echemdb"]["source"] # doctest: +NORMALIZE_WHITESPACE
            {'citationKey': 'alves_2011_electrochemistry_6010',
            'url': 'https://doi.org/10.1039/C0CP01001D',
            'figure': '1a',
            'curve': 'solid',
            'bibdata': '@article{alves_2011_electrochemistry_6010,...}

        """
        return self._descriptor[name]

    @property
    def _descriptor(self):
        r"""
        Return a Descriptor object wrapping the entry's metadata.

        The metadata structure depends on the :attr:`default_metadata_key` class attribute:

        - If ``default_metadata_key`` is an empty string (default in :class:`Entry`),
          the entire ``metadata`` dict is wrapped as the descriptor.
        - If ``default_metadata_key`` is set to a non-empty string (e.g., "echemdb" in subclasses),
          the descriptor wraps only the metadata under that specific key.

        This allows subclasses to work with different metadata structures while maintaining
        a consistent interface through the Descriptor class.

        EXAMPLES::

            >>> entry = Entry.create_examples()[0]
            >>> entry._descriptor # doctest: +ELLIPSIS
            {'echemdb': ...}

            >>> entry.echemdb.source.citationKey
            'alves_2011_electrochemistry_6010'


        """
        return Descriptor(self._default_metadata)

    @property
    def _metadata(self):
        r"""
        Returns the metadata associated with this entry.

        The metadata may contain keys which nest entire metadata schemas (e.g., "echemdb", "myExperiment", etc.).
        Use :attr:`_default_metadata` to access the subset determined by :attr:`default_metadata_key`.

        EXAMPLES::

            >>> entry = Entry.create_examples()[0]
            >>> entry._metadata # doctest: +ELLIPSIS +NORMALIZE_WHITESPACE
            {...'echemdb': {...'source': {'citationKey': 'alves_2011_electrochemistry_6010',...}...}

        """
        return self.resource.custom.setdefault("metadata", {})

    @property
    def _default_metadata(self):
        r"""
        Returns the metadata subset based on :attr:`default_metadata_key`.

        If :attr:`default_metadata_key` is empty, returns the entire metadata dict.
        Otherwise, returns the metadata under the specified key.

        This is useful for subclasses that want to work with a specific metadata structure.

        EXAMPLES::

            >>> entry = Entry.create_examples()[0]
            >>> entry._default_metadata # doctest: +ELLIPSIS +NORMALIZE_WHITESPACE
            {...'echemdb': {...'source': {'citationKey': 'alves_2011_electrochemistry_6010',...}...}

        """
        metadata = self._metadata
        if self.default_metadata_key and self.default_metadata_key in metadata:
            return metadata[self.default_metadata_key]
        return metadata

    @property
    def fields(self):
        r"""
        Return the fields of the resource's schema.

        This is a convenience property that returns `self.resource.schema.fields`.

        EXAMPLES::

            >>> entry = Entry.create_examples()[0]
            >>> entry.fields
            [{'name': 't', 'type': 'number', 'unit': 's'},
            {'name': 'E', 'type': 'number', 'unit': 'V', 'reference': 'RHE'},
            {'name': 'j', 'type': 'number', 'unit': 'A / m2'}]

        """
        return self.resource.schema.fields

    def field_unit(self, field_name):
        r"""
        Return the unit of the ``field_name`` of the resource.

        EXAMPLES::

            >>> entry = Entry.create_examples()[0]
            >>> entry.field_unit('E')
            'V'

        """
        field = self.resource.schema.get_field(field_name).custom.get("unit", "")
        if not field:
            logger.warning(f"Field {field_name} has no unit.")
            return ""

        return field

    def rescale(self, units):
        r"""
        Returns a rescaled :class:`~unitpackage.entry.Entry` with axes in the specified ``units``.
        Provide a dict, where the key is the axis name and the value
        the new unit, such as `{'j': 'uA / cm2', 't': 'h'}`.

        EXAMPLES:

        The units without any rescaling::

            >>> entry = Entry.create_examples()[0]
            >>> entry.fields
            [{'name': 't', 'type': 'number', 'unit': 's'},
            {'name': 'E', 'type': 'number', 'unit': 'V', 'reference': 'RHE'},
            {'name': 'j', 'type': 'number', 'unit': 'A / m2'}]

        A rescaled entry using different units::

            >>> rescaled_entry = entry.rescale({'j':'uA / cm2', 't':'h'})
            >>> rescaled_entry.fields
            [{'name': 't', 'type': 'number', 'unit': 'h'},
            {'name': 'E', 'type': 'number', 'unit': 'V', 'reference': 'RHE'},
            {'name': 'j', 'type': 'number', 'unit': 'uA / cm2'}]

        The values in the data frame are scaled to match the new units::

            >>> rescaled_entry.df
                         t         E          j
            0     0.000000 -0.103158 -99.827664
            1     0.000006 -0.102158 -98.176205
            ...

        """
        from collections.abc import Mapping

        if not isinstance(units, Mapping):
            raise ValueError(
                "'units' must have the format {'dimension': 'new unit'}, e.g., `{'j': 'uA / cm2', 't': 'h'}`"
            )

        if not units:
            units = {}

        from astropy import units as u

        # Get current dataframe and schema
        df = self.df.copy()
        fields = self.fields

        # Apply rescaling to dataframe
        for field in fields:
            if field.name in units:
                df[field.name] *= u.Unit(field.custom["unit"]).to(
                    u.Unit(units[field.name])
                )

        # Create new resource with rescaled data and updated units
        field_updates = {name: {"unit": unit} for name, unit in units.items()}
        new_resource = self._create_new_df_resource(df, field_updates=field_updates)

        return type(self)(resource=new_resource)

    def add_offset(self, field_name=None, offset=None, unit=""):
        r"""
        Return an entry with an offset (with specified units) to a specified field of the entry.
        The offset properties are stored in the fields metadata.

        If offsets are applied consecutively, the value is updated.

        EXAMPLES::

            >>> from unitpackage.entry import Entry
            >>> entry = Entry.create_examples()[0]
            >>> entry.df.head() # doctest: +NORMALIZE_WHITESPACE
                  t         E         j
            0  0.00 -0.103158 -0.998277
            1  0.02 -0.102158 -0.981762
            ...

            >>> new_entry = entry.add_offset('E', 0.1, 'V')
            >>> new_entry.df.head() # doctest: +NORMALIZE_WHITESPACE
                  t         E         j
            0  0.00 -0.003158 -0.998277
            1  0.02 -0.002158 -0.981762
            ...

            >>> new_entry.resource.schema.get_field('E') # doctest: +NORMALIZE_WHITESPACE
            {'name': 'E',
            'type': 'number',
            'unit': 'V',
            'reference': 'RHE',
            'offset': {'value': 0.1, 'unit': 'V'}}

        An offset with a different unit than that of the field.::

            >>> new_entry = entry.add_offset('E', 250, 'mV')
            >>> new_entry.df.head() # doctest: +NORMALIZE_WHITESPACE
                  t         E         j
            0  0.00  0.146842 -0.998277
            1  0.02  0.147842 -0.981762
            ...

        A consecutively added offset::

            >>> new_entry_1 = new_entry.add_offset('E', 0.150, 'V')
            >>> new_entry_1.df.head() # doctest: +NORMALIZE_WHITESPACE
                  t         E         j
            0  0.00  0.296842 -0.998277
            1  0.02  0.297842 -0.981762
            ...

            >>> new_entry_1.resource.schema.get_field('E') # doctest: +NORMALIZE_WHITESPACE
            {'name': 'E',
            'type': 'number',
            'unit': 'V',
            'reference': 'RHE',
            'offset': {'value': 0.4, 'unit': 'V'}}

        If no unit is provided, the field unit is used instead.::

            >>> new_entry_2 = new_entry.add_offset('E', 0.150)
            >>> new_entry_2.df.head() # doctest: +NORMALIZE_WHITESPACE
                  t         E         j
            0  0.00  0.296842 -0.998277
            1  0.02  0.297842 -0.981762
            ...


        """
        import astropy.units as u

        field = self.resource.schema.get_field(field_name)

        if field.custom.get("unit") and not unit:
            logger.warning(
                f"""No unit provided for the offset, using field unit '{field.custom.get("unit")}' instead."""
            )
            unit = field.custom.get("unit")

        field_unit = u.Unit(field.custom.get("unit"))

        # create a new dataframe with offset values
        df = self.df.copy()
        offset_quantity = (offset * u.Unit(unit)).to(u.Unit(field_unit))
        df[field_name] += offset_quantity.value

        # Calculate the new offset value
        old_offset_quantity = field.custom.get("offset", {}).get("value", 0.0) * u.Unit(
            field.custom.get("offset", {}).get("unit", field.custom.get("unit"))
        )
        new_offset = old_offset_quantity.value + offset_quantity.value

        # Create new resource with offset metadata
        field_updates = {
            field_name: {
                "offset": {
                    "value": float(new_offset),
                    "unit": str(offset_quantity.unit),
                }
            }
        }
        new_resource = self._create_new_df_resource(df, field_updates=field_updates)

        return type(self)(resource=new_resource)

    def _create_new_df_resource(self, df, schema=None, field_updates=None):
        r"""
        Create a new dataframe resource from a dataframe, preserving metadata and schema.

        Args:
            df: pandas DataFrame to create resource from
            schema: Optional schema descriptor dict. If None, copies schema from original resource
            field_updates: Optional dict mapping field names to update dicts

        Returns:
            A new frictionless Resource

        EXAMPLES::

            >>> entry = Entry.create_examples()[0]
            >>> df = entry.df.copy()
            >>> new_resource = entry._create_new_df_resource(df)
            >>> new_resource.name == entry.resource.name
            True
        """
        from frictionless import Resource, Schema

        new_resource = Resource(df)
        new_resource.infer()
        new_resource.name = self.resource.name

        if schema is not None:
            # Use the provided schema
            new_resource.schema = Schema.from_descriptor(schema, allow_invalid=True)
        else:
            # Copy schema from original resource
            for field_obj in self.resource.schema.fields:
                field_dict = field_obj.to_dict()
                # Apply any field-specific updates
                if field_updates and field_obj.name in field_updates:
                    field_dict.update(field_updates[field_obj.name])
                new_resource.schema.update_field(field_obj.name, field_dict)

        # Copy metadata to new resource
        new_resource.custom["metadata"] = self.resource.custom.get("metadata", {})

        return new_resource

    def _ensure_df_resource(self):
        r"""
        Ensure the resource is a pandas dataframe resource and return it.
        If the resource is a CSV resource, convert it to pandas format.

        EXAMPLES::

            >>> entry = Entry.create_examples()[0]
            >>> resource = entry._ensure_df_resource()
            >>> resource.format
            'pandas'
        """
        if self.resource.format == "pandas":
            return self.resource

        if self.resource.format == "csv":
            from unitpackage.local import create_df_resource_from_tabular_resource

            # Create pandas resource from CSV
            df_resource = create_df_resource_from_tabular_resource(self.resource)
            # Copy schema from original resource
            from frictionless import Schema

            df_resource.schema = Schema.from_descriptor(self.resource.schema.to_dict())
            return df_resource

        raise ValueError(
            f"Cannot convert resource of format '{self.resource.format}' to pandas dataframe."
        )

    @property
    def df(self):
        r"""
        Return the data of this entry's resource as a data frame.

        EXAMPLES::

            >>> entry = Entry.create_examples()[0]
            >>> entry.df
                          t         E         j
            0      0.000000 -0.103158 -0.998277
            1      0.020000 -0.102158 -0.981762
            ...

        The units and descriptions of the axes in the data frame can be recovered::

            >>> entry.fields # doctest: +NORMALIZE_WHITESPACE
            [{'name': 't', 'type': 'number', 'unit': 's'},
            {'name': 'E', 'type': 'number', 'unit': 'V', 'reference': 'RHE'},
            {'name': 'j', 'type': 'number', 'unit': 'A / m2'}]

        TESTS::

            >>> import pandas as pd
            >>> from unitpackage.entry import Entry
            >>> df = pd.DataFrame({'x':[1,2,3], 'y':[2,3,4]})
            >>> entry = Entry.from_df(df=df, basename='test_df')
            >>> entry.df
               x  y
            0  1  2
            1  2  3
            2  3  4

        """
        return self._ensure_df_resource().data

    def add_columns(self, df, new_fields):
        r"""
        Adds a column to the dataframe with specified field properties
        and returns an updated entry.

        EXAMPLES::

            >>> entry = Entry.create_examples()[0]
            >>> entry.df
                          t         E         j
            0      0.000000 -0.103158 -0.998277
            1      0.020000 -0.102158 -0.981762
            ...

        The units and descriptions of the axes in the data frame can be recovered::

            >>> import pandas as pd
            >>> import astropy.units as u
            >>> df = pd.DataFrame()
            >>> df['P/A'] = entry.df['E'] * entry.df['j']
            >>> new_field_unit = u.Unit(entry.field_unit('E')) * u.Unit(entry.field_unit('j'))
            >>> new_entry = entry.add_columns(df['P/A'], new_fields=[{'name':'P/A', 'unit': new_field_unit}])
            >>> new_entry.df
                          t         E         j       P/A
            0      0.000000 -0.103158 -0.998277  0.102981
            1      0.020000 -0.102158 -0.981762  0.100295
            ...

            >>> new_entry.field_unit('P/A')
            Unit("A V / m2")

        TESTS:

        Validate that the identifier is preserved::

            >>> new_entry.identifier
            'alves_2011_electrochemistry_6010_f1a_solid'

        """
        import pandas as pd
        from frictionless import Field, Schema

        df_ = pd.concat([self.df, df], axis=1)

        # Create new schema with added fields using frictionless method
        new_schema = Schema.from_descriptor(self.resource.schema.to_dict())

        # Add new fields using schema.add_field()
        for field_descriptor in new_fields:
            field = Field.from_descriptor(field_descriptor)
            new_schema.add_field(field)

        # Create new entry with updated schema
        new_resource = self._create_new_df_resource(df_, schema=new_schema.to_dict())
        entry = type(self)(resource=new_resource)
        entry.metadata.from_dict(self._metadata)

        return entry

    def remove_column(self, field_name):
        r"""
        Removes a single column from the dataframe
        and returns an updated entry.

        EXAMPLES::

            >>> entry = Entry.create_examples()[0]
            >>> entry.df
                          t         E         j
            0      0.000000 -0.103158 -0.998277
            1      0.020000 -0.102158 -0.981762
            ...

            >>> new_entry = entry.remove_column('E')
            >>> new_entry.df
                          t         j
            0      0.000000 -0.998277
            1      0.020000 -0.981762
            ...

            >>> 'E' in new_entry.df.columns
            False

        """
        from frictionless import Schema

        # Remove column from dataframe
        df = self.df.copy()
        df.drop(columns=[field_name], inplace=True)

        # Create new schema and remove field using frictionless method
        new_schema = Schema.from_descriptor(self.resource.schema.to_dict())
        if field_name in [field.name for field in new_schema.fields]:
            new_schema.remove_field(field_name)

        # Create new entry with updated schema
        new_resource = self._create_new_df_resource(df, schema=new_schema.to_dict())
        entry = type(self)(resource=new_resource)
        entry.metadata.from_dict(self._metadata)

        return entry

    def remove_columns(self, *field_names):
        r"""
        Removes specified columns from the dataframe
        and returns an updated entry.

        EXAMPLES::

            >>> entry = Entry.create_examples()[0]
            >>> entry.df
                          t         E         j
            0      0.000000 -0.103158 -0.998277
            1      0.020000 -0.102158 -0.981762
            ...

            >>> new_entry = entry.remove_columns('E', 'j')
            >>> new_entry.df
                          t
            0      0.000000
            1      0.020000
            ...

            >>> 'E' in new_entry.df.columns
            False

        """
        result = self
        for field_name in field_names:
            result = result.remove_column(field_name)
        return result

    def __repr__(self):
        r"""
        Return a printable representation of this entry.

        EXAMPLES::

            >>> entry = Entry.create_examples()[0]
            >>> entry
            Entry('alves_2011_electrochemistry_6010_f1a_solid')

        """
        return f"Entry({repr(self.identifier)})"

    @classmethod
    def create_examples(cls, name=""):
        r"""
        Return some example entries for use in automated tests.

        The examples are created from Data Packages in the unitpackage's examples directory.
        These are only available from the development environment.

        EXAMPLES::

            >>> Entry.create_examples()
            [Entry('alves_2011_electrochemistry_6010_f1a_solid'), Entry('engstfeld_2018_polycrystalline_17743_f4b_1'), Entry('no_bibliography')]

        An entry without associated BIB file.

            >>> Entry.create_examples(name="no_bibliography")
            [Entry('no_bibliography')]

        """
        example_dir = os.path.join(
            os.path.dirname(__file__), "..", "examples", "local", name
        )

        if not os.path.exists(example_dir):
            raise ValueError(
                f"No subdirectory in examples/ for {name}, i.e., could not find {example_dir}."
            )

        from unitpackage.local import collect_datapackages

        packages = collect_datapackages(example_dir)

        if len(packages) == 0:
            from glob import glob

            raise ValueError(
                f"No literature data found for {name}. The directory for this data {example_dir} exists. But we could not find any datapackages in there. "
                f"There is probably some outdated data in {example_dir}. The contents of that directory are: { glob(os.path.join(example_dir,'**')) }"
            )

        from unitpackage.local import collect_resources

        return [cls(resource=resource) for resource in collect_resources(packages)]

    def plot(self, x_label=None, y_label=None, name=None):
        r"""
        Return a 2D plot of this entry.

        The default plot is constructed from the first two columns of the dataframe.

        EXAMPLES::

            >>> entry = Entry.create_examples()[0]
            >>> entry.plot()
            Figure(...)

        The 2D plot can also be returned with custom axis units available in the resource::

            >>> entry.plot(x_label='j', y_label='E')
            Figure(...)

        A plot from data without units::

            >>> import pandas as pd
            >>> data = {'t': [0, 1, 2], 'E': [0.0, 1.0, 2.0]}
            >>> df = pd.DataFrame(data)
            >>> entry = Entry.from_df(df=df, basename='test_df')
            >>> entry.plot()
            Figure(...)

        """
        import plotly.graph_objects

        x_label = x_label or self.df.columns[0]
        y_label = y_label or self.df.columns[1]

        fig = plotly.graph_objects.Figure()

        fig.add_trace(
            plotly.graph_objects.Scatter(
                x=self.df[x_label],
                y=self.df[y_label],
                mode="lines",
                name=name or self.identifier,
            )
        )

        x_unit = self.field_unit(x_label)
        y_unit = self.field_unit(y_label)

        fig.update_layout(
            template="simple_white",
            showlegend=True,
            autosize=True,
            width=600,
            height=400,
            margin={"l": 70, "r": 70, "b": 70, "t": 70, "pad": 7},
            xaxis_title=f"{x_label} [{x_unit}]" if x_unit else x_label,
            yaxis_title=f"{y_label} [{y_unit}]" if y_unit else y_label,
        )

        fig.update_xaxes(showline=True, mirror=True)
        fig.update_yaxes(showline=True, mirror=True)

        return fig

    def update_fields(self, fields):
        r"""
        Return a new entry with updated fields in the resource.

        The :param fields: list must must be structured such as
        `[{'name':'E', 'unit': 'mV'}, {'name':'T', 'unit': 'K'}]`.

        EXAMPLES::

            >>> from unitpackage.entry import Entry
            >>> entry = Entry.create_examples()[0]
            >>> entry.fields # doctest: +NORMALIZE_WHITESPACE
            [{'name': 't', 'type': 'number', 'unit': 's'},
            {'name': 'E', 'type': 'number', 'unit': 'V', 'reference': 'RHE'},
            {'name': 'j', 'type': 'number', 'unit': 'A / m2'}]

        Updating the fields returns a new entry with updated field metadata::

            >>> fields = [{'name':'E', 'unit': 'mV'},
            ... {'name':'j', 'unit': 'uA / cm2'},
            ... {'name':'x', 'unit': 'm'}]
            >>> new_entry = entry.update_fields(fields)
            >>> new_entry.fields # doctest: +NORMALIZE_WHITESPACE
            [{'name': 't', 'type': 'number', 'unit': 's'},
            {'name': 'E', 'type': 'number', 'unit': 'mV', 'reference': 'RHE'},
            {'name': 'j', 'type': 'number', 'unit': 'uA / cm2'}]

        The original entry remains unchanged::

            >>> entry.fields # doctest: +NORMALIZE_WHITESPACE
            [{'name': 't', 'type': 'number', 'unit': 's'},
            {'name': 'E', 'type': 'number', 'unit': 'V', 'reference': 'RHE'},
            {'name': 'j', 'type': 'number', 'unit': 'A / m2'}]

        """
        from frictionless import Schema

        # Get the dataframe and create a new schema
        df = self.df.copy()
        new_schema = Schema.from_descriptor(self.resource.schema.to_dict())

        # Update fields using schema.update_field()
        for field_descriptor in fields:
            field_name = field_descriptor.get("name")
            if field_name and field_name in [field.name for field in new_schema.fields]:
                # Extract the updates (excluding 'name' since update_field takes name separately)
                updates = {k: v for k, v in field_descriptor.items() if k != "name"}
                new_schema.update_field(field_name, updates)

        # Create new resource with updated schema
        new_resource = self._create_new_df_resource(df, schema=new_schema.to_dict())

        return type(self)(resource=new_resource)

    @classmethod
    def from_csv(
        cls,
        csvname,
        encoding=None,
        header_lines=None,
        column_header_lines=None,
        decimal=None,
        delimiters=None,
    ):
        r"""
        Returns an entry constructed from a CSV.

        EXAMPLES::

            >>> from unitpackage.entry import Entry
            >>> entry = Entry.from_csv(csvname='examples/from_csv/from_csv.csv')
            >>> entry
            Entry('from_csv')

            >>> entry.resource # doctest: +NORMALIZE_WHITESPACE
            {'name': 'from_csv',
            ...

        .. important::
            Upper case filenames are converted to lower case entry identifiers!

        A filename containing upper case characters::

            >>> entry = Entry.from_csv(csvname='examples/from_csv/UpperCase.csv')
            >>> entry
            Entry('uppercase')

        Casing in the filename is preserved in the metadata::

            >>> entry.resource # doctest: +NORMALIZE_WHITESPACE
            {'name': 'uppercase',
            'type': 'table',
            'path': 'UpperCase.csv',
            ...

        CSV with a more complex structure, such as multiple header lines can be constructed::

            >>> filename = 'examples/from_csv/from_csv_multiple_headers.csv'
            >>> entry = Entry.from_csv(csvname='examples/from_csv/from_csv_multiple_headers.csv', column_header_lines=2)
            >>> entry.resource # doctest: +NORMALIZE_WHITESPACE
            {'name': 'from_csv_multiple_headers',
            'type': 'table',
            'data': [],
            'format': 'pandas',
            'mediatype': 'application/pandas',
            'schema': {'fields': [{'name': 'E / V', 'type': 'integer'},
                                {'name': 'j / A / cm2', 'type': 'integer'}]}}

        """
        from unitpackage.local import create_tabular_resource_from_csv

        # pylint: disable=duplicate-code
        resource = create_tabular_resource_from_csv(
            csvname=csvname,
            encoding=encoding,
            header_lines=header_lines,
            column_header_lines=column_header_lines,
            decimal=decimal,
            delimiters=delimiters,
        )

        from pathlib import Path

        if resource.name == "memory":
            resource.name = Path(
                csvname
            ).stem.lower()  # Use stem (filename without extension)

        return cls(resource)

    @classmethod
    def _modify_field_name(cls, field, old_name, new_name, keep_original_name_as=None):
        r"""Modifies a single field's name if it matches the old_name.

        The original name can optionally be preserved in a custom field property.

        EXAMPLES::

            >>> field = {'name': '<E>', 'unit':'mV'}
            >>> Entry._modify_field_name(field, '<E>', 'E', keep_original_name_as='original')
            {'name': 'E', 'unit': 'mV', 'original': '<E>'}

            >>> field = {'name': 'I', 'unit':'mA'}
            >>> Entry._modify_field_name(field, '<E>', 'E', keep_original_name_as='original')
            {'name': 'I', 'unit': 'mA'}

        """
        if field["name"] == old_name:
            if keep_original_name_as:
                field.setdefault(keep_original_name_as, old_name)
            field["name"] = new_name
        return field

    @classmethod
    def _modify_fields_names(cls, fields, name_mappings, keep_original_name_as=None):
        r"""Updates field names in a list of fields based on provided name mappings.

        The original field names can optionally be preserved in a custom property.

        EXAMPLES::

            >>> fields = [{'name': '<E>', 'unit':'mV'},{'name': 'I', 'unit':'mA'}]
            >>> name_mappings = {'<E>':'E'}
            >>> Entry._modify_fields_names(fields, name_mappings, keep_original_name_as='original')
            [{'name': 'E', 'unit': 'mV', 'original': '<E>'}, {'name': 'I', 'unit': 'mA'}]

        """
        for field in fields:
            for old_name, new_name in name_mappings.items():
                cls._modify_field_name(field, old_name, new_name, keep_original_name_as)
        return fields

    def rename_field(self, field_name, new_name, keep_original_name_as=None):
        r"""Returns a :class:`~unitpackage.entry.Entry` with a single renamed field and
        corresponding dataframe column name.

        The original field name can optionally be kept in a new key.

        EXAMPLES:

        The original dataframe::

            >>> from unitpackage.entry import Entry
            >>> entry = Entry.create_examples()[0]
            >>> entry.df
                          t         E         j
            0      0.000000 -0.103158 -0.998277
            1      0.020000 -0.102158 -0.981762
            ...

        Dataframe with a single modified column name::

            >>> renamed_entry = entry.rename_field('t', 't_rel', keep_original_name_as='originalName')
            >>> renamed_entry.df
                      t_rel         E         j
            0      0.000000 -0.103158 -0.998277
            1      0.020000 -0.102158 -0.981762
            ...

        Updated fields of the resource::

            >>> renamed_entry.fields
            [{'name': 't_rel', 'type': 'number', 'unit': 's', 'originalName': 't'},
            {'name': 'E', 'type': 'number', 'unit': 'V', 'reference': 'RHE'},
            {'name': 'j', 'type': 'number', 'unit': 'A / m2'}]

        TESTS:

        Renaming a non-existing field has no effect::

            >>> renamed_entry = entry.rename_field('x', 'y', keep_original_name_as='originalName')
            >>> renamed_entry.fields
            [{'name': 't', 'type': 'number', 'unit': 's'},
            {'name': 'E', 'type': 'number', 'unit': 'V', 'reference': 'RHE'},
            {'name': 'j', 'type': 'number', 'unit': 'A / m2'}]

        """
        df = self.df.rename(columns={field_name: new_name}).copy()

        new_fields = self._modify_fields_names(
            self.resource.schema.to_dict()["fields"],
            name_mappings={field_name: new_name},
            keep_original_name_as=keep_original_name_as,
        )

        # Create new resource with renamed data
        new_resource = self._create_new_df_resource(df, schema={"fields": new_fields})

        return type(self)(resource=new_resource)

    def rename_fields(self, field_names, keep_original_name_as=None):
        r"""Returns a :class:`~unitpackage.entry.Entry` with updated field names and dataframe
        column names. Provide a dict, where the key is the previous field name and the
        value the new name, such as ``{'t':'t_rel', 'E':'E_we'}``.
        The original field names can be kept in a new key.

        EXAMPLES:

        The original dataframe::

            >>> from unitpackage.entry import Entry
            >>> entry = Entry.create_examples()[0]
            >>> entry.df
                          t         E         j
            0      0.000000 -0.103158 -0.998277
            1      0.020000 -0.102158 -0.981762
            ...

        Dataframe with modified column names::

            >>> renamed_entry = entry.rename_fields({'t': 't_rel', 'E': 'E_we'}, keep_original_name_as='originalName')
            >>> renamed_entry.df
                      t_rel      E_we         j
            0      0.000000 -0.103158 -0.998277
            1      0.020000 -0.102158 -0.981762
            ...

        Updated fields of the resource::

            >>> renamed_entry.fields
            [{'name': 't_rel', 'type': 'number', 'unit': 's', 'originalName': 't'},
            {'name': 'E_we', 'type': 'number', 'unit': 'V', 'reference': 'RHE', 'originalName': 'E'},
            {'name': 'j', 'type': 'number', 'unit': 'A / m2'}]

        TESTS:

        Provide alternatives for non-existing fields::

            >>> renamed_entry = entry.rename_fields({'t': 't_rel', 'x':'y'}, keep_original_name_as='originalName')
            >>> renamed_entry.fields
            [{'name': 't_rel', 'type': 'number', 'unit': 's', 'originalName': 't'},
            {'name': 'E', 'type': 'number', 'unit': 'V', 'reference': 'RHE'},
            {'name': 'j', 'type': 'number', 'unit': 'A / m2'}]

        """
        if not field_names:
            logger.warning(
                "No renaming pattern was provided, such as {'t': 't_rel', 'x':'y'}."
            )
            return self

        result = self
        for old_name, new_name in field_names.items():
            result = result.rename_field(
                old_name, new_name, keep_original_name_as=keep_original_name_as
            )
        return result

    @classmethod
    def from_local(cls, filename):
        r"""
        Return an entry from a :param filename containing a frictionless Data Package.
        The Data Package must contain a single resource.

        Otherwise use `collection.from_local_file` to create a collection from
        all resources within.

        EXAMPLES::

            >>> from unitpackage.entry import Entry
            >>> entry = Entry.from_local('./examples/local/no_bibliography/no_bibliography.json')
            >>> entry
            Entry('no_bibliography')

        """
        from frictionless import Package

        package = Package(filename)

        if len(package.resources) == 0:
            raise ValueError(f"No resource available in '{filename}'")

        if len(package.resources) > 1:
            raise ValueError(
                f"More than one resource available in '{filename}'. Use collection.from_local()`"
            )

        return cls(resource=package.resources[0])

    @classmethod
    def from_df(cls, df, *, basename):
        r"""
        Returns an entry constructed from a pandas dataframe.
        A name `basename` for the entry must be provided.
        The name must be lower-case and contain only alphanumeric
        characters along with `.` , `_` or `-` characters'.
        (Upper case characters are converted to lower case.)

        EXAMPLES::

            >>> import pandas as pd
            >>> from unitpackage.entry import Entry
            >>> df = pd.DataFrame({'x':[1,2,3], 'y':[2,3,4]})
            >>> entry = Entry.from_df(df=df, basename='test_df')
            >>> entry
            Entry('test_df')

        Metadata and field descriptions can be added::

            >>> import os
            >>> fields = [{'name':'x', 'unit': 'm'}, {'name':'P', 'unit': 'um'}, {'name':'E', 'unit': 'V'}]
            >>> metadata = {'user':'Max Doe'}
            >>> entry = Entry.from_df(df=df, basename='test_df').update_fields(fields=fields)
            >>> entry.metadata.from_dict(metadata)
            >>> entry.metadata
            {'user': 'Max Doe'}

        Save the entry::

            >>> entry.save(outdir='./test/generated/from_df')

        .. important::
            Basenames with upper case characters are stored with lower case characters!
            To separate words use underscores.

        The basename will always be converted to lowercase entry identifiers::

            >>> import pandas as pd
            >>> from unitpackage.entry import Entry
            >>> df = pd.DataFrame({'x':[1,2,3], 'y':[2,3,4]})
            >>> entry = Entry.from_df(df=df, basename='TEST_DF')
            >>> entry
            Entry('test_df')

        TESTS:

        Verify that all fields are properly created even when they are not specified as fields::

            >>> fields = [{'name':'x', 'unit': 'm'}, {'name':'P', 'unit': 'um'}, {'name':'E', 'unit': 'V'}]
            >>> entry = Entry.from_df(df=df, basename='test_df').update_fields(fields=fields)
            >>> entry.fields
            [{'name': 'x', 'type': 'integer', 'unit': 'm'}, {'name': 'y', 'type': 'integer'}]

        """
        from unitpackage.local import create_df_resource_from_df

        resource = create_df_resource_from_df(df)
        resource.name = basename.lower()

        return cls(resource)

    def save(self, *, outdir, basename=None):
        r"""
        Create a Data Package, i.e., a CSV file and a JSON file, in the directory ``outdir``.

        EXAMPLES:

        The output files are named ``identifier.csv`` and ``identifier.json`` using the identifier of the original resource::

            >>> import os
            >>> entry = Entry.create_examples()[0]
            >>> entry.save(outdir='./test/generated')
            >>> basename = entry.identifier
            >>> os.path.exists(f'test/generated/{basename}.json') and os.path.exists(f'test/generated/{basename}.csv')
            True

        When a ``basename`` is set, the files are named ``basename.csv`` and ``basename.json``.

        .. note::
            For a valid frictionless Data Package the basename
            MUST be lower-case and contain only alphanumeric
            characters along with ``.``, ``_`` or ``-`` characters'

        A valid basename::

            >>> import os
            >>> entry = Entry.create_examples()[0]
            >>> basename = 'save_basename'
            >>> entry.save(basename=basename, outdir='./test/generated')
            >>> os.path.exists(f'test/generated/{basename}.json') and os.path.exists(f'test/generated/{basename}.csv')
            True

        Upper case characters are saved lower case::

            >>> import os
            >>> import pandas as pd
            >>> from unitpackage.entry import Entry
            >>> df = pd.DataFrame({'x':[1,2,3], 'y':[2,3,4]})
            >>> basename = 'Upper_Case_Save'
            >>> entry = Entry.from_df(df=df, basename=basename)
            >>> entry.save(outdir='./test/generated')
            >>> os.path.exists(f'test/generated/{basename.lower()}.json') and os.path.exists(f'test/generated/{basename.lower()}.csv')
            True

            >>> new_entry = Entry.from_local(f'test/generated/{basename.lower()}.json')
            >>> new_entry.resource # doctest: +NORMALIZE_WHITESPACE
            {'name': 'upper_case_save',
            'type': 'table',
            'path': 'upper_case_save.csv',
            ...

        TESTS:

        Save the entry as Data Package with metadata containing datetime format,
        which is not natively supported by JSON.::

            >>> import os
            >>> from datetime import datetime
            >>> import pandas as pd
            >>> from unitpackage.entry import Entry
            >>> df = pd.DataFrame({'x':[1,2,3], 'y':[2,3,4]})
            >>> basename = 'save_datetime'
            >>> entry = Entry.from_df(df=df, basename=basename)
            >>> entry.metadata.from_dict({'currentTime':datetime.now()})
            >>> entry.save(outdir='./test/generated')
            >>> os.path.exists(f'test/generated/{basename}.json') and os.path.exists(f'test/generated/{basename}.csv')
            True

        """
        if not os.path.isdir(outdir):
            os.makedirs(outdir)

        basename = basename or self.identifier
        basename = basename.lower()
        csv_name = os.path.join(outdir, basename + ".csv")
        json_name = os.path.join(outdir, basename + ".json")

        self.df.to_csv(csv_name, index=False)

        # Create resource descriptor for saving
        from frictionless import Resource

        # Get current schema from the dataframe resource
        current_schema = self.resource.schema.to_dict()

        # Build resource descriptor
        resource = {
            "name": basename,
            "type": "table",
            "path": basename + ".csv",
            "format": "csv",
            "mediatype": "text/csv",
            "schema": current_schema,
        }

        # Add metadata if present
        if self.resource.custom.get("metadata"):
            resource["metadata"] = self.resource.custom["metadata"]

        from frictionless import Package

        package = Package(
            resources=[Resource.from_descriptor(resource)],
        )

        with open(json_name, mode="w", encoding="utf-8") as json:
            from unitpackage.local import write_metadata

            write_metadata(json, package.to_dict())
