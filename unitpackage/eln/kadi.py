r"""
Client for integrating unitpackage with Kadi4Mat electronic lab notebooks.

Provides the :class:`KadiClient` class for fetching records from a Kadi4Mat
instance as unitpackage entries, and for uploading entries back to Kadi4Mat.

EXAMPLES:

Create a client from environment variables::

    # export KADI_HOST=https://kadi4mat.example.edu
    # export KADI_PAT=your-personal-access-token
    # client = KadiClient.from_env()

Or provide credentials directly::

    # client = KadiClient(
    #     host="https://kadi4mat.example.edu",
    #     pat="your-personal-access-token",
    # )

Fetch a single record as an Entry::

    # entry = client.fetch_entry(42)
    # entry.df  # pandas DataFrame with the CSV data

Fetch multiple records filtered by tags::

    # entries = client.fetch_entries(tags=["electrochemistry"])

Upload an Entry to Kadi4Mat::

    # entity_id = client.upload_entry(entry, title="My Record")

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
import json
import logging
import os
import re
import tempfile
from pathlib import Path

import pandas as pd
from kadi_apy import KadiManager

from unitpackage.eln import (
    BaseELNClient,
    apply_datapackage_descriptor,
    build_datapackage_descriptor,
)
from unitpackage.entry import Entry

logger = logging.getLogger("unitpackage")


def _dict_to_kadi_extras(data, key=None):
    """Convert a Python value to Kadi4Mat extras format recursively.

    Dict and list values become nested ``type: "dict"`` / ``type: "list"``
    entries so they are visible as structured metadata in the Kadi UI.
    """
    if isinstance(data, bool):
        result = {"type": "bool", "value": data}
    elif isinstance(data, int):
        result = {"type": "int", "value": data}
    elif isinstance(data, float):
        result = {"type": "float", "value": data}
    elif isinstance(data, dict):
        children = [_dict_to_kadi_extras(v, key=k) for k, v in data.items()]
        result = {"type": "dict", "value": children}
    elif isinstance(data, list):
        children = [_dict_to_kadi_extras(item) for item in data]
        result = {"type": "list", "value": children}
    else:
        result = {"type": "str", "value": str(data)}
    if key is not None:
        result["key"] = key
    return result


def _kadi_extras_to_python(extra):
    """Convert a Kadi4Mat extras entry back to a plain Python value."""
    extra_type = extra.get("type")
    if extra_type == "dict":
        return {
            child["key"]: _kadi_extras_to_python(child)
            for child in extra.get("value", [])
        }
    if extra_type == "list":
        return [_kadi_extras_to_python(item) for item in extra.get("value", [])]
    if extra_type == "int":
        return int(extra.get("value", 0))
    if extra_type == "float":
        return float(extra.get("value", 0.0))
    if extra_type == "bool":
        return bool(extra.get("value", False))
    return extra.get("value")


class KadiClient(BaseELNClient):
    r"""
    Client for interacting with a Kadi4Mat electronic lab notebook instance.

    Provides methods to fetch records as unitpackage entries and to upload
    entries back to Kadi4Mat.

    EXAMPLES:

    Create a client with explicit credentials::

        # client = KadiClient(
        #     host="https://kadi4mat.example.edu",
        #     pat="your-personal-access-token",
        # )

    Create a client from environment variables::

        # client = KadiClient.from_env()

    """

    def __init__(self, host, pat, verify_ssl=True):
        r"""
        Initialize the Kadi4Mat client.

        The ``host`` should be the base URL of the Kadi4Mat instance
        (e.g., ``https://kadi4mat.example.edu``).

        The ``pat`` is a Personal Access Token created via the Kadi4Mat
        web interface under Settings > Access tokens.

        Set ``verify_ssl=False`` to disable TLS certificate verification
        (e.g., for self-signed certificates on private instances).
        ``KadiManager`` accepts a ``verify`` parameter; ``False`` also
        suppresses urllib3 warnings automatically.

        EXAMPLES::

            # client = KadiClient(
            #     host="https://kadi4mat.example.edu",
            #     pat="your-personal-access-token",
            #     verify_ssl=True,
            # )

        """
        self._host = host.rstrip("/")
        self._manager = KadiManager(host=host, pat=pat, verify=verify_ssl)

    @classmethod
    def from_env(cls):
        r"""
        Create a KadiClient from environment variables.

        Reads ``KADI_HOST`` and ``KADI_PAT`` from the environment.

        EXAMPLES::

            # import os
            # os.environ["KADI_HOST"] = "https://kadi4mat.example.edu"
            # os.environ["KADI_PAT"] = "your-personal-access-token"
            # client = KadiClient.from_env()

        """
        host = os.environ.get("KADI_HOST")
        pat = os.environ.get("KADI_PAT")

        if not host:
            raise ValueError(
                "KADI_HOST environment variable is not set. "
                "Set it to the base URL of your Kadi4Mat instance "
                "(e.g., https://kadi4mat.example.edu)."
            )
        if not pat:
            raise ValueError(
                "KADI_PAT environment variable is not set. "
                "Create a Personal Access Token in your Kadi4Mat settings."
            )

        return cls(host=host, pat=pat)

    @classmethod
    def from_config(cls, profile=None):
        r"""
        Create a KadiClient from a configuration file profile.

        Reads the ``[kadi.<profile>]`` section from the unitpackage
        config file (``~/.config/unitpackage/config.toml``).
        If ``profile`` is ``None``, the first Kadi profile is used.

        EXAMPLES::

            # client = KadiClient.from_config("production")
            # client = KadiClient.from_config()  # uses first profile

        """
        from unitpackage.config import get_profile

        settings = get_profile("kadi", profile=profile)

        if not settings:
            if profile:
                raise ValueError(
                    f"No Kadi profile '{profile}' found in configuration file. "
                    f"Add a [kadi.{profile}] section to your config.toml."
                )
            raise ValueError(
                "No Kadi profiles found in configuration file. "
                "Add a [kadi.<name>] section to your config.toml."
            )

        host = settings.get("host")
        pat = settings.get("pat")

        if not host:
            raise ValueError("Missing 'host' in Kadi config profile.")
        if not pat:
            raise ValueError("Missing 'pat' in Kadi config profile.")

        verify_ssl = settings.get("verify_ssl", True)
        return cls(host=host, pat=pat, verify_ssl=verify_ssl)

    def info(self):
        r"""
        Return information about the connected Kadi4Mat instance.

        Makes a request to the server and returns a dictionary with
        basic information.

        EXAMPLES::

            # client = KadiClient.from_env()
            # info = client.info()

        """
        response = self._manager.make_request(f"{self._host}/api/info", "get")
        if hasattr(response, "json"):
            return response.json()
        return {"status": "connected"}

    def fetch_entry(self, entity_id):  # pylint: disable=too-many-locals
        r"""
        Fetch a record from Kadi4Mat and return it as a unitpackage Entry.

        Only records created by unitpackage (those carrying a ``unitpackage``
        metadatum) are supported.  Raises ``ValueError`` if the record has no
        such metadatum or if the CSV file named in the descriptor is missing.

        EXAMPLES::

            # client = KadiClient.from_env()
            # entry = client.fetch_entry(42)
            # entry.df

        """
        record = self._manager.record(id=entity_id)

        record_meta = record.meta if isinstance(record.meta, dict) else {}
        title = (
            record_meta.get("title")
            or record_meta.get("identifier")
            or f"record_{entity_id}"
        )
        logger.info("Fetched record %d: %s", entity_id, title)

        # Only records created by unitpackage are supported.
        extras = record.meta.get("extras", []) if isinstance(record.meta, dict) else []
        unitpackage_extra = next(
            (item for item in extras if item.get("key") == "unitpackage"),
            None,
        )
        if unitpackage_extra is None:
            raise ValueError(
                f"Record {entity_id} has no 'unitpackage' metadatum. "
                "Only records created by unitpackage are supported."
            )

        if unitpackage_extra.get("type") == "dict":
            decoded = _kadi_extras_to_python(unitpackage_extra)
            descriptor_dict = decoded if isinstance(decoded, dict) else None
        else:
            descriptor_dict = json.loads(unitpackage_extra.get("value", "{}"))

        if not isinstance(descriptor_dict, dict):
            raise ValueError(
                f"Record {entity_id}: failed to decode 'unitpackage' metadatum."
            )

        resources = descriptor_dict.get("resources", [])
        if not (
            isinstance(resources, list) and resources and isinstance(resources[0], dict)
        ):
            raise ValueError(
                f"Record {entity_id}: 'unitpackage' descriptor has no resources."
            )

        target_csv_name = Path(resources[0].get("path", "")).name
        if not target_csv_name:
            raise ValueError(
                f"Record {entity_id}: 'unitpackage' descriptor resource has no path."
            )

        # Find the CSV file named in the descriptor.
        filelist_response = record.get_filelist()
        files = []
        if hasattr(filelist_response, "json"):
            data = filelist_response.json()
            files = data.get("items", data) if isinstance(data, dict) else data
        elif isinstance(filelist_response, list):
            files = filelist_response

        csv_file_id = None
        csv_file_name = None
        for f in files:
            name = f.get("name", "") if isinstance(f, dict) else getattr(f, "name", "")
            fid = f.get("id", "") if isinstance(f, dict) else getattr(f, "id", "")
            if name == target_csv_name:
                csv_file_id, csv_file_name = fid, name
                break

        if csv_file_id is None:
            raise ValueError(
                f"CSV file '{target_csv_name}' referenced in the unitpackage descriptor "
                f"was not found on record {entity_id}."
            )

        logger.info("Downloading CSV file '%s' (id=%s)", csv_file_name, csv_file_id)

        with tempfile.TemporaryDirectory() as tmpdir:
            csv_path = os.path.join(tmpdir, csv_file_name)
            record.download_file(file_id=csv_file_id, file_path=csv_path)
            df = pd.read_csv(csv_path)

        basename = Path(resources[0].get("path", "")).stem or f"record_{entity_id}"
        entry = Entry.from_df(df=df, basename=basename)
        return apply_datapackage_descriptor(entry, json.dumps(descriptor_dict))

    def fetch_entries(self, tags=None):
        r"""
        Fetch multiple records from Kadi4Mat as a list of unitpackage
        Entry objects.

        Optionally filter by ``tags``, which should be a list of tag strings.
        Records without CSV files are skipped with a warning.

        EXAMPLES::

            # client = KadiClient.from_env()
            # entries = client.fetch_entries(tags=["electrochemistry"])
            # len(entries)

        """
        kwargs = {}
        if tags:
            kwargs["tags"] = tags

        response = self._manager.search.search_resources("record", **kwargs)

        records = []
        if hasattr(response, "json"):
            data = response.json()
            records = data.get("items", data) if isinstance(data, dict) else data
        elif isinstance(response, list):
            records = response

        logger.info(
            "Found %d records%s",
            len(records),
            f" matching tags {tags}" if tags else "",
        )

        entries = []
        for rec in records:
            rec_id = (
                rec.get("id") if isinstance(rec, dict) else getattr(rec, "id", None)
            )
            rec_title = (
                rec.get("title", "")
                if isinstance(rec, dict)
                else getattr(rec, "title", "")
            )
            if rec_id is None:
                continue
            try:
                entry = self.fetch_entry(rec_id)
                entries.append(entry)
            except ValueError as e:
                logger.warning(
                    "Skipping record %d (%s): %s",
                    rec_id,
                    rec_title,
                    e,
                )

        logger.info(
            "Successfully fetched %d of %d records as entries",
            len(entries),
            len(records),
        )

        return entries

    def upload_entry(self, entry, title=None, tags=None):
        r"""
        Upload a unitpackage Entry to Kadi4Mat as a new record.

        Creates a new record, uploads the CSV data as a file attachment,
        and sets metadata from the entry.

        Returns the ID of the newly created record.

        EXAMPLES::

            # from unitpackage.entry import Entry
            # import pandas as pd
            # df = pd.DataFrame({"t": [0, 1, 2], "E": [0.1, 0.2, 0.3]})
            # entry = Entry.from_df(df=df, basename="my_record")
            # client = KadiClient.from_env()
            # entity_id = client.upload_entry(entry, title="My Record")

        """
        record_title = title or entry.identifier
        identifier = re.sub(r"[^a-zA-Z0-9_-]", "_", record_title).lower().strip("_")
        if not identifier:
            identifier = f"unitpackage_{entry.identifier}"

        record = self._manager.record(
            identifier=identifier,
            title=record_title,
            create=True,
        )

        entity_id = (
            record.meta.get("id", None) if isinstance(record.meta, dict) else None
        )
        if entity_id is None:
            logger.warning(
                "Could not determine ID for created Kadi4Mat record '%s'", record_title
            )
        logger.info("Created record: %s (id=%s)", record_title, entity_id)

        # Upload CSV data as file attachment.  The filename must match the
        # ``path`` field in the datapackage descriptor so that the two can be
        # reliably linked when the record is fetched back.
        with tempfile.TemporaryDirectory() as tmpdir:
            csv_path = os.path.join(tmpdir, f"{entry.identifier}.csv")
            entry.df.to_csv(csv_path, index=False)
            record.upload_file(file_path=csv_path)
            logger.info("Uploaded CSV data for record %s", entity_id)

        # Store the full datapackage descriptor (schema + metadata) as a
        # nested Kadi dict metadatum so it is human-readable in the Kadi UI.
        descriptor = build_datapackage_descriptor(entry)
        record.add_metadatum(
            metadatum=_dict_to_kadi_extras(descriptor, key="unitpackage")
        )
        logger.info("Set datapackage descriptor on record %s", entity_id)

        # Add tags
        if tags:
            for tag in tags:
                record.add_tag(tag)
            logger.info("Added tags %s to record %s", tags, entity_id)

        return entity_id
