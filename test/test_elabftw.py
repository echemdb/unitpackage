"""
Comprehensive tests for unitpackage.elabftw -- the eLabFTW integration module.

Every eLabFTW API call is mocked; no live server is needed.
Run with:  pytest -m elabftw
"""

import json
import sys
from pathlib import Path
from unittest.mock import MagicMock, Mock, patch

import pandas as pd
import pytest

# ---------------------------------------------------------------------------
# Fixture loader (recorded real API responses)
# ---------------------------------------------------------------------------

sys.path.insert(0, str(Path(__file__).parent))
from fixture_loader import get_versions, load_fixture, get_csv_bytes, make_field_dict, make_mock_uploads  # noqa: E402

_BACKEND = "elabftw"
_ELABFTW_VERSIONS = get_versions(_BACKEND)

# ---------------------------------------------------------------------------
# Constants / mock data shared across tests
# ---------------------------------------------------------------------------

CSV_DATA = b"t,E,j\n0.0,-0.103,43.01\n0.01,-0.102,51.41\n0.02,-0.101,42.89\n"

UNITPACKAGE_METADATA = {
    "unitpackage": {
        "resources": [
            {
                "name": "test_entry",
                "type": "table",
                "path": "test_entry.csv",
                "format": "csv",
                "mediatype": "text/csv",
                "schema": {
                    "fields": [
                        {"name": "t", "type": "number", "unit": "s"},
                        {"name": "E", "type": "number", "unit": "V"},
                        {"name": "j", "type": "number", "unit": "A / m2"},
                    ]
                },
                "metadata": {
                    "echemdb": {
                        "source": {"citationKey": "test_2026"},
                    }
                },
            }
        ]
    }
}

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


def _make_mock_upload(upload_id=1, real_name="test_entry.csv", comment="Measurement data"):
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
    if _ELABFTW_VERSIONS:
        uploads = make_mock_uploads(_BACKEND, _ELABFTW_VERSIONS[-1])
        return uploads[0]
    return _make_mock_upload()


@pytest.fixture()
def csv_bytes():
    return CSV_DATA


@pytest.fixture()
def sample_df():
    """A small DataFrame matching CSV_DATA."""
    return pd.DataFrame(
        {
            "t": [0.0, 0.01, 0.02],
            "E": [-0.103, -0.102, -0.101],
            "j": [43.01, 51.41, 42.89],
        }
    )


@pytest.fixture()
def sample_entry(sample_df):
    """A unitpackage Entry built from the sample DataFrame."""
    from unitpackage.entry import Entry

    entry = Entry.from_df(df=sample_df, basename="test_entry")
    fields = [
        {"name": "t", "unit": "s"},
        {"name": "E", "unit": "V"},
        {"name": "j", "unit": "A / m2"},
    ]
    entry = entry.update_fields(fields=fields)
    entry.metadata.from_dict(
        {
            "echemdb": {
                "source": {"citationKey": "test_2026"},
            },
        }
    )
    return entry


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


def _make_client():
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
            assert client._entity_type == "items"

    def test_client_from_env(self):
        """from_env reads ELABFTW_HOST and ELABFTW_API_KEY from the environment."""
        from unitpackage.eln.elabftw import ElabFTWClient

        env = {
            "ELABFTW_HOST": "https://env.example.org",
            "ELABFTW_API_KEY": "env-key-456",
        }
        with patch("unitpackage.eln.elabftw.elabapi_python"), patch.dict(
            "os.environ", env, clear=False
        ):
            client = ElabFTWClient.from_env()
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
    def test_info(self):
        """info() delegates to InfoApi.get_info and returns a dict."""
        client = _make_client()

        mock_info = Mock()
        mock_info.to_dict.return_value = {
            "elabftw_version": "5.1.0",
            "teams_count": 3,
            "all_users_count": 25,
        }
        mock_info_api = MagicMock()
        mock_info_api.get_info.return_value = mock_info

        with patch("unitpackage.eln.elabftw.elabapi_python") as mock_elabapi:
            mock_elabapi.InfoApi.return_value = mock_info_api
            result = client.info()

        assert isinstance(result, dict)
        assert result["elabftw_version"] == "5.1.0"


# ===================================================================
# Test: fetch_entry
# ===================================================================


@pytest.mark.elabftw
class TestFetchEntry:
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

        assert entry is not None
        assert hasattr(entry, "df")
        assert list(entry.df.columns) == ["t", "E", "j"]
        assert len(entry.df) == 3

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
    def test_fetch_entries_all(self, csv_bytes):
        """fetch_entries returns multiple Entry objects."""
        client = _make_client()

        dict1 = _make_entity_dict(exp_id=1, title="Item_1")
        dict2 = _make_entity_dict(exp_id=2, title="Item_2")
        client.items_client.read_items.return_value = _make_raw_response(
            [dict1, dict2]
        )

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
        foreign_dict = _make_entity_dict(exp_id=2, title="Foreign", metadata={"other": {}})
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

        assert isinstance(entries, list)
        assert len(entries) >= 1


# ===================================================================
# Test: upload_entry
# ===================================================================


@pytest.mark.elabftw
class TestUploadEntry:
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
        patch_kwargs = client.items_client.patch_item.call_args
        body = patch_kwargs.kwargs.get("body") or patch_kwargs[1].get("body", {})
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

    def test_upload_entry_stores_unitpackage_metadata(self, sample_entry):
        """upload_entry stores the datapackage descriptor under the 'unitpackage' key."""
        client = _make_client()

        client.items_client.post_item_with_http_info.return_value = (
            None,
            201,
            {"Location": "/api/v2/items/102"},
        )

        client.upload_entry(sample_entry)

        patch_kwargs = client.items_client.patch_item.call_args
        body = patch_kwargs.kwargs.get("body") or patch_kwargs[1].get("body", {})
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


# ===================================================================
# Test: round-trip upload → fetch
# ===================================================================


@pytest.mark.elabftw
class TestRoundTrip:
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
        patch_kwargs = client.items_client.patch_item.call_args
        body = patch_kwargs.kwargs.get("body") or patch_kwargs[1].get("body", {})
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

        # Assert field units are faithfully preserved
        field_dict = make_field_dict(result)
        assert field_dict["t"].get("unit") == "s"
        assert field_dict["E"].get("unit") == "V"
        assert field_dict["j"].get("unit") == "A / m2"

        # Assert column names are preserved
        assert list(result.df.columns) == ["t", "E", "j"]


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
        field_dict = make_field_dict(entry)
        assert field_dict["t"].get("unit") == "s"
        assert field_dict["E"].get("unit") == "V"
        assert field_dict["j"].get("unit") == "A / m2"

    def test_fetch_entry_restores_metadata_from_fixture(self, fixture_version):
        """fetch_entry restores metadata stored in the datapackage descriptor."""
        client, entity_id = self._wire_client(fixture_version)
        entry = client.fetch_entry(entity_id)
        custom = entry.resource.custom
        metadata = custom.get("metadata", {})
        assert "echemdb" in metadata
