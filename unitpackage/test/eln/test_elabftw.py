"""
Comprehensive tests for unitpackage.elabftw -- the eLabFTW integration module.

Every eLabFTW API call is mocked; no live server is needed.
Run with:  pytest -m elabftw
"""

# pylint: disable=redefined-outer-name,protected-access,too-few-public-methods
# Parallel per-backend test suites share structurally similar assertions.
# pylint: disable=duplicate-code

import io
import json
from unittest.mock import MagicMock, Mock, patch

import pandas as pd
import pytest

from unitpackage.test.eln.fixture_loader import (
    CSV_DATA,
    SAMPLE_COLUMNS,
    SAMPLE_DESCRIPTOR,
    assert_basic_entry,
    assert_field_units,
    get_csv_bytes,
    get_versions,
    load_fixture,
    load_manifest,
    make_field_dict,
    make_mock_uploads,
)

# ---------------------------------------------------------------------------
# Fixture loader (recorded real API responses)
# ---------------------------------------------------------------------------


_BACKEND = "elabftw"
_ELABFTW_VERSIONS = get_versions(_BACKEND)

# ---------------------------------------------------------------------------
# Constants / mock data shared across tests
# ---------------------------------------------------------------------------

# eLabFTW stores the descriptor as JSON in the entity's ``metadata`` field,
# nested under a ``"unitpackage"`` key.
UNITPACKAGE_METADATA = {"unitpackage": SAMPLE_DESCRIPTOR}

_USE_DEFAULT = object()


def _make_entity_dict(
    exp_id=42,
    title="CV measurement on Pt(111)",
    tags="electrochemistry,CV",
    body="<p>Cyclic voltammetry experiment</p>",
    metadata=_USE_DEFAULT,
    created_at="2026-01-15",
    modified_at="2026-01-16",
    sharelink="https://elab.example.org/experiments.php?mode=view&id=42",
):
    """Return a dict mimicking a raw eLabFTW API JSON response for an entity."""
    if metadata is _USE_DEFAULT:
        metadata = UNITPACKAGE_METADATA
    return {
        "id": exp_id,
        "title": title,
        "tags": tags,
        "body": body,
        "metadata": json.dumps(metadata) if metadata is not None else None,
        "created_at": created_at,
        "modified_at": modified_at,
        "sharelink": sharelink,
    }


def _make_raw_response(data):
    """Wrap *data* in a response-like object with ``.data`` as JSON bytes.

    Mimics the urllib3 HTTPResponse returned by elabapi_python when
    ``_preload_content=False`` is used.
    """
    resp = Mock()
    resp.data = json.dumps(data).encode()
    return resp


def _make_mock_upload(
    upload_id=1, real_name="test_entry.csv", comment="Measurement data"
):
    """Return a Mock that looks like an eLabFTW upload object."""
    up = Mock()
    up.id = upload_id
    up.real_name = real_name
    up.comment = comment
    return up


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture()
def mock_experiment():
    """Raw response mimicking ``get_item(..., _preload_content=False)``."""
    if _ELABFTW_VERSIONS:
        version = _ELABFTW_VERSIONS[-1]
        # Use the patch_metadata response as entity data (get_entity.json only
        # has HTTP metadata since it was recorded with _preload_content=False).
        entity_data = load_fixture(_BACKEND, version, "patch_metadata")["response"]
        # Override metadata with the unitpackage descriptor from the request.
        entity_data["metadata"] = json.dumps(
            load_fixture(_BACKEND, version, "patch_metadata")["request"]["metadata"]
        )
        return _make_raw_response(entity_data)
    return _make_raw_response(_make_entity_dict())


@pytest.fixture()
def mock_upload():
    """Mock eLabFTW upload object."""
    if _ELABFTW_VERSIONS:
        uploads = make_mock_uploads(_BACKEND, _ELABFTW_VERSIONS[-1])
        return uploads[0]
    return _make_mock_upload()


@pytest.fixture(params=_ELABFTW_VERSIONS if _ELABFTW_VERSIONS else [None])
def fixture_version(request):
    """Pytest fixture: parameterised over each recorded eLabFTW version."""
    version = request.param
    if version is None:
        pytest.skip("No elabftw fixtures recorded")
    return version


# ---------------------------------------------------------------------------
# Helpers -- build a minimal ElabFTWClient without hitting the real API
# ---------------------------------------------------------------------------


def _make_client():  # pylint: disable=protected-access
    """
    Instantiate an ElabFTWClient with all API objects replaced by Mocks.

    The fake elabapi_python module is already injected into sys.modules
    by conftest.py, so we can import directly.
    """
    from unitpackage.eln.elabftw import ElabFTWClient

    client = ElabFTWClient.__new__(ElabFTWClient)
    client._entity_type = "items"
    client._api_client = MagicMock()
    client.items_client = MagicMock()
    client.uploads_client = MagicMock()
    return client


# ===================================================================
# Test: initialisation
# ===================================================================


@pytest.mark.elabftw
class TestClientInit:
    """Tests for ElabFTWClient.__init__ and from_env."""

    def test_client_init(self):
        """Configuration and ApiClient are created with the supplied values."""
        from unitpackage.eln.elabftw import ElabFTWClient

        with patch("unitpackage.eln.elabftw.elabapi_python") as elabapi:
            mock_config = MagicMock()
            elabapi.Configuration.return_value = mock_config

            mock_api_client = MagicMock()
            elabapi.ApiClient.return_value = mock_api_client

            client = ElabFTWClient(
                host="https://elab.example.org",
                api_key="test-key-123",
                verify_ssl=True,
            )

            elabapi.Configuration.assert_called_once()
            assert mock_config.host == "https://elab.example.org/api/v2"
            assert mock_config.verify_ssl is True
            assert client._entity_type == "items"  # pylint: disable=protected-access

    def test_client_init_no_verify_ssl(self):
        """Configuration.verify_ssl is set to False when verify_ssl=False."""
        from unitpackage.eln.elabftw import ElabFTWClient

        with patch("unitpackage.eln.elabftw.elabapi_python") as elabapi:
            mock_config = MagicMock()
            elabapi.Configuration.return_value = mock_config

            ElabFTWClient(
                host="https://elab.example.org",
                api_key="test-key-123",
                verify_ssl=False,
            )

            assert mock_config.verify_ssl is False

    def test_client_from_env(self):
        """from_env reads ELABFTW_HOST and ELABFTW_API_KEY from the environment."""
        from unitpackage.eln.elabftw import ElabFTWClient

        env = {
            "ELABFTW_HOST": "https://env.example.org",
            "ELABFTW_API_KEY": "env-key-456",
        }
        with (
            patch("unitpackage.eln.elabftw.elabapi_python"),
            patch.dict("os.environ", env, clear=False),
        ):
            ElabFTWClient.from_env()
            # Client was created without error

    def test_client_from_env_missing_vars(self):
        """from_env raises when the required env vars are absent."""
        from unitpackage.eln.elabftw import ElabFTWClient

        with patch.dict("os.environ", {}, clear=True):
            with pytest.raises((KeyError, ValueError, EnvironmentError)):
                ElabFTWClient.from_env()


# ===================================================================
# Test: info
# ===================================================================


@pytest.mark.elabftw
class TestInfo:
    """Tests for ElabFTWClient.info()."""

    def test_info(self):
        """info() delegates to InfoApi.get_info and returns a dict."""
        client = _make_client()

        mock_info = {
            "elabftw_version": "5.5.9",
            "teams_count": 3,
            "all_users_count": 25,
        }
        mock_info_api = MagicMock()
        mock_info_api.get_info.return_value = mock_info

        with patch("unitpackage.eln.elabftw.elabapi_python") as mock_elabapi:
            mock_elabapi.InfoApi.return_value = mock_info_api
            result = client.info()

        assert isinstance(result, dict)
        assert result["elabftw_version"] == "5.5.9"

    def test_info_normalizes_model_to_dict(self):
        """A model object (with ``.to_dict()``) is normalised to a plain dict.

        The real ``InfoApi.get_info()`` returns an ``Info`` model, not a dict;
        ``info()`` must convert it so the CLI's ``.get()`` lookups work.
        """
        client = _make_client()

        model = Mock(spec=["to_dict"])
        model.to_dict.return_value = {"elabftw_version": "5.5.14", "teams_count": 27}
        mock_info_api = MagicMock()
        mock_info_api.get_info.return_value = model

        with patch("unitpackage.eln.elabftw.elabapi_python") as mock_elabapi:
            mock_elabapi.InfoApi.return_value = mock_info_api
            result = client.info()

        assert isinstance(result, dict)
        assert result["elabftw_version"] == "5.5.14"
        assert result.get("teams_count") == 27


# ===================================================================
# Test: fetch_entry
# ===================================================================


@pytest.mark.elabftw
class TestFetchEntry:
    """Tests for ElabFTWClient.fetch_entry()."""

    def test_fetch_entry(self, mock_experiment, mock_upload, csv_bytes):
        """fetch_entry returns a valid Entry from an items entity."""
        client = _make_client()

        client.items_client.get_item.return_value = mock_experiment
        client.uploads_client.read_uploads.return_value = [mock_upload]

        csv_response = Mock()
        csv_response.data = csv_bytes
        client.uploads_client.read_upload.return_value = csv_response

        entry = client.fetch_entry(42)

        client.items_client.get_item.assert_called_once_with(42, _preload_content=False)
        client.uploads_client.read_uploads.assert_called_once_with("items", 42)

        assert_basic_entry(entry)

    def test_fetch_entry_no_matching_upload(self, mock_experiment):
        """fetch_entry raises ValueError when no upload matches the descriptor path."""
        client = _make_client()
        client.items_client.get_item.return_value = mock_experiment

        other = _make_mock_upload(real_name="something_else.csv")
        client.uploads_client.read_uploads.return_value = [other]

        with pytest.raises(ValueError, match="No upload named"):
            client.fetch_entry(42)

    def test_fetch_entry_rejects_non_unitpackage(self):
        """fetch_entry raises ValueError for entities without unitpackage metadata."""
        client = _make_client()

        client.items_client.get_item.return_value = _make_raw_response(
            _make_entity_dict(metadata={"some_other_tool": {}})
        )

        with pytest.raises(ValueError, match="not uploaded by unitpackage"):
            client.fetch_entry(42)

    def test_fetch_entry_rejects_empty_metadata(self):
        """fetch_entry raises ValueError for entities with no metadata."""
        client = _make_client()

        client.items_client.get_item.return_value = _make_raw_response(
            _make_entity_dict(metadata=None)
        )

        with pytest.raises(ValueError, match="not uploaded by unitpackage"):
            client.fetch_entry(42)

    def test_fetch_entry_metadata_mapping(self, csv_bytes):
        """Metadata stored under the 'unitpackage' key is restored on fetch."""
        client = _make_client()

        client.items_client.get_item.return_value = _make_raw_response(
            _make_entity_dict()
        )
        client.uploads_client.read_uploads.return_value = [_make_mock_upload()]

        csv_response = Mock()
        csv_response.data = csv_bytes
        client.uploads_client.read_upload.return_value = csv_response

        entry = client.fetch_entry(42)

        metadata = entry.resource.custom.get("metadata", {})
        assert metadata is not None
        assert "echemdb" in metadata


# ===================================================================
# Test: fetch_entries
# ===================================================================


@pytest.mark.elabftw
class TestFetchEntries:
    """Tests for ElabFTWClient.fetch_entries()."""

    def test_fetch_entries_all(self, csv_bytes):
        """fetch_entries returns multiple Entry objects."""
        client = _make_client()

        dict1 = _make_entity_dict(exp_id=1, title="Item_1")
        dict2 = _make_entity_dict(exp_id=2, title="Item_2")
        client.items_client.read_items.return_value = _make_raw_response([dict1, dict2])

        # fetch_entries calls fetch_entry for each, which calls get_item
        client.items_client.get_item.side_effect = [
            _make_raw_response(dict1),
            _make_raw_response(dict2),
        ]

        client.uploads_client.read_uploads.return_value = [_make_mock_upload()]
        csv_response = Mock()
        csv_response.data = csv_bytes
        client.uploads_client.read_upload.return_value = csv_response

        entries = client.fetch_entries()

        assert len(entries) == 2
        for e in entries:
            assert hasattr(e, "df")

    def test_fetch_entries_skips_non_unitpackage(self, csv_bytes):
        """fetch_entries only returns entities with unitpackage metadata."""
        client = _make_client()

        up_dict = _make_entity_dict(exp_id=1, title="UP_Item")
        foreign_dict = _make_entity_dict(
            exp_id=2, title="Foreign", metadata={"other": {}}
        )
        no_meta_dict = _make_entity_dict(exp_id=3, title="NoMeta", metadata=None)

        client.items_client.read_items.return_value = _make_raw_response(
            [up_dict, foreign_dict, no_meta_dict]
        )

        # Only up_dict should be fetched
        client.items_client.get_item.return_value = _make_raw_response(up_dict)
        client.uploads_client.read_uploads.return_value = [_make_mock_upload()]
        csv_response = Mock()
        csv_response.data = csv_bytes
        client.uploads_client.read_upload.return_value = csv_response

        entries = client.fetch_entries()

        assert len(entries) == 1
        # get_item should only be called once (for the unitpackage entity)
        client.items_client.get_item.assert_called_once_with(1, _preload_content=False)

    def test_fetch_entries_with_tags(self, csv_bytes):
        """fetch_entries filters by tags when provided."""
        client = _make_client()

        dict1 = _make_entity_dict(exp_id=1, title="I1", tags="electrochemistry,CV")
        client.items_client.read_items.return_value = _make_raw_response([dict1])

        # fetch_entries calls fetch_entry which calls get_item
        client.items_client.get_item.return_value = _make_raw_response(dict1)

        client.uploads_client.read_uploads.return_value = [_make_mock_upload()]
        csv_response = Mock()
        csv_response.data = csv_bytes
        client.uploads_client.read_upload.return_value = csv_response

        entries = client.fetch_entries(tags=["CV"])

        # The tag must be forwarded to the eLabFTW read_items API call.
        call_kwargs = client.items_client.read_items.call_args.kwargs
        assert call_kwargs.get("tags") == ["CV"]
        assert len(entries) == 1


# ===================================================================
# Test: upload_entry
# ===================================================================


@pytest.mark.elabftw
class TestUploadEntry:
    """Tests for ElabFTWClient.upload_entry()."""

    def test_upload_entry(self, sample_entry):
        """upload_entry posts an item, uploads CSV, and patches metadata."""
        client = _make_client()

        client.items_client.post_item_with_http_info.return_value = (
            None,
            201,
            {"Location": "/api/v2/items/100"},
        )

        result = client.upload_entry(sample_entry)

        client.items_client.post_item_with_http_info.assert_called_once()
        assert client.uploads_client.post_upload.call_count == 1  # CSV only
        client.items_client.patch_item.assert_called_once()
        # Verify metadata contains the unitpackage descriptor
        patch_args = client.items_client.patch_item.call_args
        body = patch_args.args[0]
        metadata = json.loads(body["metadata"])
        assert "unitpackage" in metadata
        assert result == 100

    def test_upload_entry_custom_title(self, sample_entry):
        """A custom title is forwarded to the API call."""
        client = _make_client()

        client.items_client.post_item_with_http_info.return_value = (
            None,
            201,
            {"Location": "/api/v2/items/101"},
        )

        client.upload_entry(sample_entry, title="My Custom Title")

        call_kwargs = client.items_client.post_item_with_http_info.call_args
        body = call_kwargs.kwargs.get("body", {})
        assert body.get("title") == "My Custom Title"

    def test_upload_entry_with_tags(self, sample_entry):
        """Tags are forwarded into the item creation body."""
        client = _make_client()

        client.items_client.post_item_with_http_info.return_value = (
            None,
            201,
            {"Location": "/api/v2/items/105"},
        )

        client.upload_entry(sample_entry, tags=["test", "cv"])

        call_kwargs = client.items_client.post_item_with_http_info.call_args
        body = call_kwargs.kwargs.get("body", {})
        assert body.get("tags") == ["test", "cv"]

    def test_upload_entry_stores_unitpackage_metadata(self, sample_entry):
        """upload_entry stores the datapackage descriptor under the 'unitpackage' key."""
        client = _make_client()

        client.items_client.post_item_with_http_info.return_value = (
            None,
            201,
            {"Location": "/api/v2/items/102"},
        )

        client.upload_entry(sample_entry)

        patch_args = client.items_client.patch_item.call_args
        body = patch_args.args[0]
        metadata = json.loads(body["metadata"])
        assert "unitpackage" in metadata
        assert "resources" in metadata["unitpackage"]
        resource = metadata["unitpackage"]["resources"][0]
        assert resource["name"] == "test_entry"
        assert "schema" in resource

    def test_upload_entry_cleans_up_on_failure(self, sample_entry):
        """Partially created item is deleted when upload fails."""
        client = _make_client()

        client.items_client.post_item_with_http_info.return_value = (
            None,
            201,
            {"Location": "/api/v2/items/200"},
        )
        client.uploads_client.post_upload.side_effect = RuntimeError("upload failed")

        with pytest.raises(RuntimeError, match="upload failed"):
            client.upload_entry(sample_entry)

        client.items_client.delete_item.assert_called_once_with(200)

    def test_upload_entry_missing_location_header(self, sample_entry):
        """A missing Location header raises a clear error, not AttributeError."""
        client = _make_client()

        client.items_client.post_item_with_http_info.return_value = (None, 201, {})

        with pytest.raises(ValueError, match="Location"):
            client.upload_entry(sample_entry)


# ===================================================================
# Test: round-trip upload → fetch
# ===================================================================


@pytest.mark.elabftw
class TestRoundTrip:
    """Tests for upload → fetch round-trip."""

    def test_upload_then_fetch_preserves_entry(self, sample_entry):
        """Full round-trip via entity metadata field."""
        client = _make_client()

        # --- Upload phase ---
        client.items_client.post_item_with_http_info.return_value = (
            None,
            201,
            {"Location": "/api/v2/items/100"},
        )

        client.upload_entry(sample_entry)

        # Capture the metadata that was patched onto the entity
        patch_args = client.items_client.patch_item.call_args
        body = patch_args.args[0]
        stored_metadata_json = body["metadata"]

        # --- Fetch phase ---
        # Build a raw response with the stored metadata
        entity_dict = _make_entity_dict(exp_id=100, title="test_entry")
        entity_dict["metadata"] = stored_metadata_json
        client.items_client.get_item.return_value = _make_raw_response(entity_dict)

        csv_upload = _make_mock_upload(upload_id=1, real_name="test_entry.csv")
        client.uploads_client.read_uploads.return_value = [csv_upload]

        csv_response = Mock()
        csv_response.data = CSV_DATA
        client.uploads_client.read_upload.return_value = csv_response

        result = client.fetch_entry(100)

        # Assert field units and column names are faithfully preserved
        assert_field_units(result)
        assert list(result.df.columns) == SAMPLE_COLUMNS


# ===================================================================
# Test: fixture-based tests (recorded real API responses)
# ===================================================================


@pytest.mark.elabftw
class TestFixtureVersions:
    """Tests that replay recorded real eLabFTW API responses."""

    def _wire_client(self, version):
        """Return (client, entity_id) with mocks populated from fixture data."""
        client = _make_client()

        # Use the patch_metadata response as entity data source.
        # (get_entity.json only has HTTP metadata since it was recorded
        # with _preload_content=False.)
        patch_data = load_fixture(_BACKEND, version, "patch_metadata")
        entity_data = dict(patch_data["response"])
        entity_id = entity_data["id"]

        # Override metadata with the unitpackage descriptor from the request.
        entity_data["metadata"] = json.dumps(patch_data["request"]["metadata"])

        client.items_client.get_item.return_value = _make_raw_response(entity_data)

        uploads = make_mock_uploads(_BACKEND, version)
        client.uploads_client.read_uploads.return_value = uploads

        csv_data = get_csv_bytes(_BACKEND, version)

        csv_response = Mock()
        csv_response.data = csv_data
        client.uploads_client.read_upload.return_value = csv_response

        return client, entity_id

    def test_fetch_entry_from_fixture(self, fixture_version):
        """fetch_entry returns a valid Entry from a real recorded fixture."""
        client, entity_id = self._wire_client(fixture_version)
        entry = client.fetch_entry(entity_id)
        assert entry is not None
        assert hasattr(entry, "df")
        assert len(entry.df) > 0

    def test_fetch_entry_columns_from_fixture(self, fixture_version):
        """fetch_entry returns an Entry with the correct column names."""
        client, entity_id = self._wire_client(fixture_version)
        entry = client.fetch_entry(entity_id)
        assert "t" in entry.df.columns
        assert "E" in entry.df.columns

    def test_fetch_entry_restores_units_from_fixture(self, fixture_version):
        """fetch_entry restores field units from the stored datapackage.json."""
        client, entity_id = self._wire_client(fixture_version)
        entry = client.fetch_entry(entity_id)
        assert_field_units(entry)

    def test_fetch_entry_restores_metadata_from_fixture(self, fixture_version):
        """fetch_entry restores metadata stored in the datapackage descriptor."""
        client, entity_id = self._wire_client(fixture_version)
        entry = client.fetch_entry(entity_id)
        custom = entry.resource.custom
        metadata = custom.get("metadata", {})
        assert "echemdb" in metadata

    def test_info_from_fixture(self, fixture_version):
        """info() returns data matching the recorded fixture."""
        client = _make_client()
        info_data = load_fixture(_BACKEND, fixture_version, "info")["response"]

        mock_info_api = MagicMock()
        mock_info_api.get_info.return_value = info_data

        with patch("unitpackage.eln.elabftw.elabapi_python") as mock_elabapi:
            mock_elabapi.InfoApi.return_value = mock_info_api
            result = client.info()

        assert isinstance(result, dict)
        assert "elabftw_version" in result

    def test_upload_entry_from_fixture(self, fixture_version, sample_entry):
        """upload_entry succeeds with real recorded response shapes."""
        client = _make_client()
        post_data = load_fixture(_BACKEND, fixture_version, "post_entity")["response"]

        client.items_client.post_item_with_http_info.return_value = (
            None,
            post_data["status_code"],
            {"Location": post_data["location"]},
        )

        result = client.upload_entry(sample_entry)
        assert result == post_data["entity_id"]

    def test_fetch_entries_from_fixture(self, fixture_version):
        """fetch_entries returns entries using recorded fixture data."""
        client, _entity_id = self._wire_client(fixture_version)

        # Build listing response from the same entity data source.
        patch_data = load_fixture(_BACKEND, fixture_version, "patch_metadata")
        entity_data = dict(patch_data["response"])
        entity_data["metadata"] = json.dumps(patch_data["request"]["metadata"])

        client.items_client.read_items.return_value = _make_raw_response([entity_data])

        entries = client.fetch_entries()
        assert len(entries) == 1
        assert_basic_entry(entries[0])
        assert_field_units(entries[0])

    def test_fetch_entry_csv_values_from_fixture(self, fixture_version):
        """Fetched DataFrame values match the recorded CSV byte-for-byte."""
        client, entity_id = self._wire_client(fixture_version)
        entry = client.fetch_entry(entity_id)

        csv_data = get_csv_bytes(_BACKEND, fixture_version)
        expected_df = pd.read_csv(io.BytesIO(csv_data))
        pd.testing.assert_frame_equal(entry.df, expected_df)

    def test_fetch_entry_matches_manifest(self, fixture_version):
        """Fetched entry columns and units match the manifest test_data."""
        client, entity_id = self._wire_client(fixture_version)
        entry = client.fetch_entry(entity_id)

        manifest = load_manifest(_BACKEND, fixture_version)
        test_data = manifest["test_data"]
        assert list(entry.df.columns) == test_data["csv_columns"]

        field_dict = make_field_dict(entry)
        for name, unit in test_data["field_units"].items():
            assert field_dict[name].get("unit") == unit

    def test_fetch_entry_identifier_from_fixture(self, fixture_version):
        """Entry identifier matches the descriptor resource name."""
        client, entity_id = self._wire_client(fixture_version)
        entry = client.fetch_entry(entity_id)

        patch_data = load_fixture(_BACKEND, fixture_version, "patch_metadata")
        descriptor = patch_data["request"]["metadata"]["unitpackage"]
        expected_name = descriptor["resources"][0]["name"]
        assert entry.identifier == expected_name

    def test_info_version_from_fixture(self, fixture_version):
        """Info response version matches the fixture directory name."""
        client = _make_client()
        info_data = load_fixture(_BACKEND, fixture_version, "info")["response"]

        mock_info_api = MagicMock()
        mock_info_api.get_info.return_value = info_data

        with patch("unitpackage.eln.elabftw.elabapi_python") as mock_elabapi:
            mock_elabapi.InfoApi.return_value = mock_info_api
            result = client.info()

        assert result.get("elabftw_version") == fixture_version

    def test_fetch_entry_metadata_values_from_fixture(self, fixture_version):
        """Metadata citationKey is preserved through the round-trip."""
        client, entity_id = self._wire_client(fixture_version)
        entry = client.fetch_entry(entity_id)

        metadata = entry.resource.custom.get("metadata", {})
        source = metadata.get("echemdb", {}).get("source", {})
        assert "citationKey" in source
        assert isinstance(source["citationKey"], str)
        assert len(source["citationKey"]) > 0
