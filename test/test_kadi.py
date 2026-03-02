"""
Comprehensive tests for unitpackage.kadi -- the Kadi4Mat integration module.

Every Kadi4Mat API call is mocked; no live server is needed.
Run with:  pytest -m kadi
"""

import json
import sys
from pathlib import Path
from unittest.mock import MagicMock, Mock, patch

import pandas as pd
import pytest

from unitpackage.eln import build_datapackage_descriptor

# ---------------------------------------------------------------------------
# Fixture loader (recorded real API responses)
# ---------------------------------------------------------------------------

sys.path.insert(0, str(Path(__file__).parent))
from fixture_loader import get_versions, load_fixture, make_field_dict, make_mock_kadi_record  # noqa: E402

_BACKEND = "kadi"
_KADI_VERSIONS = get_versions(_BACKEND)

# ---------------------------------------------------------------------------
# Constants / mock data shared across tests
# ---------------------------------------------------------------------------

CSV_DATA = b"t,E,j\n0.0,-0.103,43.01\n0.01,-0.102,51.41\n0.02,-0.101,42.89\n"

SAMPLE_CONFIG = {
    "kadi": {
        "production": {
            "host": "https://kadi.example.edu",
            "pat": "test-pat-123",
        },
        "staging": {
            "host": "https://staging-kadi.example.edu",
            "pat": "staging-pat-456",
        },
    },
}


def _make_mock_record(
    record_id=42,
    title="CV measurement on Pt(111)",
    identifier="cv_measurement_pt111",
):
    """Return a Mock that looks like a Kadi4Mat record object."""
    rec = Mock()
    rec.id = record_id
    rec.title = title
    rec.identifier = identifier
    rec.meta = {
        "id": record_id,
        "title": title,
        "identifier": identifier,
        "extras": [],
    }
    return rec


def _make_mock_file_entry(file_id="abc-123", name="data.csv"):
    """Return a dict that looks like a Kadi4Mat file list entry."""
    return {"id": file_id, "name": name}


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture()
def mock_record():
    if _KADI_VERSIONS:
        return make_mock_kadi_record(_KADI_VERSIONS[-1], CSV_DATA)
    return _make_mock_record()


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
    return entry


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
            mock_manager_cls.assert_called_once_with(
                host="https://kadi.example.edu", pat="test-pat-123", verify=True
            )

    def test_client_init_no_verify_ssl(self):
        """KadiManager is created with verify=False when verify_ssl=False."""
        from unitpackage.eln.kadi import KadiClient

        with patch("unitpackage.eln.kadi.KadiManager") as mock_manager_cls:
            KadiClient(
                host="https://kadi.example.edu",
                pat="test-pat-123",
                verify_ssl=False,
            )
            mock_manager_cls.assert_called_once_with(
                host="https://kadi.example.edu", pat="test-pat-123", verify=False
            )

    def test_client_from_env(self):
        """from_env reads KADI_HOST and KADI_PAT from the environment."""
        from unitpackage.eln.kadi import KadiClient

        env = {
            "KADI_HOST": "https://env-kadi.example.edu",
            "KADI_PAT": "env-pat-456",
        }
        with patch("unitpackage.eln.kadi.KadiManager"), patch.dict(
            "os.environ", env, clear=False
        ):
            assert KadiClient.from_env() is not None

    def test_client_from_env_missing_vars(self):
        """from_env raises when the required env vars are absent."""
        from unitpackage.eln.kadi import KadiClient

        with patch.dict("os.environ", {}, clear=True):
            with pytest.raises((KeyError, ValueError, EnvironmentError)):
                KadiClient.from_env()

    def test_client_from_config(self):
        """from_config loads credentials from config file profile."""
        from unitpackage.eln.kadi import KadiClient

        with patch("unitpackage.eln.kadi.KadiManager"), patch(
            "unitpackage.config.load_config", return_value=SAMPLE_CONFIG
        ):
            assert KadiClient.from_config("production") is not None

    def test_client_from_config_missing(self):
        """from_config raises ValueError for missing profile."""
        from unitpackage.eln.kadi import KadiClient

        with patch("unitpackage.config.load_config", return_value={}):
            with pytest.raises(ValueError, match="No Kadi profiles found"):
                KadiClient.from_config()


# ===================================================================
# Test: info
# ===================================================================


@pytest.mark.kadi
class TestInfo:
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
    def test_fetch_entry(self, mock_record):
        """fetch_entry downloads a record's CSV and returns a valid Entry."""
        client = _make_client()

        client._manager.record.return_value = mock_record

        filelist_response = Mock()
        filelist_response.json.return_value = {
            "items": [_make_mock_file_entry("csv-id", "data.csv")]
        }
        mock_record.get_filelist.return_value = filelist_response

        def mock_download(file_id, file_path):
            with open(file_path, "wb") as f:
                f.write(CSV_DATA)

        mock_record.download_file = mock_download

        entry = client.fetch_entry(42)

        client._manager.record.assert_called_once_with(id=42)
        assert entry is not None
        assert hasattr(entry, "df")
        assert list(entry.df.columns) == ["t", "E", "j"]
        assert len(entry.df) == 3

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

    def test_fetch_entry_metadata_mapping(self, mock_record):
        """Kadi metadata is mapped to entry metadata."""
        client = _make_client()

        mock_record.meta = {
            "id": 42,
            "title": mock_record.title,
            "extras": [{"key": "temperature", "value": "298.15", "type": "str"}],
        }
        client._manager.record.return_value = mock_record

        filelist_response = Mock()
        filelist_response.json.return_value = {
            "items": [_make_mock_file_entry("csv-id", "data.csv")]
        }
        mock_record.get_filelist.return_value = filelist_response

        def mock_download(file_id, file_path):
            with open(file_path, "wb") as f:
                f.write(CSV_DATA)

        mock_record.download_file = mock_download

        entry = client.fetch_entry(42)

        metadata = entry.resource.custom.get("metadata", {})
        assert metadata is not None
        assert "42" in json.dumps(metadata)  # kadi_id


# ===================================================================
# Test: fetch_entries
# ===================================================================


@pytest.mark.kadi
class TestFetchEntries:
    def test_fetch_entries(self):
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
                "record", tags=["electrochemistry"]
            )
            assert len(entries) == 1

    def test_fetch_entries_skips_no_csv(self):
        """fetch_entries skips records without CSV files."""
        client = _make_client()

        search_response = Mock()
        search_response.json.return_value = {
            "items": [{"id": 1, "title": "No CSV record"}]
        }
        client._manager.search.search_resources.return_value = search_response

        with patch.object(
            client, "fetch_entry", side_effect=ValueError("No CSV file")
        ):
            entries = client.fetch_entries()
            assert len(entries) == 0


# ===================================================================
# Test: upload_entry
# ===================================================================


@pytest.mark.kadi
class TestUploadEntry:
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


# ===================================================================
# Test: descriptor helpers and fetch with unitpackage descriptor
# ===================================================================


@pytest.mark.kadi
class TestDescriptor:
    def test_build_datapackage_descriptor(self, sample_entry):
        """build_datapackage_descriptor produces a frictionless package dict with schema."""
        descriptor = build_datapackage_descriptor(sample_entry)

        assert isinstance(descriptor, dict)
        assert "resources" in descriptor
        schema_fields = descriptor["resources"][0].get("schema", {}).get("fields", [])
        field_units = {f["name"]: f.get("unit") for f in schema_fields}
        assert field_units.get("t") == "s"
        assert field_units.get("E") == "V"

    def test_fetch_entry_with_unitpackage_descriptor(self, mock_record, sample_entry):
        """fetch_entry restores schema and metadata from a stored unitpackage descriptor."""
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
            "items": [_make_mock_file_entry("csv-id", "data.csv")]
        }
        mock_record.get_filelist.return_value = filelist_response

        def mock_download(file_id, file_path):
            with open(file_path, "wb") as f:
                f.write(CSV_DATA)

        mock_record.download_file = mock_download

        entry = client.fetch_entry(42)
        field_dict = make_field_dict(entry)
        assert field_dict["t"].get("unit") == "s"
        assert field_dict["E"].get("unit") == "V"

    def test_fetch_entry_no_unitpackage_descriptor_raises(self, mock_record):
        """fetch_entry raises ValueError for records without a unitpackage metadatum."""
        client = _make_client()

        mock_record.meta = {"id": 42, "title": mock_record.title, "extras": []}
        client._manager.record.return_value = mock_record

        with pytest.raises(ValueError, match="unitpackage"):
            client.fetch_entry(42)


# ===================================================================
# Test: CLI integration
# ===================================================================


@pytest.mark.kadi
class TestCLIIntegration:
    def test_profile_option_in_help(self):
        """--profile appears in kadi --help output."""
        from click.testing import CliRunner

        from unitpackage.entrypoint import cli

        result = CliRunner().invoke(cli, ["kadi", "--help"])
        assert "--profile" in result.output

    def test_cli_options_override_config(self):
        """CLI --host and --pat take precedence over config."""
        from click.testing import CliRunner

        from unitpackage.entrypoint import cli

        with patch("unitpackage.eln.kadi.KadiManager"):
            result = CliRunner().invoke(
                cli,
                [
                    "kadi",
                    "--host", "https://cli.example.edu",
                    "--pat", "cli-pat",
                    "info",
                ],
            )
            assert "Missing" not in result.output

    def test_cli_no_credentials_error(self):
        """No credentials at all gives a helpful error message."""
        from click.testing import CliRunner

        from unitpackage.entrypoint import cli

        with patch("unitpackage.config.load_config", return_value={}):
            result = CliRunner().invoke(cli, ["kadi", "info"])
            assert result.exit_code != 0
            assert "Missing" in result.output or "credentials" in result.output


# ===================================================================
# Test: round-trip upload -> fetch
# ===================================================================


@pytest.mark.kadi
class TestRoundTrip:
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
            "items": [_make_mock_file_entry("csv-id", "data.csv")]
        }
        mock_record.get_filelist.return_value = filelist_response

        def mock_download(file_id, file_path):
            with open(file_path, "wb") as f:
                f.write(CSV_DATA)

        mock_record.download_file = mock_download

        result = client.fetch_entry(42)
        field_dict = make_field_dict(result)
        assert field_dict["t"].get("unit") == "s"
        assert field_dict["E"].get("unit") == "V"
        assert field_dict["j"].get("unit") == "A / m2"
        assert list(result.df.columns) == ["t", "E", "j"]


# ===================================================================
# Test: fixture-based tests (recorded real API responses)
# ===================================================================


@pytest.mark.kadi
class TestFixtureVersions:
    """Tests that replay recorded real Kadi4Mat API responses."""

    def _wire_client(self, version):
        """Return (client, record) with mocks populated from fixture data."""
        client = _make_client()
        record = make_mock_kadi_record(version, CSV_DATA)
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
        field_dict = make_field_dict(entry)
        assert field_dict["t"].get("unit") == "s"
        assert field_dict["E"].get("unit") == "V"
        assert field_dict["j"].get("unit") == "A / m2"

    def test_fetch_entry_restores_metadata_from_fixture(self, fixture_version):
        """fetch_entry restores metadata stored in the datapackage descriptor."""
        client, record = self._wire_client(fixture_version)
        entry = client.fetch_entry(record.id)
        metadata = entry.resource.custom.get("metadata", {})
        assert "echemdb" in metadata
