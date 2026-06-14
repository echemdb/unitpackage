"""
Tests for the shared ELN CLI commands (fetch / export / upload).

Both backend command groups are built by the same factory
(:func:`unitpackage.eln._cli.make_eln_group`), so these tests are parameterised
over both backends. The backend client class is patched, so no real API or
optional dependency is needed.
"""

# pylint: disable=redefined-outer-name

import importlib
from unittest.mock import Mock, patch

import pytest
from click.testing import CliRunner

# Each backend: how to load its group, which client class to patch, the
# credential flags, and the nouns / display name used in command output.
_BACKENDS = [
    pytest.param(
        {
            "group": ("unitpackage.eln.elabftw_cli", "elabftw"),
            "client_path": "unitpackage.eln.elabftw.ElabFTWClient",
            "creds": ["--host", "https://e.example", "--api-key", "k"],
            "singular": "entry",
            "plural": "entries",
            "display": "eLabFTW",
            # SDK module patched so client construction needs no real server.
            "sdk_patch": "unitpackage.eln.elabftw.elabapi_python",
            "profile_creds": {
                "host": "https://e.example",
                "api_key": "k",
                "verify_ssl": True,
            },
        },
        marks=pytest.mark.elabftw,
        id="elabftw",
    ),
    pytest.param(
        {
            "group": ("unitpackage.eln.kadi_cli", "kadi"),
            "client_path": "unitpackage.eln.kadi.KadiClient",
            "creds": ["--host", "https://k.example", "--pat", "k"],
            "singular": "record",
            "plural": "records",
            "display": "Kadi4Mat",
            "sdk_patch": "unitpackage.eln.kadi.KadiManager",
            "profile_creds": {
                "host": "https://k.example",
                "pat": "k",
                "verify_ssl": True,
            },
        },
        marks=pytest.mark.kadi,
        id="kadi",
    ),
]


@pytest.fixture(params=_BACKENDS)
def backend(request):
    """Backend descriptor with the group object resolved."""
    spec = dict(request.param)
    module_name, attr = spec["group"]
    spec["group_obj"] = getattr(importlib.import_module(module_name), attr)
    return spec


def test_cli_fetch_saves_entry(backend, tmp_path):
    """``fetch`` downloads one entity and saves it to --outdir."""
    with patch(backend["client_path"]) as mock_client_cls:
        entry = Mock()
        mock_client_cls.return_value.fetch_entry.return_value = entry

        result = CliRunner().invoke(
            backend["group_obj"],
            [*backend["creds"], "fetch", "42", "--outdir", str(tmp_path)],
        )

    assert result.exit_code == 0, result.output
    mock_client_cls.return_value.fetch_entry.assert_called_once_with(42)
    entry.save.assert_called_once()
    assert f"Saved {backend['singular']} 42" in result.output


def test_cli_fetch_reports_failure(backend, tmp_path):
    """A fetch error is surfaced as a non-zero exit with a clear message."""
    with patch(backend["client_path"]) as mock_client_cls:
        mock_client_cls.return_value.fetch_entry.side_effect = ValueError("boom")

        result = CliRunner().invoke(
            backend["group_obj"],
            [*backend["creds"], "fetch", "42", "--outdir", str(tmp_path)],
        )

    assert result.exit_code != 0
    assert "Failed to fetch" in result.output


def test_cli_export_saves_entries(backend, tmp_path):
    """``export`` saves every fetched entry and reports the count."""
    with patch(backend["client_path"]) as mock_client_cls:
        e1, e2 = Mock(), Mock()
        mock_client_cls.return_value.fetch_entries.return_value = [e1, e2]

        result = CliRunner().invoke(
            backend["group_obj"],
            [*backend["creds"], "export", "--tag", "cv", "--outdir", str(tmp_path)],
        )

    assert result.exit_code == 0, result.output
    mock_client_cls.return_value.fetch_entries.assert_called_once_with(["cv"])
    e1.save.assert_called_once()
    e2.save.assert_called_once()
    assert f"Saved 2 {backend['plural']}" in result.output


def test_cli_export_empty(backend, tmp_path):
    """``export`` with no matches prints a friendly message, not an error."""
    with patch(backend["client_path"]) as mock_client_cls:
        mock_client_cls.return_value.fetch_entries.return_value = []

        result = CliRunner().invoke(
            backend["group_obj"],
            [*backend["creds"], "export", "--outdir", str(tmp_path)],
        )

    assert result.exit_code == 0, result.output
    assert f"No {backend['plural']} found" in result.output


def test_cli_upload(backend, tmp_path):
    """``upload`` loads a local datapackage and uploads it, echoing the new id."""
    datapackage = tmp_path / "entry.json"
    datapackage.write_text("{}")

    with (
        patch(backend["client_path"]) as mock_client_cls,
        patch("unitpackage.entry.Entry.from_local") as from_local,
    ):
        from_local.return_value = Mock()
        mock_client_cls.return_value.upload_entry.return_value = 100

        result = CliRunner().invoke(
            backend["group_obj"],
            [
                *backend["creds"],
                "upload",
                str(datapackage),
                "--title",
                "My Title",
                "--tag",
                "x",
            ],
        )

    assert result.exit_code == 0, result.output
    from_local.assert_called_once_with(str(datapackage))
    mock_client_cls.return_value.upload_entry.assert_called_once()
    call = mock_client_cls.return_value.upload_entry.call_args
    assert call.kwargs.get("title") == "My Title"
    assert call.kwargs.get("tags") == ["x"]
    assert "100" in result.output
    assert backend["display"] in result.output


def test_cli_upload_reports_failure(backend, tmp_path):
    """An upload error is surfaced as a non-zero exit with a clear message."""
    datapackage = tmp_path / "entry.json"
    datapackage.write_text("{}")

    with (
        patch(backend["client_path"]) as mock_client_cls,
        patch("unitpackage.entry.Entry.from_local") as from_local,
    ):
        from_local.return_value = Mock()
        mock_client_cls.return_value.upload_entry.side_effect = RuntimeError("nope")

        result = CliRunner().invoke(
            backend["group_obj"],
            [*backend["creds"], "upload", str(datapackage)],
        )

    assert result.exit_code != 0
    assert "Failed to upload" in result.output


# ---------------------------------------------------------------------------
# Credential resolution (CLI options > env > config profile)
#
# These were previously duplicated per backend (test_kadi.py::TestCLIIntegration
# and test_config.py::TestCLIProfileIntegration); they share the same factory
# (make_eln_group), so they live here, parameterised over both backends.
# ---------------------------------------------------------------------------


def test_cli_profile_option_in_help(backend):
    """``--profile`` appears in the group --help output."""
    result = CliRunner().invoke(backend["group_obj"], ["--help"])
    assert "--profile" in result.output


def test_cli_options_override_config(backend):
    """CLI --host and the secret flag take precedence (no config needed)."""
    with patch(backend["sdk_patch"]):
        result = CliRunner().invoke(backend["group_obj"], [*backend["creds"], "info"])
    # Got past credential resolution: no UsageError about missing credentials.
    assert "Missing" not in result.output


def test_cli_profile_loads_config(backend, tmp_path):
    """``--profile`` resolves credentials from the config file."""
    with (
        patch(backend["sdk_patch"]),
        patch("unitpackage.config.get_profile", return_value=backend["profile_creds"]),
        patch("unitpackage.config.config_path", return_value=tmp_path / "config.toml"),
    ):
        result = CliRunner().invoke(
            backend["group_obj"], ["--profile", "production", "info"]
        )
    assert "Missing" not in result.output


def test_cli_no_credentials_error(backend):
    """No credentials anywhere gives a helpful, non-zero error."""
    with patch("unitpackage.config.load_config", return_value={}):
        result = CliRunner().invoke(backend["group_obj"], ["info"])
    assert result.exit_code != 0
    assert "Missing" in result.output or "credentials" in result.output
