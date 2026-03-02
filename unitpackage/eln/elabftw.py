r"""
Client for integrating unitpackage with eLabFTW electronic lab notebooks.

Provides the :class:`ElabFTWClient` class for fetching experiments and items
from an eLabFTW instance as unitpackage entries, and for uploading entries
back to eLabFTW.

EXAMPLES:

Create a client from environment variables::

    # export ELABFTW_HOST=https://eln.example.org
    # export ELABFTW_API_KEY=your-api-key
    # client = ElabFTWClient.from_env()

Or provide credentials directly::

    # client = ElabFTWClient(
    #     host="https://eln.example.org",
    #     api_key="your-api-key",
    # )

Fetch a single experiment as an Entry::

    # entry = client.fetch_entry("experiments", 42)
    # entry.df  # pandas DataFrame with the CSV data
    # entry.metadata  # metadata from eLabFTW

Fetch multiple experiments filtered by tags::

    # entries = client.fetch_entries("experiments", tags=["electrochemistry"])

Upload an Entry to eLabFTW::

    # entity_id = client.upload_entry(entry, title="My Experiment")

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
import io
import json
import logging
import os
import tempfile
from pathlib import Path

import elabapi_python
import pandas as pd

from unitpackage.eln import (
    BaseELNClient,
    apply_datapackage_descriptor,
    build_datapackage_descriptor,
)
from unitpackage.entry import Entry

logger = logging.getLogger("unitpackage")

# Filename used for the datapackage descriptor attachment.


class ElabFTWClient(BaseELNClient):
    r"""
    Client for interacting with an eLabFTW electronic lab notebook instance.

    Provides methods to fetch experiments and items as unitpackage entries,
    and to upload entries back to eLabFTW.

    EXAMPLES:

    Create a client with explicit credentials::

        # client = ElabFTWClient(
        #     host="https://eln.example.org",
        #     api_key="your-api-key",
        # )

    Create a client from environment variables::

        # client = ElabFTWClient.from_env()

    """

    def __init__(self, host, api_key, entity_type="items", verify_ssl=True):
        r"""
        Initialize the eLabFTW client.

        The ``host`` should be the base URL of the eLabFTW instance
        (e.g., ``https://eln.example.org``). The ``/api/v2`` path is
        appended automatically.

        The ``api_key`` is used for authentication via the Authorization
        header.

        The ``entity_type`` must be ``"items"`` (eLabFTW resources).

        EXAMPLES::

            # client = ElabFTWClient(
            #     host="https://eln.example.org",
            #     api_key="your-api-key",
            # )

        """
        if entity_type != "items":
            raise ValueError(f"Invalid entity_type '{entity_type}'. Must be 'items'.")
        self._entity_type = entity_type

        configuration = elabapi_python.Configuration()
        configuration.host = f"{host.rstrip('/')}/api/v2"
        configuration.verify_ssl = verify_ssl

        if not verify_ssl:
            import urllib3

            urllib3.disable_warnings(category=urllib3.exceptions.InsecureRequestWarning)

        api_client = elabapi_python.ApiClient(configuration)
        api_client.set_default_header(header_name="Authorization", header_value=api_key)

        self._api_client = api_client
        self.items_client = elabapi_python.ItemsApi(api_client)
        self.uploads_client = elabapi_python.UploadsApi(api_client)

    @classmethod
    def from_env(cls):
        r"""
        Create an ElabFTWClient from environment variables.

        Reads ``ELABFTW_HOST`` and ``ELABFTW_API_KEY`` from the environment.

        EXAMPLES::

            # import os
            # os.environ["ELABFTW_HOST"] = "https://eln.example.org"
            # os.environ["ELABFTW_API_KEY"] = "your-api-key"
            # client = ElabFTWClient.from_env()

        """
        host = os.environ.get("ELABFTW_HOST")
        api_key = os.environ.get("ELABFTW_API_KEY")

        if not host:
            raise ValueError(
                "ELABFTW_HOST environment variable is not set. "
                "Set it to the base URL of your eLabFTW instance "
                "(e.g., https://eln.example.org)."
            )
        if not api_key:
            raise ValueError(
                "ELABFTW_API_KEY environment variable is not set. "
                "Generate an API key in your eLabFTW user settings."
            )

        entity_type = os.environ.get("ELABFTW_ENTITY_TYPE", "items")
        return cls(host=host, api_key=api_key, entity_type=entity_type)

    @classmethod
    def from_config(cls, profile=None):
        r"""
        Create an ElabFTWClient from a configuration file profile.

        Reads the ``[elabftw.<profile>]`` section from the unitpackage
        config file (``~/.config/unitpackage/config.toml``).
        If ``profile`` is ``None``, the first eLabFTW profile is used.

        EXAMPLES::

            # client = ElabFTWClient.from_config("production")
            # client = ElabFTWClient.from_config()  # uses first profile

        """
        from unitpackage.config import get_profile

        settings = get_profile("elabftw", profile=profile)

        if not settings:
            if profile:
                raise ValueError(
                    f"No eLabFTW profile '{profile}' found in configuration file. "
                    f"Add an [elabftw.{profile}] section to your config.toml."
                )
            raise ValueError(
                "No eLabFTW profiles found in configuration file. "
                "Add an [elabftw.<name>] section to your config.toml."
            )

        host = settings.get("host")
        api_key = settings.get("api_key")

        if not host:
            raise ValueError("Missing 'host' in eLabFTW config profile.")
        if not api_key:
            raise ValueError("Missing 'api_key' in eLabFTW config profile.")

        verify_ssl = settings.get("verify_ssl", True)
        entity_type = settings.get("entity_type", "items")
        return cls(
            host=host, api_key=api_key, entity_type=entity_type, verify_ssl=verify_ssl
        )

    def info(self):
        r"""
        Return server information as a dictionary.

        The returned dictionary contains keys such as ``version``,
        ``teams_count``, and ``all_users_count``.

        EXAMPLES::

            # client = ElabFTWClient.from_env()
            # info = client.info()
            # info["version"]
            # '5.1.0'

        """
        info_client = elabapi_python.InfoApi(self._api_client)
        response = info_client.get_info()
        return response.to_dict()

    def _get_api(self):
        r"""
        Return the appropriate API client for the given entity type.

        """
        return self.items_client

    @staticmethod
    def _parse_metadata(raw):
        r"""Parse a raw metadata value into a dict.

        The eLabFTW Python client deserialises the metadata JSON string
        into a ``Metadata`` model object that silently drops keys not in
        its schema (like ``unitpackage``).  This helper accepts a raw
        JSON string *or* an already-parsed dict and returns a plain dict.
        """
        if not raw:
            return None
        if isinstance(raw, str):
            try:
                return json.loads(raw)
            except (json.JSONDecodeError, TypeError):
                return None
        if isinstance(raw, dict):
            return raw
        return None

    @classmethod
    def _get_unitpackage_descriptor(cls, entity):
        r"""Return the ``unitpackage`` descriptor dict, or ``None``."""
        parsed = cls._parse_metadata(getattr(entity, "metadata", None))
        if parsed is None:
            return None
        return parsed.get("unitpackage")

    @classmethod
    def _has_unitpackage_metadata(cls, entity):
        r"""Return True if the entity's metadata contains a ``unitpackage`` key."""
        return cls._get_unitpackage_descriptor(entity) is not None

    def _get_item_raw(self, entity_id):
        r"""Fetch an item, bypassing model deserialisation of metadata.

        The eLabFTW Python client's ``get_item()`` returns a model object
        whose ``Metadata`` attribute silently drops keys not in its schema
        (like ``unitpackage``).  This method uses ``_preload_content=False``
        to get the raw JSON and wraps it in a ``SimpleNamespace`` so that
        the ``metadata`` field is preserved as a raw JSON string.
        """
        from types import SimpleNamespace

        api = self._get_api()
        response = api.get_item(entity_id, _preload_content=False)
        data = json.loads(response.data)
        return SimpleNamespace(**data)

    def fetch_entry(self, entity_id):
        r"""
        Fetch an item from eLabFTW and return it as a unitpackage Entry.

        Only items whose metadata contains the ``unitpackage`` key are
        considered valid.  Raises ``ValueError`` if the entity was not
        uploaded by unitpackage or has no CSV upload.

        EXAMPLES::

            # client = ElabFTWClient.from_env()
            # entry = client.fetch_entry(42)
            # entry.df
            # entry.metadata

        """
        entity_type = self._entity_type

        # Use raw fetch to preserve the metadata JSON string (the
        # elabapi_python Metadata model drops unknown keys).
        entity = self._get_item_raw(entity_id)

        # Parse the unitpackage descriptor from the entity metadata.
        descriptor = self._get_unitpackage_descriptor(entity)
        if descriptor is None:
            raise ValueError(
                f"Entity {entity_id} was not uploaded by unitpackage "
                f"(no 'unitpackage' key in metadata)."
            )

        logger.info("Fetched %s %d: %s", entity_type, entity_id, entity.title)

        # Determine the expected filename from the descriptor.
        resources = descriptor.get("resources", [])
        if not resources:
            raise ValueError(
                f"Entity {entity_id} has an empty unitpackage descriptor "
                "(no resources)."
            )
        res = resources[0]
        resource_path = res.get("path", "")
        basename = Path(resource_path).stem

        # Find the upload matching the descriptor's resource path.
        uploads = self.uploads_client.read_uploads(entity_type, entity_id)
        data_upload = None
        if resource_path:
            for upload in uploads:
                if upload.real_name == resource_path:
                    data_upload = upload
                    break

        if data_upload is None:
            raise ValueError(
                f"No upload named '{resource_path}' found on {entity_type} "
                f"entity {entity_id}. Available uploads: "
                f"{[u.real_name for u in uploads]}"
            )

        logger.info(
            "Downloading upload '%s' (id=%d)",
            data_upload.real_name,
            data_upload.id,
        )

        # Download the data file.
        response = self.uploads_client.read_upload(
            entity_type,
            entity_id,
            data_upload.id,
            format="binary",
            _preload_content=False,
        )

        df = pd.read_csv(io.BytesIO(response.data))

        # Create the entry and restore schema/metadata from the descriptor.
        entry = Entry.from_df(df=df, basename=basename)
        entry = apply_datapackage_descriptor(entry, json.dumps(descriptor))

        return entry

    def fetch_entries(self, tags=None):
        r"""
        Fetch multiple items from eLabFTW as a list of unitpackage
        Entry objects.

        Optionally filter by ``tags``, which should be a list of tag strings.
        Only entities that have CSV uploads are included in the result;
        entities without CSV uploads are skipped with a warning.

        EXAMPLES::

            # client = ElabFTWClient.from_env()
            # entries = client.fetch_entries(tags=["electrochemistry"])
            # len(entries)
            # 5

        """
        entity_type = self._entity_type
        api = self._get_api()

        # Build keyword arguments for the API call
        kwargs = {"limit": 9999}

        if tags:
            # The eLabFTW API v2 supports a native ``tags`` parameter
            # (list of strings, sent as ``tags[]`` query params, AND logic).
            kwargs["tags"] = list(tags)

        # Fetch with _preload_content=False to preserve raw metadata JSON
        # (the elabapi_python Metadata model drops unknown keys).
        from types import SimpleNamespace

        response = api.read_items(**kwargs, _preload_content=False)
        entities = [SimpleNamespace(**item) for item in json.loads(response.data)]

        logger.info(
            "Found %d %s%s",
            len(entities),
            entity_type,
            f" matching tags {tags}" if tags else "",
        )

        # Filter to only unitpackage-managed entities before fetching data.
        up_entities = [e for e in entities if self._has_unitpackage_metadata(e)]
        logger.info(
            "%d of %d %s have unitpackage metadata",
            len(up_entities),
            len(entities),
            entity_type,
        )

        entries = []
        for entity in up_entities:
            try:
                entry = self.fetch_entry(entity.id)
                entries.append(entry)
            except ValueError as e:
                logger.warning(
                    "Skipping %s %d (%s): %s",
                    entity_type,
                    entity.id,
                    entity.title,
                    e,
                )

        logger.info(
            "Successfully fetched %d of %d unitpackage %s",
            len(entries),
            len(up_entities),
            entity_type,
        )

        return entries

    def upload_entry(
        self, entry, title=None, tags=None
    ):  # pylint: disable=too-many-locals
        r"""
        Upload a unitpackage Entry to eLabFTW as a new resource (item).

        Creates a new item, sets the title and tags, uploads the CSV data
        as a file attachment, and stores the datapackage descriptor in the
        entity's metadata field.

        Returns the ID of the newly created item.

        EXAMPLES::

            # from unitpackage.entry import Entry
            # import pandas as pd
            # df = pd.DataFrame({"t": [0, 1, 2], "E": [0.1, 0.2, 0.3]})
            # entry = Entry.from_df(df=df, basename="my_entry")
            # client = ElabFTWClient.from_env()
            # entity_id = client.upload_entry(entry, title="My Entry")

        """
        entity_type = self._entity_type
        api = self._get_api()

        # Build the creation body
        body = {}

        if title:
            body["title"] = title
        else:
            body["title"] = entry.identifier

        if tags:
            body["tags"] = list(tags)

        # Build the descriptor before creating anything so we fail fast
        # on malformed entries.
        descriptor = build_datapackage_descriptor(entry)
        resource_path = descriptor["resources"][0]["path"]

        # Create the item
        _, _, headers = api.post_item_with_http_info(body=body)

        location = headers.get("Location")
        entity_id = int(location.split("/").pop())

        logger.info(
            "Created %s %d: %s",
            entity_type,
            entity_id,
            body.get("title", ""),
        )

        try:
            # Upload the data file with the canonical name matching the
            # "path" key in the datapackage descriptor.
            with tempfile.TemporaryDirectory() as tmpdir:
                csv_path = os.path.join(tmpdir, resource_path)
                entry.df.to_csv(csv_path, index=False)
                self.uploads_client.post_upload(
                    entity_type,
                    entity_id,
                    file=csv_path,
                    comment="Data uploaded from unitpackage",
                )
                logger.info("Uploaded data for %s %d", entity_type, entity_id)

            # Store the datapackage descriptor in the entity's metadata field
            # under a top-level "unitpackage" key so that a round-trip fetch
            # can faithfully restore schema and metadata.
            metadata = {
                "unitpackage": descriptor,
            }
            metadata_json = json.dumps(metadata, default=str)
            api.patch_item(entity_id, body={"metadata": metadata_json})
            logger.info(
                "Stored datapackage descriptor in metadata for %s %d",
                entity_type,
                entity_id,
            )
        except Exception:  # pylint: disable=broad-except
            logger.warning(
                "Upload failed, deleting partially created %s %d",
                entity_type,
                entity_id,
            )
            try:
                api.delete_item(entity_id)
            except Exception:  # pylint: disable=broad-except
                logger.error(
                    "Failed to clean up %s %d after upload error",
                    entity_type,
                    entity_id,
                )
            raise

        return entity_id
