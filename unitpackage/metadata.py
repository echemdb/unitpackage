r"""
Metadata management for unitpackage entries.

This module provides the MetadataDescriptor class that manages metadata
for Entry objects, supporting both dict and attribute access, and providing
methods to load metadata from various sources (YAML, JSON, dict).

EXAMPLES:

Access metadata with dict-style or attribute-style syntax::

    >>> from unitpackage.entry import Entry
    >>> entry = Entry.create_examples()[0]
    >>> entry.metadata['echemdb']['source']['citationKey']
    'alves_2011_electrochemistry_6010'

    >>> entry.metadata.echemdb.source.citationKey
    'alves_2011_electrochemistry_6010'

Load metadata from external sources::

    >>> entry.metadata.from_dict({'custom': {'key': 'value'}})
    >>> entry.metadata['custom']['key']
    'value'

"""

# ********************************************************************
#  This file is part of unitpackage.
#
#        Copyright (C) 2026 Albert Engstfeld
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

from unitpackage.descriptor import Descriptor


class MetadataDescriptor:
    r"""
    Manages metadata for an Entry, supporting both dict and attribute access,
    and providing methods to load metadata from various sources.

    EXAMPLES::

        >>> from unitpackage.entry import Entry
        >>> entry = Entry.create_examples()[0]
        >>> entry.metadata # doctest: +ELLIPSIS
        {'echemdb': {'experimental': ...

        >>> entry.metadata['echemdb']['source']['citationKey']
        'alves_2011_electrochemistry_6010'

        >>> entry.metadata.echemdb.source.citationKey
        'alves_2011_electrochemistry_6010'

    """

    def __init__(self, entry):
        object.__setattr__(self, "_entry", entry)

    def __repr__(self):
        return repr(self._metadata)

    @property
    def _metadata(self):
        return self._entry.resource.custom.setdefault("metadata", {})

    @property
    def _descriptor(self):
        return Descriptor(self._metadata)

    def __getitem__(self, key):
        r"""
        Dict-style access to metadata with descriptor support.

        EXAMPLES::

            >>> from unitpackage.entry import Entry
            >>> entry = Entry.create_examples()[0]
            >>> entry.metadata['echemdb']['source']['citationKey']
            'alves_2011_electrochemistry_6010'

        """
        return self._descriptor[key]

    def __setitem__(self, key, value):
        r"""
        Dict-style assignment to metadata.

        EXAMPLES::

            >>> from unitpackage.entry import Entry
            >>> entry = Entry.create_examples()[0]
            >>> entry.metadata['custom_key'] = {'data': 'value'}
            >>> entry.metadata['custom_key']
            {'data': 'value'}

        """
        self._metadata[key] = value

    def __getattr__(self, name):
        r"""
        Attribute-style access to metadata with full descriptor support.

        EXAMPLES::

            >>> from unitpackage.entry import Entry
            >>> entry = Entry.create_examples()[0]
            >>> entry.metadata.echemdb.source.citationKey
            'alves_2011_electrochemistry_6010'

        """
        return getattr(self._descriptor, name)

    def from_dict(self, data):
        r"""
        Load metadata from a dictionary.

        EXAMPLES::

            >>> from unitpackage.entry import Entry
            >>> entry = Entry.create_examples()[0]
            >>> entry.metadata.from_dict({'echemdb': {'source': {'citationKey': 'test'}}})
            >>> entry.metadata['echemdb']['source']['citationKey']
            'test'

        """
        self._entry.resource.custom["metadata"] = data

    def _add_metadata(self, key, data):
        r"""
        Add metadata under a specific key.

        EXAMPLES::

            >>> from unitpackage.entry import Entry
            >>> entry = Entry.create_examples()[0]
            >>> entry.metadata._add_metadata('custom_key', {'data': 'value'})
            >>> entry.metadata['custom_key']
            {'data': 'value'}

        """
        if key:
            self._entry.resource.custom["metadata"][key] = data
        else:
            self._entry.resource.custom["metadata"] = data

    def from_yaml(self, filename, key=None):
        r"""
        Load metadata from a YAML file.

        If a key is provided, the loaded data is stored under that key.
        Otherwise, it replaces the entire metadata dict.

        EXAMPLES::

            >>> import os
            >>> import tempfile
            >>> import yaml
            >>> from unitpackage.entry import Entry
            >>> entry = Entry.create_examples()[0]
            >>> with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            ...     yaml.dump({'source': {'citationKey': 'yaml_test'}}, f)
            ...     temp_path = f.name
            >>> entry.metadata.from_yaml(temp_path, key='echemdb')
            >>> entry.metadata['echemdb']['source']['citationKey']
            'yaml_test'
            >>> os.unlink(temp_path)

        """
        import yaml

        with open(filename, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)

        self._add_metadata(key, data)

    def from_json(self, filename, key=None):
        r"""
        Load metadata from a JSON file.

        If a key is provided, the loaded data is stored under that key.
        Otherwise, it replaces the entire metadata dict.

        EXAMPLES::

            >>> import os
            >>> import json
            >>> import tempfile
            >>> from unitpackage.entry import Entry
            >>> entry = Entry.create_examples()[0]
            >>> with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            ...     json.dump({'source': {'citationKey': 'json_test'}}, f)
            ...     temp_path = f.name
            >>> entry.metadata.from_json(temp_path, key='echemdb')
            >>> entry.metadata['echemdb']['source']['citationKey']
            'json_test'
            >>> os.unlink(temp_path)

        """
        import json

        with open(filename, "r", encoding="utf-8") as f:
            data = json.load(f)

        self._add_metadata(key, data)
