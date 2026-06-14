r"""
Shared, backend-agnostic building blocks for ELN integrations.

Defines the :class:`BaseELNClient` abstract base class implemented by the
concrete backends (:mod:`unitpackage.eln.elabftw` and
:mod:`unitpackage.eln.kadi`) together with the datapackage-descriptor helpers
they share.

These names are re-exported from :mod:`unitpackage.eln`, so import them from
there (``from unitpackage.eln import BaseELNClient``) rather than reaching into
this private module directly.

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

    def _collect_entries(self, items, label):
        r"""
        Fetch each ``(entity_id, title)`` pair, skipping ones that raise
        ``ValueError``.

        Shared by the concrete backends' :meth:`fetch_entries` implementations:
        each backend resolves its own listing into a list of
        ``(entity_id, title)`` tuples and delegates the per-entity download,
        error handling, and summary logging here.

        ``items`` must be a list (so its length is the meaningful denominator
        of entities actually considered). ``label`` is a human-readable noun
        used in log messages (e.g. ``"record"`` or ``"items"``).
        """
        entries = []
        for entity_id, title in items:
            try:
                entries.append(self.fetch_entry(entity_id))
            except ValueError as exc:
                logger.warning("Skipping %s %s (%s): %s", label, entity_id, title, exc)

        logger.info(
            "Successfully fetched %d of %d %s entries",
            len(entries),
            len(items),
            label,
        )
        return entries


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


def first_resource(descriptor):
    r"""
    Return the first resource dict from a datapackage descriptor.

    Validates that the descriptor carries at least one well-formed resource
    with a non-empty ``path``. Shared by the ELN backends' :meth:`fetch_entry`
    implementations, which use the resource's ``path`` to locate the uploaded
    CSV file.

    Raises ``ValueError`` if the descriptor has no resources or the first
    resource has no path.

    EXAMPLES::

        >>> first_resource({"resources": [{"path": "a.csv"}]})
        {'path': 'a.csv'}
        >>> first_resource({"resources": []})
        Traceback (most recent call last):
        ...
        ValueError: unitpackage descriptor has no resources.

    """
    resources = descriptor.get("resources", []) if isinstance(descriptor, dict) else []
    if not (
        isinstance(resources, list) and resources and isinstance(resources[0], dict)
    ):
        raise ValueError("unitpackage descriptor has no resources.")

    resource = resources[0]
    if not resource.get("path"):
        raise ValueError("unitpackage descriptor resource has no path.")

    return resource


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
