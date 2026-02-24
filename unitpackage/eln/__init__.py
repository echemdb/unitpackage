r"""
Shared utilities for Electronic Lab Notebook (ELN) backend integrations.

Functions here are backend-agnostic and used by :mod:`unitpackage.eln.elabftw`.

"""

# ********************************************************************
#  This file is part of unitpackage.
#
#        Copyright (C) 2026 Johannes Hermann
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
import abc
import json
import logging

logger = logging.getLogger("unitpackage")

#: Canonical filename used by all ELN backends to store the frictionless
#: datapackage descriptor as a file attachment alongside the CSV data.
DATAPACKAGE_FILENAME = "datapackage.json"


class BaseELNClient(abc.ABC):
    r"""
    Abstract base class for ELN backend clients.

    ELN backends (e.g. eLabFTW) implement this interface, which guarantees
    a uniform API for fetching and uploading unitpackage entries.

    Concrete subclasses must implement :meth:`from_env`, :meth:`from_config`,
    :meth:`info`, :meth:`fetch_entry`, :meth:`fetch_entries`, and
    :meth:`upload_entry`.
    """

    @classmethod
    @abc.abstractmethod
    def from_env(cls):
        """Create a client from environment variables."""

    @classmethod
    @abc.abstractmethod
    def from_config(cls, profile=None):
        """Create a client from a configuration file profile."""

    @abc.abstractmethod
    def info(self) -> dict:
        """Return server information as a dict."""

    @abc.abstractmethod
    def fetch_entry(self, entity_id: int):
        """Fetch a single ELN entity and return it as an :class:`~unitpackage.entry.Entry`."""

    @abc.abstractmethod
    def fetch_entries(self, tags=None):
        """Fetch multiple ELN entities and return them as a list of entries."""

    @abc.abstractmethod
    def upload_entry(self, entry, title=None, tags=None) -> int:
        """Upload a unitpackage entry to the ELN and return the created entity ID."""



def build_datapackage_descriptor(entry):
    r"""
    Build the frictionless datapackage descriptor dict for an Entry.

    Returns the same structure that ``entry.save()`` writes to disk as the
    JSON file — i.e. the full datapackage (schema, field units, metadata)
    but without the CSV data itself.

    This is used by ELN backends to store the complete entry description in
    the ELN's metadata system so that a round-trip fetch faithfully restores
    schema and metadata.

    EXAMPLES::

        >>> import pandas as pd
        >>> from unitpackage.entry import Entry
        >>> df = pd.DataFrame({"t": [0.0, 1.0], "E": [-0.1, -0.2]})
        >>> entry = Entry.from_df(df=df, basename="test")
        >>> descriptor = build_datapackage_descriptor(entry)
        >>> list(descriptor.keys())
        ['resources']
        >>> descriptor["resources"][0]["name"]
        'test'

    """
    from frictionless import Package, Resource

    current_schema = entry.resource.schema.to_dict()
    resource_descriptor = {
        "name": entry.identifier,
        "type": "table",
        "path": f"{entry.identifier}.csv",
        "format": "csv",
        "mediatype": "text/csv",
        "schema": current_schema,
    }
    if entry.resource.custom.get("metadata"):
        resource_descriptor["metadata"] = entry.resource.custom["metadata"]

    package = Package(resources=[Resource.from_descriptor(resource_descriptor)])
    return package.to_dict()


def apply_datapackage_descriptor(entry, datapackage_json):
    r"""
    Reconstruct metadata and field units from a stored datapackage JSON string
    and apply them to an Entry.

    Returns the updated entry, or the original entry unchanged if the JSON
    cannot be parsed or contains no resources.

    EXAMPLES::

        >>> import json, pandas as pd
        >>> from unitpackage.entry import Entry
        >>> df = pd.DataFrame({"t": [0.0, 1.0], "E": [-0.1, -0.2]})
        >>> entry = Entry.from_df(df=df, basename="test")
        >>> descriptor = build_datapackage_descriptor(entry)
        >>> entry2 = apply_datapackage_descriptor(entry, json.dumps(descriptor))
        >>> entry2 is not None
        True

    """
    try:
        descriptor = json.loads(datapackage_json)
        # Some ELN backends double-encode JSON attachments; if parsing
        # yields a string, decode one more level.
        if isinstance(descriptor, str):
            descriptor = json.loads(descriptor)
    except (json.JSONDecodeError, TypeError) as exc:
        logger.warning("Failed to parse stored datapackage descriptor: %s", exc)
        return entry

    resources = descriptor.get("resources", [])
    if not resources:
        return entry

    res = resources[0]

    metadata = res.get("metadata", {})
    if metadata:
        entry.metadata.from_dict(metadata)

    schema_fields = res.get("schema", {}).get("fields", [])
    if schema_fields:
        entry = entry.update_fields(schema_fields)

    return entry
