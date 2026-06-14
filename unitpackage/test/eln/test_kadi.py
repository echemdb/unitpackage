"""
Comprehensive tests for unitpackage.kadi -- the Kadi4Mat integration module.

Every Kadi4Mat API call is mocked; no live server is needed.
Run with:  pytest -m kadi
"""

# pylint: disable=redefined-outer-name,protected-access,too-few-public-methods

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
    make_mock_kadi_record,
)

# ---------------------------------------------------------------------------
# Fixture loader (recorded real API responses)
# ---------------------------------------------------------------------------


_BACKEND = "kadi"
_KADI_VERSIONS = get_versions(_BACKEND)

# ---------------------------------------------------------------------------
# Constants / mock data shared across tests
# ---------------------------------------------------------------------------

_KADI_CSV_NAME = "test_entry.csv"


def _make_mock_record(
    record_id=42,
    title="CV measurement on Pt(111)",
    identifier="cv_measurement_pt111",
):
    """Return a self-contained Mock mimicking a Kadi4Mat record with a unitpackage descriptor."""
    from unitpackage.eln.kadi import _dict_to_kadi_extras

    # Kadi4Mat stores the descriptor as a typed ``extras`` tree under the
    # ``"unitpackage"`` key.
    extras = _dict_to_kadi_extras(SAMPLE_DESCRIPTOR, key="unitpackage")

    rec = Mock()
    rec.id = record_id
    rec.title = title
    rec.identifier = identifier
    rec.meta = {
        "id": record_id,
        "title": title,
        "identifier": identifier,
        "extras": [extras],
    }

    filelist_mock = Mock()
    filelist_mock.json.return_value = {
        "items": [_make_mock_file_entry("csv-id", _KADI_CSV_NAME)]
    }
    rec.get_filelist.return_value = filelist_mock

    def _download(**kwargs):
        with open(kwargs["file_path"], "wb") as fh:
            fh.write(CSV_DATA)

    rec.download_file = _download
    return rec


def _make_mock_file_entry(file_id="abc-123", name="test_entry.csv"):
    """Return a dict that looks like a Kadi4Mat file list entry."""
    return {"id": file_id, "name": name}


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture()
def mock_record():
    """Mock Kadi4Mat record, populated from fixtures when available."""
    if _KADI_VERSIONS:
        return make_mock_kadi_record(_KADI_VERSIONS[-1], CSV_DATA)
    return _make_mock_record()


@pytest.fixture(params=_KADI_VERSIONS if _KADI_VERSIONS else [None])
def fixture_version(request):
    """Pytest fixture: parameterised over each recorded Kadi version."""
    version = request.param
    if version is None:
        pytest.skip("No kadi fixtures recorded")
    return version


# ---------------------------------------------------------------------------
# Helpers -- build a minimal KadiClient without hitting the real API
# ---------------------------------------------------------------------------


def _make_client():
    """
    Instantiate a KadiClient with the KadiManager replaced by a Mock.

    The fake kadi_apy module is already injected into sys.modules
    by conftest.py, so we can import directly.
    """
    from unitpackage.eln.kadi import KadiClient

    client = KadiClient.__new__(KadiClient)
    client._manager = MagicMock()
    client._host = "https://kadi.example.org"
    return client


# ===================================================================
# Test: initialisation
# ===================================================================


@pytest.mark.kadi
class TestClientInit:
    """Tests for KadiClient.__init__ and from_env."""

    def test_client_init(self):
        """KadiManager is created with the supplied host, pat, and verify=True by default."""
        from unitpackage.eln.kadi import KadiClient

        with patch("unitpackage.eln.kadi.KadiManager") as mock_manager_cls:
            KadiClient(
                host="https://kadi.example.edu",
                pat="test-pat-123",
            )
            mock_manager_cls.assert_called_once()
            kwargs = mock_manager_cls.call_args.kwargs
            assert kwargs["host"] == "https://kadi.example.edu"
            assert kwargs["pat"] == "test-pat-123"
            assert kwargs["verify"] is True

    def test_client_init_forwards_empty_base_path(self):
        """base_path is always forwarded (defaulting to "") so KadiManager
        never falls back to dereferencing its unloaded (None) config."""
        from unitpackage.eln.kadi import KadiClient

        with patch("unitpackage.eln.kadi.KadiManager") as mock_manager_cls:
            KadiClient(host="https://kadi.example.edu", pat="test-pat-123")
            assert mock_manager_cls.call_args.kwargs["base_path"] == ""

    def test_client_init_forwards_explicit_base_path(self):
        """An explicit base_path (subpath instance) is forwarded as given."""
        from unitpackage.eln.kadi import KadiClient

        with patch("unitpackage.eln.kadi.KadiManager") as mock_manager_cls:
            KadiClient(
                host="https://kadi.example.edu",
                pat="test-pat-123",
                base_path="kadi",
            )
            assert mock_manager_cls.call_args.kwargs["base_path"] == "kadi"

    def test_client_init_no_verify_ssl(self):
        """KadiManager is created with verify=False when verify_ssl=False."""
        from unitpackage.eln.kadi import KadiClient

        with patch("unitpackage.eln.kadi.KadiManager") as mock_manager_cls:
            KadiClient(
                host="https://kadi.example.edu",
                pat="test-pat-123",
                verify_ssl=False,
            )
            mock_manager_cls.assert_called_once()
            kwargs = mock_manager_cls.call_args.kwargs
            assert kwargs["host"] == "https://kadi.example.edu"
            assert kwargs["pat"] == "test-pat-123"
            assert kwargs["verify"] is False

    def test_client_from_env(self):
        """from_env reads KADI_HOST and KADI_PAT from the environment."""
        from unitpackage.eln.kadi import KadiClient

        env = {
            "KADI_HOST": "https://env-kadi.example.edu",
            "KADI_PAT": "env-pat-456",
        }
        with (
            patch("unitpackage.eln.kadi.KadiManager"),
            patch.dict("os.environ", env, clear=False),
        ):
            assert KadiClient.from_env() is not None

    def test_client_from_env_missing_vars(self):
        """from_env raises when the required env vars are absent."""
        from unitpackage.eln.kadi import KadiClient

        with patch.dict("os.environ", {}, clear=True):
            with pytest.raises((KeyError, ValueError, EnvironmentError)):
                KadiClient.from_env()


# ===================================================================
# Test: info
# ===================================================================


@pytest.mark.kadi
class TestInfo:
    """Tests for KadiClient.info()."""

    def test_info(self):
        """info() makes a request and returns a dict."""
        client = _make_client()

        mock_response = Mock()
        mock_response.json.return_value = {"version": "1.8.0"}
        client._manager.make_request.return_value = mock_response

        result = client.info()

        assert isinstance(result, dict)
        assert result["version"] == "1.8.0"


# ===================================================================
# Test: fetch_entry
# ===================================================================


@pytest.mark.kadi
class TestFetchEntry:
    """Tests for KadiClient.fetch_entry()."""

    def test_fetch_entry(self, mock_record):
        """fetch_entry downloads a record's CSV and returns a valid Entry."""
        client = _make_client()
        client._manager.record.return_value = mock_record

        entry = client.fetch_entry(42)

        client._manager.record.assert_called_once_with(id=42)
        assert_basic_entry(entry)

    def test_fetch_entry_no_csv(self, mock_record):
        """fetch_entry raises ValueError when no CSV file exists."""
        client = _make_client()

        client._manager.record.return_value = mock_record

        filelist_response = Mock()
        filelist_response.json.return_value = {
            "items": [_make_mock_file_entry("img-id", "image.png")]
        }
        mock_record.get_filelist.return_value = filelist_response

        with pytest.raises(ValueError, match="(?i)csv"):
            client.fetch_entry(42)

    def test_fetch_entry_metadata_mapping(self):
        """Metadata stored in the unitpackage descriptor is restored on fetch."""
        client = _make_client()
        mock_rec = _make_mock_record()
        client._manager.record.return_value = mock_rec

        entry = client.fetch_entry(42)

        metadata = entry.resource.custom.get("metadata", {})
        assert metadata is not None
        assert "echemdb" in metadata


# ===================================================================
# Test: fetch_entries
# ===================================================================


@pytest.mark.kadi
class TestFetchEntries:
    """Tests for KadiClient.fetch_entries()."""

    def test_fetch_entries_all(self):
        """fetch_entries returns multiple Entry objects."""
        client = _make_client()

        search_response = Mock()
        search_response.json.return_value = {
            "items": [
                {"id": 1, "title": "Record 1"},
                {"id": 2, "title": "Record 2"},
            ]
        }
        client._manager.search.search_resources.return_value = search_response

        with patch.object(client, "fetch_entry") as mock_fetch:
            mock_fetch.side_effect = [
                Mock(spec=["df", "identifier"]),
                Mock(spec=["df", "identifier"]),
            ]

            entries = client.fetch_entries()

            assert len(entries) == 2
            assert mock_fetch.call_count == 2

    def test_fetch_entries_with_tags(self):
        """fetch_entries passes tags to the search API."""
        client = _make_client()

        search_response = Mock()
        search_response.json.return_value = {"items": [{"id": 1, "title": "E1"}]}
        client._manager.search.search_resources.return_value = search_response

        with patch.object(client, "fetch_entry") as mock_fetch:
            mock_fetch.return_value = Mock(spec=["df", "identifier"])
            entries = client.fetch_entries(tags=["electrochemistry"])

            client._manager.search.search_resources.assert_called_once_with(
                "record", page=1, per_page=100, tags=["electrochemistry"]
            )
            assert len(entries) == 1

    def test_fetch_entries_skips_non_unitpackage(self):
        """fetch_entries skips records lacking a 'unitpackage' metadatum.

        Exercises the real fetch_entry rejection together with the
        _collect_entries skip path (no fetch_entry mock).
        """
        client = _make_client()

        search_response = Mock()
        search_response.json.return_value = {
            "items": [{"id": 7, "title": "Foreign record"}]
        }
        client._manager.search.search_resources.return_value = search_response

        # A record without the unitpackage metadatum -> fetch_entry raises
        # ValueError -> the record is skipped rather than aborting the export.
        foreign = Mock()
        foreign.meta = {"id": 7, "title": "Foreign record", "extras": []}
        client._manager.record.return_value = foreign

        entries = client.fetch_entries()
        assert len(entries) == 0

    def test_fetch_entries_walks_all_pages(self):
        """fetch_entries follows pagination beyond the first page."""
        client = _make_client()

        page1 = Mock()
        page1.json.return_value = {
            "items": [{"id": 1, "title": "R1"}, {"id": 2, "title": "R2"}],
            "_pagination": {"total_pages": 2},
        }
        page2 = Mock()
        page2.json.return_value = {
            "items": [{"id": 3, "title": "R3"}],
            "_pagination": {"total_pages": 2},
        }
        client._manager.search.search_resources.side_effect = [page1, page2]

        with patch.object(client, "fetch_entry") as mock_fetch:
            mock_fetch.side_effect = [Mock(spec=["df", "identifier"]) for _ in range(3)]

            entries = client.fetch_entries()

            assert len(entries) == 3
            assert client._manager.search.search_resources.call_count == 2
            second_call = client._manager.search.search_resources.call_args_list[1]
            assert second_call.kwargs["page"] == 2


# ===================================================================
# Test: upload_entry
# ===================================================================


@pytest.mark.kadi
class TestUploadEntry:
    """Tests for KadiClient.upload_entry()."""

    def test_upload_entry(self, sample_entry):
        """upload_entry creates a record, uploads the CSV, and stores the datapackage descriptor."""
        client = _make_client()

        mock_record = Mock()
        mock_record.meta = {"id": 100}
        client._manager.record.return_value = mock_record

        result = client.upload_entry(sample_entry)

        client._manager.record.assert_called_once()
        mock_record.upload_file.assert_called_once()
        assert result == 100

        mock_record.add_metadatum.assert_called_once()
        call_kwargs = mock_record.add_metadatum.call_args.kwargs["metadatum"]
        assert call_kwargs["key"] == "unitpackage"
        assert call_kwargs["type"] == "dict"
        from unitpackage.eln.kadi import _kadi_extras_to_python

        descriptor = _kadi_extras_to_python(call_kwargs)
        assert "resources" in descriptor

    def test_upload_entry_custom_title(self, sample_entry):
        """A custom title is used for the record."""
        client = _make_client()

        mock_record = Mock()
        mock_record.meta = {"id": 101}
        client._manager.record.return_value = mock_record

        client.upload_entry(sample_entry, title="My Custom Title")

        call_kwargs = client._manager.record.call_args
        assert call_kwargs.kwargs.get("title") == "My Custom Title"

    def test_upload_entry_with_tags(self, sample_entry):
        """Tags are added to the record after creation."""
        client = _make_client()

        mock_record = Mock()
        mock_record.meta = {"id": 102}
        client._manager.record.return_value = mock_record

        client.upload_entry(sample_entry, tags=["test", "cv"])

        assert mock_record.add_tag.call_count == 2

    def test_upload_entry_rolls_back_on_failure(self, sample_entry):
        """A failure after record creation deletes the orphaned record."""
        client = _make_client()

        mock_record = Mock()
        mock_record.meta = {"id": 103}
        mock_record.created = True
        mock_record.add_metadatum.side_effect = RuntimeError("boom")
        client._manager.record.return_value = mock_record

        with pytest.raises(RuntimeError, match="boom"):
            client.upload_entry(sample_entry)

        mock_record.delete.assert_called_once()

    def test_upload_entry_refuses_existing_record(self, sample_entry):
        """An identifier collision is refused without touching the record."""
        client = _make_client()

        mock_record = Mock()
        mock_record.meta = {"id": 104}
        # kadi-apy returns an existing record (created is False) on collision.
        mock_record.created = False
        client._manager.record.return_value = mock_record

        with pytest.raises(ValueError, match="already"):
            client.upload_entry(sample_entry)

        mock_record.upload_file.assert_not_called()
        mock_record.add_metadatum.assert_not_called()
        mock_record.delete.assert_not_called()


# ===================================================================
# Test: descriptor helpers and fetch with unitpackage descriptor
# ===================================================================


@pytest.mark.kadi
class TestDescriptor:
    """Tests for descriptor helpers and fetch with unitpackage descriptor."""

    def test_build_datapackage_descriptor(self, sample_entry):
        """build_datapackage_descriptor produces a frictionless package dict with schema."""
        from unitpackage.eln import build_datapackage_descriptor

        descriptor = build_datapackage_descriptor(sample_entry)

        assert isinstance(descriptor, dict)
        assert "resources" in descriptor
        schema_fields = descriptor["resources"][0].get("schema", {}).get("fields", [])
        field_units = {f["name"]: f.get("unit") for f in schema_fields}
        assert field_units.get("t") == "s"
        assert field_units.get("E") == "V"

    def test_fetch_entry_with_unitpackage_descriptor(self, mock_record, sample_entry):
        """fetch_entry restores schema and metadata from a stored unitpackage descriptor."""
        from unitpackage.eln import build_datapackage_descriptor

        client = _make_client()

        descriptor = build_datapackage_descriptor(sample_entry)
        datapackage_json = json.dumps(descriptor)

        mock_record.meta = {
            "id": 42,
            "title": mock_record.title,
            "extras": [
                {"key": "unitpackage", "value": datapackage_json, "type": "str"},
            ],
        }
        client._manager.record.return_value = mock_record

        filelist_response = Mock()
        filelist_response.json.return_value = {
            "items": [_make_mock_file_entry("csv-id", "test_entry.csv")]
        }
        mock_record.get_filelist.return_value = filelist_response

        def mock_download(file_id, file_path):  # pylint: disable=unused-argument
            with open(file_path, "wb") as f:
                f.write(CSV_DATA)

        mock_record.download_file = mock_download

        entry = client.fetch_entry(42)
        assert_field_units(entry)

    def test_fetch_entry_no_unitpackage_descriptor_raises(self, mock_record):
        """fetch_entry raises ValueError for records without a unitpackage metadatum."""
        client = _make_client()

        mock_record.meta = {"id": 42, "title": mock_record.title, "extras": []}
        client._manager.record.return_value = mock_record

        with pytest.raises(ValueError, match="unitpackage"):
            client.fetch_entry(42)


# ===================================================================
# Test: round-trip upload -> fetch
# ===================================================================


@pytest.mark.kadi
class TestRoundTrip:
    """Tests for upload → fetch round-trip."""

    def test_upload_then_fetch_preserves_entry(self, sample_entry):
        """Full round-trip: upload_entry stores descriptor; fetch_entry restores it."""
        client = _make_client()

        mock_record = Mock()
        mock_record.meta = {"id": 42}
        client._manager.record.return_value = mock_record

        client.upload_entry(sample_entry, title="Test Round-Trip")

        stored_extras = mock_record.add_metadatum.call_args.kwargs["metadatum"]

        mock_record.meta = {
            "id": 42,
            "title": "Test Round-Trip",
            "extras": [stored_extras],
        }

        filelist_response = Mock()
        filelist_response.json.return_value = {
            "items": [_make_mock_file_entry("csv-id", "test_entry.csv")]
        }
        mock_record.get_filelist.return_value = filelist_response

        def mock_download(file_id, file_path):  # pylint: disable=unused-argument
            with open(file_path, "wb") as f:
                f.write(CSV_DATA)

        mock_record.download_file = mock_download

        result = client.fetch_entry(42)
        assert_field_units(result)
        assert list(result.df.columns) == SAMPLE_COLUMNS


# ===================================================================
# Test: fixture-based tests (recorded real API responses)
# ===================================================================


@pytest.mark.kadi
class TestFixtureVersions:
    """Tests that replay recorded real Kadi4Mat API responses."""

    def _wire_client(self, version):
        """Return (client, record) with mocks populated from fixture data."""
        client = _make_client()
        csv_data = get_csv_bytes(_BACKEND, version)
        record = make_mock_kadi_record(version, csv_data)
        client._manager.record.return_value = record
        return client, record

    def test_fetch_entry_from_fixture(self, fixture_version):
        """fetch_entry returns a valid Entry from a real recorded fixture."""
        client, record = self._wire_client(fixture_version)
        entry = client.fetch_entry(record.id)
        assert entry is not None
        assert hasattr(entry, "df")
        assert len(entry.df) > 0

    def test_fetch_entry_columns_from_fixture(self, fixture_version):
        """fetch_entry returns an Entry with the expected column names."""
        client, record = self._wire_client(fixture_version)
        entry = client.fetch_entry(record.id)
        assert "t" in entry.df.columns
        assert "E" in entry.df.columns

    def test_fetch_entry_restores_units_from_fixture(self, fixture_version):
        """fetch_entry restores field units from the stored datapackage descriptor."""
        client, record = self._wire_client(fixture_version)
        entry = client.fetch_entry(record.id)
        assert_field_units(entry)

    def test_fetch_entry_restores_metadata_from_fixture(self, fixture_version):
        """fetch_entry restores metadata stored in the datapackage descriptor."""
        client, record = self._wire_client(fixture_version)
        entry = client.fetch_entry(record.id)
        metadata = entry.resource.custom.get("metadata", {})
        assert "echemdb" in metadata

    def test_info_from_fixture(self, fixture_version):
        """info() returns data matching the recorded fixture."""
        client = _make_client()
        info_data = load_fixture(_BACKEND, fixture_version, "info")["response"]

        mock_response = Mock()
        mock_response.json.return_value = info_data
        client._manager.make_request.return_value = mock_response

        result = client.info()
        assert isinstance(result, dict)
        assert "version" in result

    def test_upload_entry_from_fixture(self, fixture_version, sample_entry):
        """upload_entry succeeds with real recorded response shapes."""
        client = _make_client()
        create_data = load_fixture(
            _BACKEND, fixture_version, "create_record"
        )["response"]

        mock_record = Mock()
        mock_record.meta = create_data
        mock_record.created = True
        client._manager.record.return_value = mock_record

        result = client.upload_entry(sample_entry)
        assert result == create_data["id"]

    def test_fetch_entries_from_fixture(self, fixture_version):
        """fetch_entries returns entries using recorded fixture data."""
        client, record = self._wire_client(fixture_version)

        list_data = load_fixture(
            _BACKEND, fixture_version, "list_list_entities"
        )["response"]

        search_response = Mock()
        search_response.json.return_value = list_data
        client._manager.search.search_resources.return_value = search_response

        entries = client.fetch_entries()
        assert len(entries) >= 1
        assert_basic_entry(entries[0])
        assert_field_units(entries[0])

    def test_fetch_entry_csv_values_from_fixture(self, fixture_version):
        """Fetched DataFrame values match the recorded CSV byte-for-byte."""
        client, record = self._wire_client(fixture_version)
        entry = client.fetch_entry(record.id)

        csv_data = get_csv_bytes(_BACKEND, fixture_version)
        expected_df = pd.read_csv(io.BytesIO(csv_data))
        pd.testing.assert_frame_equal(entry.df, expected_df)

    def test_fetch_entry_matches_manifest(self, fixture_version):
        """Fetched entry columns and units match the manifest test_data."""
        client, record = self._wire_client(fixture_version)
        entry = client.fetch_entry(record.id)

        manifest = load_manifest(_BACKEND, fixture_version)
        test_data = manifest["test_data"]
        assert list(entry.df.columns) == test_data["csv_columns"]

        field_dict = make_field_dict(entry)
        for name, unit in test_data["field_units"].items():
            assert field_dict[name].get("unit") == unit

    def test_fetch_entry_identifier_from_fixture(self, fixture_version):
        """Entry identifier matches the descriptor resource name."""
        from unitpackage.eln.kadi import _kadi_extras_to_python

        client, record = self._wire_client(fixture_version)
        entry = client.fetch_entry(record.id)

        entity_data = load_fixture(_BACKEND, fixture_version, "get_entity")["response"]
        extras = entity_data.get("extras", [])
        up_extra = next(e for e in extras if e.get("key") == "unitpackage")
        if up_extra.get("type") == "dict":
            descriptor = _kadi_extras_to_python(up_extra)
        else:
            descriptor = json.loads(up_extra.get("value", "{}"))
        expected_name = descriptor["resources"][0]["name"]
        assert entry.identifier == expected_name

    def test_info_version_from_fixture(self, fixture_version):
        """Info response version matches the fixture directory name."""
        client = _make_client()
        info_data = load_fixture(_BACKEND, fixture_version, "info")["response"]

        mock_response = Mock()
        mock_response.json.return_value = info_data
        client._manager.make_request.return_value = mock_response

        result = client.info()
        assert result.get("version") == fixture_version

    def test_fetch_entry_metadata_values_from_fixture(self, fixture_version):
        """Metadata citationKey is preserved through the round-trip."""
        client, record = self._wire_client(fixture_version)
        entry = client.fetch_entry(record.id)

        metadata = entry.resource.custom.get("metadata", {})
        source = metadata.get("echemdb", {}).get("source", {})
        assert "citationKey" in source
        assert isinstance(source["citationKey"], str)
        assert len(source["citationKey"]) > 0

    def test_fixture_consistency(self, fixture_version):
        """get_entity.json and list_get_entity.json describe the same entity."""
        single = load_fixture(_BACKEND, fixture_version, "get_entity")["response"]
        list_ver = load_fixture(
            _BACKEND, fixture_version, "list_get_entity"
        )["response"]
        assert single["id"] == list_ver["id"]
        assert single["title"] == list_ver["title"]
        assert single["identifier"] == list_ver["identifier"]
