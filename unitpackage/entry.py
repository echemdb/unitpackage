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

    def load_metadata(self, filename, format=None, key=None):
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
        if format is None:
            if filename.endswith('.yaml') or filename.endswith('.yml'):
                format = 'yaml'
            elif filename.endswith('.json'):
                format = 'json'
            else:
                raise ValueError(
                    f"Cannot auto-detect format for '{filename}'. "
                    "Please specify format='yaml' or format='json'"
                )

        # Load metadata using the appropriate method
        if format == 'yaml':
            self.metadata.from_yaml(filename, key=key)
        elif format == 'json':
            self.metadata.from_json(filename, key=key)
        else:
            raise ValueError(
                f"Unsupported format '{format}'. Use 'yaml' or 'json'"
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
            'from_csv', 'from_df', 'from_local', 'identifier', 'load_metadata',
            'metadata', 'mutable_resource', 'plot', 'rename_fields', 'rescale', 'resource',
            'save', 'yaml']

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
        return self.resource.custom["metadata"]

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

    def field_unit(self, field_name):
        r"""
        Return the unit of the ``field_name`` of the ``MutableResource`` resource.

        EXAMPLES::

            >>> entry = Entry.create_examples()[0]
            >>> entry.field_unit('E')
            'V'

        """
        return self.mutable_resource.schema.get_field(field_name).custom["unit"]

    def rescale(self, units):
        r"""
        Returns a rescaled :class:`~unitpackage.entry.Entry` with axes in the specified ``units``.
        Provide a dict, where the key is the axis name and the value
        the new unit, such as `{'j': 'uA / cm2', 't': 'h'}`.

        EXAMPLES:

        The units without any rescaling::

            >>> entry = Entry.create_examples()[0]
            >>> entry.resource.schema.fields
            [{'name': 't', 'type': 'number', 'unit': 's'},
            {'name': 'E', 'type': 'number', 'unit': 'V', 'reference': 'RHE'},
            {'name': 'j', 'type': 'number', 'unit': 'A / m2'}]

        A rescaled entry using different units::

            >>> rescaled_entry = entry.rescale({'j':'uA / cm2', 't':'h'})
            >>> rescaled_entry.mutable_resource.schema.fields
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
        from frictionless import Resource

        resource = Resource(self.resource.to_dict())
        fields = self.mutable_resource.schema.fields
        df = self.df.copy()

        for field in fields:
            if field.name in units:
                df[field.name] *= u.Unit(field.custom["unit"]).to(
                    u.Unit(units[field.name])
                )
                resource.schema.update_field(field.name, {"unit": units[field.name]})

        # create a new dataframe resource
        df_resource = Resource(df)
        df_resource.infer()
        # update units in the schema of the df resource
        df_resource.schema = resource.schema

        # Update the "MutableResource"
        resource.custom["MutableResource"] = df_resource

        return type(self)(resource=resource)

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

            >>> new_entry.mutable_resource.schema.get_field('E') # doctest: +NORMALIZE_WHITESPACE
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

            >>> new_entry_1.mutable_resource.schema.get_field('E') # doctest: +NORMALIZE_WHITESPACE
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

        field = self.mutable_resource.schema.get_field(field_name)

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

        # create new resource
        from frictionless import Resource

        resource = Resource(self.resource.to_dict())

        df_resource = Resource(df)
        df_resource.infer()
        df_resource.schema = resource.schema

        resource.custom["MutableResource"] = df_resource

        # include or update the offset in the fields metadata
        old_offset_quantity = field.custom.get("offset", {}).get("value", 0.0) * u.Unit(
            field.custom.get("offset", {}).get("unit", field.custom.get("unit"))
        )
        new_offset = old_offset_quantity.value + offset_quantity.value

        df_resource.schema.update_field(
            field_name,
            {"offset": {"value": float(new_offset), "unit": str(offset_quantity.unit)}},
        )

        return type(self)(resource=resource)

    @property
    def mutable_resource(self):
        r"""
        Return the entry's "MutableResource".

        EXAMPLES::

            >>> entry = Entry.create_examples()[0]
            >>> entry.mutable_resource
            {'name': 'memory',
            'type': 'table',
            'data': [],
            'format': 'pandas',
            'mediatype': 'application/pandas',
            'schema': {'fields': [{'name': 't', 'type': 'number', 'unit': 's'},
                                {'name': 'E',
                                    'type': 'number',
                                    'unit': 'V',
                                    'reference': 'RHE'},
                                {'name': 'j', 'type': 'number', 'unit': 'A / m2'}]}}
        """
        self.resource.custom.setdefault("MutableResource", "")

        if not self.resource.custom["MutableResource"]:
            if self.resource.format not in ["csv", "pandas"]:
                raise ValueError(
                    "MutableResource can only be created from resources of format 'csv' or 'pandas'."
                )

            if self.resource.format == "csv":

                from unitpackage.local import create_df_resource_from_tabular_resource

                self.resource.custom["MutableResource"] = (
                    create_df_resource_from_tabular_resource(self.resource)
                )

            elif self.resource.format == "pandas":
                self.resource.custom["MutableResource"] = self.resource

            from frictionless import Schema

            self.resource.custom["MutableResource"].schema = Schema.from_descriptor(
                self.resource.schema.to_dict()
            )

        return self.resource.custom["MutableResource"]

    @property
    def df(self):
        r"""
        Return the data of this entry's "MutableResource" as a data frame.

        EXAMPLES::

            >>> entry = Entry.create_examples()[0]
            >>> entry.df
                          t         E         j
            0      0.000000 -0.103158 -0.998277
            1      0.020000 -0.102158 -0.981762
            ...

        The units and descriptions of the axes in the data frame can be recovered::

            >>> entry.mutable_resource.schema.fields # doctest: +NORMALIZE_WHITESPACE
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
        return self.mutable_resource.data

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

        """
        import pandas as pd

        df_ = pd.concat([self.df, df], axis=1)

        fields = [field.to_dict() for field in self.mutable_resource.schema.fields]

        fields.extend(new_fields)
        return self.from_df(
            df=df_, metadata=self._metadata, basename=self.identifier, fields=fields
        )

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

        fig.update_layout(
            template="simple_white",
            showlegend=True,
            autosize=True,
            width=600,
            height=400,
            margin={"l": 70, "r": 70, "b": 70, "t": 70, "pad": 7},
            xaxis_title=f"{x_label} [{self.field_unit(x_label)}]",
            yaxis_title=f"{y_label} [{self.field_unit(y_label)}]",
        )

        fig.update_xaxes(showline=True, mirror=True)
        fig.update_yaxes(showline=True, mirror=True)

        return fig

    @classmethod
    def from_csv(
        cls,
        csvname,
        encoding=None,
        header_lines=None,
        column_header_lines=None,
        decimal=None,
        delimiters=None,
        metadata=None,
        fields=None,
    ):
        r"""
        Returns an entry constructed from a CSV with a single header line.

        EXAMPLES:

        Units describing the fields can be provided::

            >>> from unitpackage.entry import Entry
            >>> fields = [{'name':'E', 'unit': 'mV'}, {'name':'I', 'unit': 'A'}]
            >>> entry = Entry.from_csv(csvname='examples/from_csv/from_csv.csv', fields=fields)
            >>> entry
            Entry('from_csv')

            >>> entry.resource # doctest: +NORMALIZE_WHITESPACE
            {'name': 'from_csv',
            ...

        Metadata can be appended::

            >>> fields = [{'name':'E', 'unit': 'mV'}, {'name':'I', 'unit': 'A'}]
            >>> metadata = {'user':'Max Doe'}
            >>> entry = Entry.from_csv(csvname='examples/from_csv/from_csv.csv', metadata=metadata, fields=fields)
            >>> entry.user
            'Max Doe'

        .. important::
            Upper case filenames are converted to lower case entry identifiers!

        A filename containing upper case characters::

            >>> fields = [{'name':'E', 'unit': 'mV'}, {'name':'I', 'unit': 'A'}]
            >>> entry = Entry.from_csv(csvname='examples/from_csv/UpperCase.csv', fields=fields)
            >>> entry
            Entry('uppercase')

        Casing in the filename is preserved in the metadata::

            >>> entry.resource # doctest: +NORMALIZE_WHITESPACE
            {'name': 'uppercase',
            'type': 'table',
            'path': 'UpperCase.csv',
            ...

        """
        from unitpackage.local import (
            create_tabular_resource_from_csv,
            create_unitpackage,
        )

        # pylint: disable=duplicate-code
        resource = create_tabular_resource_from_csv(
            csvname=csvname,
            encoding=encoding,
            header_lines=header_lines,
            column_header_lines=column_header_lines,
            decimal=decimal,
            delimiters=delimiters,
        )

        package = create_unitpackage(
            resource=resource, metadata=metadata, fields=fields
        )

        return cls(resource=package.resources[0])

    @classmethod
    def _modify_fields(cls, original, alternative, keep_original_name_as=None):
        r"""Updates in a list of fields (original) the field names with those
        provided in a dictionary. The original name of the fields is kept with
        the name `original` in the updated fields.

        EXAMPLES::

            >>> fields = [{'name': '<E>', 'unit':'mV'},{'name': 'I', 'unit':'mA'}]
            >>> alt_fields = {'<E>':'E'}
            >>> Entry._modify_fields(fields, alt_fields, keep_original_name_as='original')
            [{'name': 'E', 'unit': 'mV', 'original': '<E>'}, {'name': 'I', 'unit': 'mA'}]

        """
        for field in original:
            for key in alternative.keys():
                if field["name"] == key:
                    if keep_original_name_as:
                        field.setdefault(keep_original_name_as, key)
                    field["name"] = alternative[key]

        return original

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

        Updated fields of the "MutableResource"::

            >>> renamed_entry.mutable_resource.schema.fields
            [{'name': 't_rel', 'type': 'number', 'unit': 's', 'originalName': 't'},
            {'name': 'E_we', 'type': 'number', 'unit': 'V', 'reference': 'RHE', 'originalName': 'E'},
            {'name': 'j', 'type': 'number', 'unit': 'A / m2'}]

        TESTS:

        Provide alternatives for non-existing fields::

            >>> renamed_entry = entry.rename_fields({'t': 't_rel', 'x':'y'}, keep_original_name_as='originalName')
            >>> renamed_entry.mutable_resource.schema.fields
            [{'name': 't_rel', 'type': 'number', 'unit': 's', 'originalName': 't'},
            {'name': 'E', 'type': 'number', 'unit': 'V', 'reference': 'RHE'},
            {'name': 'j', 'type': 'number', 'unit': 'A / m2'}]

        """
        if not field_names:
            logger.warning(
                "No renaming pattern was provided, such as {'t': 't_rel', 'x':'y'}."
            )
            field_names = {}

        from frictionless import Resource, Schema

        resource = Resource(self.resource.to_dict())

        df = self.df.rename(columns=field_names).copy()

        new_fields = self._modify_fields(
            self.mutable_resource.schema.to_dict()["fields"],
            alternative=field_names,
            keep_original_name_as=keep_original_name_as,
        )

        df_resource = Resource(df)
        df_resource.infer()
        df_resource.schema = Schema.from_descriptor(
            {"fields": new_fields}, allow_invalid=True
        )

        resource.custom["MutableResource"] = df_resource

        return type(self)(resource=resource)

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
        from unitpackage.local import Package

        package = Package(filename)

        if len(package.resources) == 0:
            raise ValueError(f"No resource available in '{filename}'")

        if len(package.resources) > 1:
            raise ValueError(
                f"No than one resource available in '{filename}'. Use collection.from_local()`"
            )

        return cls(resource=package.resources[0])

    @classmethod
    def from_df(cls, df, metadata=None, fields=None, *, basename):
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
            >>> entry = Entry.from_df(df=df, basename='test_df', metadata=metadata, fields=fields)
            >>> entry.user
            'Max Doe'

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
            >>> metadata = {'user':'Max Doe'}
            >>> entry = Entry.from_df(df=df, basename='test_df', metadata=metadata, fields=fields)
            >>> entry.resource.schema.fields
            [{'name': 'x', 'type': 'integer', 'unit': 'm'}, {'name': 'y', 'type': 'integer'}]

        """
        from unitpackage.local import create_df_resource_from_df, create_unitpackage

        resource = create_df_resource_from_df(df)
        resource.name = basename.lower()

        package = create_unitpackage(
            resource=resource, metadata=metadata, fields=fields
        )
        return cls(resource=package.resources[0])

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
            >>> entry = Entry.from_df(df=df, basename=basename, metadata={'currentTime':datetime.now()})
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

        # update the identifier and filepath of the resource
        if basename:
            self.resource.path = basename + ".csv"
            self.resource.name = basename

        # convert a pandas resource into a csv resource
        if self.resource.format == "pandas":
            self.resource.format = "csv"
            self.resource.mediatype = "text/csv"
            if hasattr(self.resource, "data"):
                del self.resource.data

        resource = self.resource.to_dict()

        # update the fields from the main resource with those from the "MutableResource"resource
        resource["schema"]["fields"] = self.mutable_resource.schema.fields
        resource["schema"] = resource["MutableResource"].schema.to_dict()
        del resource["MutableResource"]

        from frictionless import Package, Resource

        package = Package(
            resources=[Resource.from_descriptor(resource)],
        )

        with open(json_name, mode="w", encoding="utf-8") as json:
            from unitpackage.local import write_metadata

            write_metadata(json, package.to_dict())
