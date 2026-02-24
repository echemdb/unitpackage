#!/usr/bin/env python
"""
Record API fixtures from a real eLabFTW instance for mock-based testing.

Connects to a live eLabFTW instance, performs the standard unitpackage
operations (info, upload, fetch_entry, fetch_entries), and records the raw
API responses as JSON fixture files.  Fixtures are saved in versioned
directories so that API changes across eLabFTW releases can be tracked
and tested against.

Usage::

    # Version auto-detected from server info
    python test/record_fixtures.py elabftw

    # With explicit credentials
    python test/record_fixtures.py elabftw --host https://eln.example.org --api-key KEY

    # Keep the test entity on the server
    python test/record_fixtures.py elabftw --no-cleanup

    # Custom output directory
    python test/record_fixtures.py elabftw --outdir /tmp/my_fixtures

Credentials are resolved in this order:
  1. CLI options (--host, --api-key)
  2. Environment variables (ELABFTW_HOST, ELABFTW_API_KEY)
  3. Configuration file (~/.config/unitpackage/config.toml, via --profile)
"""

import base64
import io
import json
import logging
import os
import re
import sys
import tempfile
import uuid
from datetime import datetime, timezone
from functools import wraps
from pathlib import Path

import click
import pandas as pd

# Ensure the unitpackage package is importable when running from the repo root.
_REPO_ROOT = Path(__file__).resolve().parent.parent
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from unitpackage.entry import Entry  # noqa: E402

logger = logging.getLogger("unitpackage.record_fixtures")

FIXTURES_DIR = Path(__file__).parent / "fixtures"

# ---------------------------------------------------------------------------
# Standard test data
# ---------------------------------------------------------------------------

TEST_CSV_DATA = "t,E,j\n0.0,-0.103,43.01\n0.01,-0.102,51.41\n0.02,-0.101,42.89\n"
TEST_FIELDS = [
    {"name": "t", "unit": "s"},
    {"name": "E", "unit": "V"},
    {"name": "j", "unit": "A / m2"},
]
TEST_METADATA = {"echemdb": {"source": {"citationKey": "fixture_test_2026"}}}
TEST_TITLE_PREFIX = "unitpackage_fixture_test"
TEST_TITLE_RE = re.compile(r"^unitpackage_fixture_test_[0-9a-f]{8}$")
TEST_TAGS = ["unitpackage-test"]


def _build_test_entry():
    """Build the standard test Entry used for fixture recording."""
    df = pd.read_csv(io.StringIO(TEST_CSV_DATA))
    entry = Entry.from_df(df=df, basename="fixture_test")
    entry = entry.update_fields(fields=TEST_FIELDS)
    entry.metadata.from_dict(TEST_METADATA)
    return entry


# ---------------------------------------------------------------------------
# Serialization helpers
# ---------------------------------------------------------------------------


def _save_json(data, directory, filename):
    """Write *data* as pretty-printed JSON to *directory*/*filename*."""
    os.makedirs(directory, exist_ok=True)
    path = os.path.join(directory, filename)
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(data, fh, indent=2, default=str, ensure_ascii=False)
    logger.info("Saved %s", path)


def _redact(data, replacements):
    """Recursively replace sensitive strings in fixture data.

    *replacements* is a list of ``(sensitive, placeholder)`` pairs.
    Only non-empty *sensitive* strings are replaced.  Apply the most
    specific replacements first (e.g., full name before first/last name).
    """
    if not replacements:
        return data
    if isinstance(data, str):
        for sensitive, placeholder in replacements:
            if sensitive:
                data = data.replace(sensitive, placeholder)
        return data
    if isinstance(data, dict):
        return {k: _redact(v, replacements) for k, v in data.items()}
    if isinstance(data, list):
        return [_redact(item, replacements) for item in data]
    return data


def _redact_directory(version_dir, replacements):
    """Apply *replacements* to all JSON files in *version_dir* in-place."""
    if not replacements:
        return
    for json_path in sorted(Path(version_dir).glob("*.json")):
        with open(json_path, encoding="utf-8") as fh:
            data = json.load(fh)
        redacted = _redact(data, replacements)
        with open(json_path, "w", encoding="utf-8") as fh:
            json.dump(redacted, fh, indent=2, default=str, ensure_ascii=False)
        logger.debug("Redacted %s", json_path)


def _serialize(obj):
    """Best-effort serialization of an API response object to a JSON-safe value."""
    if obj is None:
        return None
    if isinstance(obj, (str, int, float, bool)):
        return obj
    if isinstance(obj, bytes):
        return base64.b64encode(obj).decode("ascii")
    if isinstance(obj, dict):
        return {k: _serialize(v) for k, v in obj.items()}
    if isinstance(obj, (list, tuple)):
        return [_serialize(item) for item in obj]
    if hasattr(obj, "to_dict"):
        return obj.to_dict()
    if hasattr(obj, "__dict__"):
        return {
            k: _serialize(v)
            for k, v in obj.__dict__.items()
            if not k.startswith("_")
        }
    return str(obj)


# ---------------------------------------------------------------------------
# Recording wrapper helpers
# ---------------------------------------------------------------------------


def _unwrap(obj, method_name):
    """Restore *obj.method_name* to the original if it was previously wrapped."""
    current = getattr(obj, method_name)
    original = getattr(current, "_recording_original", None)
    if original is not None:
        setattr(obj, method_name, original)


def _wrap(obj, method_name, store, operation_name, full_method_name):
    """Replace *obj.method_name* with a wrapper that records the response."""
    _unwrap(obj, method_name)
    original = getattr(obj, method_name)

    @wraps(original)
    def wrapper(*args, **kwargs):
        result = original(*args, **kwargs)
        store[operation_name] = {
            "operation": operation_name,
            "method": full_method_name,
            "response": _serialize(result),
        }
        return result

    wrapper._recording_original = original
    setattr(obj, method_name, wrapper)


def _wrap_binary(obj, method_name, store, full_method_name):
    """Replace *obj.method_name* with a wrapper that records binary responses."""
    _unwrap(obj, method_name)
    original = getattr(obj, method_name)
    call_count = [0]

    @wraps(original)
    def wrapper(*args, **kwargs):
        result = original(*args, **kwargs)
        call_count[0] += 1

        data = getattr(result, "data", result)
        if isinstance(data, bytes):
            serialized = {"data_base64": base64.b64encode(data).decode("ascii")}
        else:
            serialized = _serialize(data)

        # First binary download is CSV, second is datapackage.json.
        op_name = "download_csv" if call_count[0] == 1 else "download_datapackage"
        store[op_name] = {
            "operation": op_name,
            "method": full_method_name,
            "response": serialized,
        }
        return result

    wrapper._recording_original = original
    setattr(obj, method_name, wrapper)


# ---------------------------------------------------------------------------
# eLabFTW recorder
# ---------------------------------------------------------------------------


class ElabFTWRecorder:
    """Record API fixtures from a real eLabFTW instance."""

    backend_name = "elabftw"

    def get_redaction_replacements(self, client, info_dict):
        replacements = []
        # eLabFTW info() does not include the host URL; extract it from the
        # API client configuration (strips the /api/v2 suffix).
        config_host = getattr(
            getattr(getattr(client, "_api_client", None), "configuration", None),
            "host", "",
        )
        if config_host:
            base_host = re.sub(r"/api/v\d+.*$", "", config_host)
            if base_host:
                replacements.append((base_host, "https://elabftw.example.org"))
        return replacements

    def _extract_additional_replacements(self, version_dir):
        """Extract user name fields from the recorded patch_metadata response."""
        replacements = []
        entity_path = Path(version_dir) / "patch_metadata.json"
        if not entity_path.exists():
            return replacements
        try:
            with open(entity_path, encoding="utf-8") as fh:
                data = json.load(fh)
            resp = data.get("response", {})
            # Full name first (most specific), then parts.
            fullname = resp.get("fullname", "")
            if fullname:
                replacements.append((fullname, "Test User"))
            firstname = resp.get("firstname", "")
            if firstname:
                replacements.append((firstname, "Test"))
            lastname = resp.get("lastname", "")
            if lastname:
                replacements.append((lastname, "User"))
        except Exception as exc:
            logger.debug("Could not extract user fields from patch_metadata.json: %s", exc)
        return replacements

    def extract_version(self, info_dict):
        version = info_dict.get("elabftw_version") or info_dict.get("version")
        if not version:
            raise ValueError(
                "Could not extract version from eLabFTW info response. "
                "Use --version to specify it manually."
            )
        return str(version)

    def create_test_entry(self, client, version_dir, title):
        """Create a test item using raw elabapi_python calls."""
        from unitpackage.eln import build_datapackage_descriptor

        api = client.items_client

        # Step 1: Create the item
        body = {"title": title, "tags": list(TEST_TAGS)}
        _, status_code, headers = api.post_item_with_http_info(body=body)

        location = headers.get("Location")
        entity_id = int(location.split("/").pop())

        _save_json(
            {
                "operation": "post_entity",
                "method": "ItemsApi.post_item_with_http_info",
                "request": {"body": body},
                "response": {
                    "status_code": status_code,
                    "location": location,
                    "entity_id": entity_id,
                },
            },
            version_dir,
            "post_entity.json",
        )
        click.echo(f"    POST items -> {entity_id}")

        # Step 2: Upload CSV file
        entry = _build_test_entry()
        with tempfile.TemporaryDirectory() as tmpdir:
            csv_path = os.path.join(tmpdir, f"{entry.identifier}.csv")
            entry.df.to_csv(csv_path, index=False)
            csv_upload_result = client.uploads_client.post_upload(
                "items", entity_id, file=csv_path,
                comment="Data uploaded from unitpackage",
            )
            _save_json(
                {
                    "operation": "post_upload_csv",
                    "method": "UploadsApi.post_upload",
                    "request": {
                        "entity_type": "items",
                        "entity_id": entity_id,
                        "comment": "Data uploaded from unitpackage",
                    },
                    "response": _serialize(csv_upload_result),
                },
                version_dir,
                "post_upload_csv.json",
            )
            click.echo("    POST upload (CSV)")

        # Step 3: Store datapackage descriptor in entity metadata
        descriptor = build_datapackage_descriptor(entry)
        metadata = {"unitpackage": descriptor}
        metadata_json = json.dumps(metadata, default=str)
        patch_result = api.patch_item(entity_id, body={"metadata": metadata_json})

        _save_json(
            {
                "operation": "patch_metadata",
                "method": "ItemsApi.patch_item",
                "request": {
                    "entity_id": entity_id,
                    "metadata": metadata,
                },
                "response": _serialize(patch_result),
            },
            version_dir,
            "patch_metadata.json",
        )
        click.echo("    PATCH metadata (unitpackage descriptor)")

        return entity_id

    def install_hooks(self, client, store):
        api = client.items_client
        _wrap(api, "get_item", store, "get_entity", "ItemsApi.get_item")
        _wrap(api, "read_items", store, "list_entities", "ItemsApi.read_items")

        _wrap(
            client.uploads_client, "read_uploads", store,
            "list_uploads", "UploadsApi.read_uploads",
        )
        _wrap_binary(
            client.uploads_client, "read_upload", store,
            "UploadsApi.read_upload",
        )

    def cleanup_leftovers(self, client):
        """Delete leftover test entities from previous runs."""
        try:
            entities = self.list_test_entities(client)
        except Exception as exc:
            click.echo(f"  WARNING: Could not list leftover entities: {exc}", err=True)
            return

        for entity_id, title in entities:
            if not TEST_TITLE_RE.match(title or ""):
                click.echo(f"  Skipping entity {entity_id} ({title!r}): title does not match fixture pattern")
                continue
            try:
                self.delete_entity(client, entity_id)
                click.echo(f"  Deleted leftover entity {entity_id} ({title})")
            except Exception as exc:
                click.echo(f"  WARNING: Failed to delete entity {entity_id}: {exc}", err=True)

    def list_test_entities(self, client):
        entities = client.items_client.read_items(tags=list(TEST_TAGS), limit=9999)
        return [(e.id, e.title) for e in entities]

    def delete_entity(self, client, entity_id):
        client.items_client.delete_item(entity_id)

    def record(self, client, outdir, cleanup=True, version_override=None):
        """Run the full recording workflow against a real eLabFTW instance."""
        entity_id = None
        captured = {}

        # Phase 0: clean up leftovers from previous runs
        click.echo("Cleaning up leftover test entities...")
        self.cleanup_leftovers(client)

        try:
            # Phase 1: server info
            click.echo("Recording server info...")
            info_dict = client.info()
            version = version_override or self.extract_version(info_dict)
            version_dir = os.path.join(outdir, version)
            _save_json(
                {"operation": "info", "method": "client.info", "response": info_dict},
                version_dir,
                "info.json",
            )
            click.echo(f"  ELN version: {version}")

            # Phase 2: create test entry using raw API calls (recorded per-step)
            uid = uuid.uuid4().hex[:8]
            title = f"{TEST_TITLE_PREFIX}_{uid}"
            click.echo(f"Creating test entry via raw API ({title})...")
            entity_id = self.create_test_entry(client, version_dir, title)
            click.echo(f"  Created test entity: {entity_id}")

            # Phase 3: install hooks and fetch entry back
            click.echo("Fetching test entity with recording hooks...")
            self.install_hooks(client, captured)
            fetched = client.fetch_entry(entity_id)
            assert fetched is not None, "fetch_entry returned None"

            for op_name, data in captured.items():
                _save_json(data, version_dir, f"{op_name}.json")
            click.echo(f"  Recorded {len(captured)} API responses")

            # Phase 4: fetch_entries
            click.echo("Recording fetch_entries...")
            captured_list = {}
            self.install_hooks(client, captured_list)
            entries = client.fetch_entries(tags=TEST_TAGS)
            for op_name, data in captured_list.items():
                _save_json(data, version_dir, f"list_{op_name}.json")

            _save_json(
                {
                    "operation": "fetch_entries",
                    "method": "client.fetch_entries",
                    "response": {"count": len(entries)},
                },
                version_dir,
                "fetch_entries.json",
            )
            click.echo(f"  Found {len(entries)} entries via fetch_entries")

        except Exception:
            logger.exception("Recording failed")
            if entity_id is not None and cleanup:
                self._try_cleanup(client, entity_id)
            raise

        else:
            # Phase 5: cleanup
            cleanup_performed = False
            if cleanup and entity_id is not None:
                cleanup_performed = self._try_cleanup(client, entity_id)
            elif entity_id is not None:
                click.echo(f"  Skipping cleanup (entity {entity_id} kept on server)")

            # Write manifest
            try:
                from unitpackage import __version__ as up_version
            except (ImportError, AttributeError):
                up_version = "unknown"

            manifest = {
                "backend": self.backend_name,
                "version": version,
                "recorded_at": datetime.now(timezone.utc).isoformat(),
                "unitpackage_version": up_version,
                "entity_id": entity_id,
                "cleanup_performed": cleanup_performed,
                "test_data": {
                    "csv_columns": ["t", "E", "j"],
                    "field_units": {f["name"]: f["unit"] for f in TEST_FIELDS},
                    "title": title,
                },
            }
            _save_json(manifest, version_dir, "manifest.json")

            # Redact sensitive information from all fixture files
            replacements = self.get_redaction_replacements(client, info_dict)
            replacements.extend(self._extract_additional_replacements(version_dir))
            if replacements:
                _redact_directory(version_dir, replacements)
                click.echo(f"  Redacted {len(replacements)} sensitive value(s) from fixture files")

            click.echo(f"Fixture recording complete: {version_dir}")

    def _try_cleanup(self, client, entity_id):
        """Best-effort cleanup of the test entity."""
        try:
            self.delete_entity(client, entity_id)
            click.echo(f"  Cleaned up test entity {entity_id}")
            return True
        except Exception as exc:
            click.echo(
                f"  WARNING: Cleanup of entity {entity_id} failed: {exc}\n"
                "  Manual cleanup required.",
                err=True,
            )
            return False


# ---------------------------------------------------------------------------
# Client resolution helper
# ---------------------------------------------------------------------------


def _resolve_elabftw_client(host, api_key, no_verify_ssl, profile):
    from unitpackage.eln.elabftw import ElabFTWClient

    if host and api_key:
        return ElabFTWClient(
            host=host, api_key=api_key,
            verify_ssl=not no_verify_ssl,
        )

    from unitpackage.config import config_path, get_profile

    settings = get_profile("elabftw", profile=profile)
    if not settings:
        raise click.UsageError(
            "Missing eLabFTW credentials. Provide --host and --api-key, "
            "set ELABFTW_HOST/ELABFTW_API_KEY environment variables, "
            f"or add an [elabftw.<name>] section to {config_path()}."
        )

    resolved_host = host or settings.get("host")
    resolved_api_key = api_key or settings.get("api_key")
    if not resolved_host or not resolved_api_key:
        raise click.UsageError("Missing host or API key in credentials.")

    verify_ssl = not no_verify_ssl if no_verify_ssl else settings.get("verify_ssl", True)
    return ElabFTWClient(
        host=resolved_host, api_key=resolved_api_key,
        verify_ssl=verify_ssl,
    )


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


@click.command()
@click.option("-v", "--verbose", is_flag=True, help="Enable verbose logging")
@click.option("--host", envvar="ELABFTW_HOST", default=None, help="eLabFTW server URL")
@click.option("--api-key", envvar="ELABFTW_API_KEY", default=None, help="eLabFTW API key")
@click.option("--no-verify-ssl", is_flag=True, default=False, help="Disable SSL verification")
@click.option("--profile", default=None, help="Config profile name")
@click.option("--version", "version_override", default=None, help="Override detected version")
@click.option("--no-cleanup", is_flag=True, default=False, help="Keep test entity on server")
@click.option("--outdir", default=None, help="Output directory (default: test/fixtures/elabftw)")
def cli(verbose, host, api_key, no_verify_ssl, profile, version_override, no_cleanup, outdir):
    """Record API fixtures from a real eLabFTW instance for mock-based testing."""
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(level=level, format="%(levelname)s: %(message)s")

    client = _resolve_elabftw_client(host, api_key, no_verify_ssl, profile)
    outdir = outdir or str(FIXTURES_DIR / "elabftw")
    try:
        ElabFTWRecorder().record(client, outdir, cleanup=not no_cleanup, version_override=version_override)
    finally:
        # Explicitly shut down the thread pool so Python's atexit doesn't
        # hit a closed file descriptor in ApiClient.__del__.
        pool = getattr(client._api_client, "pool", None)
        if pool is not None:
            pool.close()
            pool.join()


if __name__ == "__main__":
    cli()
