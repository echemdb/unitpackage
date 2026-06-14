"""
Tests for the ELN config CLI commands (add / list / show / remove / set-default).

Both backend ``config`` subgroups are built by the same factory
(:func:`unitpackage.eln._config_cli.make_config_group`), differing only in the
config-section key, display name, and the secret credential flag/field
(``--api-key`` / ``api_key`` vs ``--pat`` / ``pat``). These tests are therefore
parameterised over both backends.

Run with:  pytest test/eln/test_config_cli.py
"""

# pylint: disable=redefined-outer-name,unused-argument

from unittest.mock import patch

import pytest
from click.testing import CliRunner

from unitpackage.config import load_config, save_config
from unitpackage.entrypoint import cli

# Each backend: the config-section key, display name (used in messages), and
# the secret option flag / config field that distinguish the two CLIs.
_BACKENDS = [
    pytest.param(
        {
            "key": "elabftw",
            "display": "eLabFTW",
            "secret_opt": "--api-key",
            "secret_field": "api_key",
        },
        marks=pytest.mark.elabftw,
        id="elabftw",
    ),
    pytest.param(
        {
            "key": "kadi",
            "display": "Kadi4Mat",
            "secret_opt": "--pat",
            "secret_field": "pat",
        },
        marks=pytest.mark.kadi,
        id="kadi",
    ),
]


@pytest.fixture(params=_BACKENDS)
def backend(request):
    """Backend descriptor (key / display / secret flag+field)."""
    return request.param


@pytest.fixture()
def config_file(tmp_path):
    """Provide a temp config file and patch config_path to point to it."""
    path = tmp_path / "config.toml"
    with patch("unitpackage.config.config_path", return_value=path):
        yield path


def _prof(backend, host="x", secret="k", **extra):
    """Build a profile dict with the backend's secret field name."""
    return {"host": host, backend["secret_field"]: secret, **extra}


def _seed_config(backend, path, profiles=None, default=None):
    """Write a config file with the given profiles for *backend*."""
    section = {}
    if default:
        section["default_profile"] = default
    for name, data in (profiles or {}).items():
        section[name] = data
    save_config({backend["key"]: section}, path=path)


# ===================================================================
# Test: config add
# ===================================================================


class TestConfigAdd:
    """Tests for 'config add' CLI command."""

    def test_add_profile(self, backend, config_file):
        """Add a profile and verify it appears in the config file."""
        result = CliRunner().invoke(
            cli,
            [
                backend["key"],
                "config",
                "add",
                "production",
                "--host",
                "https://eln.example.org",
                backend["secret_opt"],
                "abc123",
            ],
        )
        assert result.exit_code == 0
        assert "production" in result.output
        cfg = load_config(config_file)
        section = cfg[backend["key"]]["production"]
        assert section["host"] == "https://eln.example.org"
        assert section[backend["secret_field"]] == "abc123"
        assert section["verify_ssl"] is True

    def test_first_profile_becomes_default(self, backend, config_file):
        """First profile added is automatically set as default."""
        CliRunner().invoke(
            cli,
            [
                backend["key"],
                "config",
                "add",
                "prod",
                "--host",
                "https://eln.example.org",
                backend["secret_opt"],
                "key",
            ],
        )
        cfg = load_config(config_file)
        assert cfg[backend["key"]]["default_profile"] == "prod"

    def test_second_profile_no_auto_default(self, backend, config_file):
        """Second profile does not change the default."""
        _seed_config(backend, config_file, {"prod": _prof(backend)}, default="prod")
        CliRunner().invoke(
            cli,
            [
                backend["key"],
                "config",
                "add",
                "staging",
                "--host",
                "https://staging.example.org",
                backend["secret_opt"],
                "key2",
            ],
        )
        cfg = load_config(config_file)
        assert cfg[backend["key"]]["default_profile"] == "prod"

    def test_add_duplicate_fails(self, backend, config_file):
        """Adding an existing profile name produces an error."""
        _seed_config(backend, config_file, {"prod": _prof(backend)})
        result = CliRunner().invoke(
            cli,
            [
                backend["key"],
                "config",
                "add",
                "prod",
                "--host",
                "https://new.example.org",
                backend["secret_opt"],
                "newkey",
            ],
        )
        assert result.exit_code != 0
        assert "already exists" in result.output

    def test_add_with_set_default(self, backend, config_file):
        """--set-default flag sets the new profile as default."""
        _seed_config(backend, config_file, {"prod": _prof(backend)}, default="prod")
        CliRunner().invoke(
            cli,
            [
                backend["key"],
                "config",
                "add",
                "staging",
                "--host",
                "https://staging.example.org",
                backend["secret_opt"],
                "key2",
                "--set-default",
            ],
        )
        cfg = load_config(config_file)
        assert cfg[backend["key"]]["default_profile"] == "staging"

    def test_add_no_verify_ssl(self, backend, config_file):
        """--no-verify-ssl sets verify_ssl to false."""
        result = CliRunner().invoke(
            cli,
            [
                backend["key"],
                "config",
                "add",
                "dev",
                "--host",
                "https://dev.example.org",
                backend["secret_opt"],
                "devkey",
                "--no-verify-ssl",
            ],
        )
        assert result.exit_code == 0
        cfg = load_config(config_file)
        assert cfg[backend["key"]]["dev"]["verify_ssl"] is False


# ===================================================================
# Test: config list
# ===================================================================


class TestConfigList:
    """Tests for 'config list' CLI command."""

    def test_list_empty(self, backend, config_file):
        """No profiles shows a helpful message."""
        result = CliRunner().invoke(cli, [backend["key"], "config", "list"])
        assert result.exit_code == 0
        assert f"No {backend['display']} profiles" in result.output

    def test_list_profiles(self, backend, config_file):
        """Lists profiles."""
        _seed_config(
            backend,
            config_file,
            {
                "prod": _prof(backend, host="https://prod.example.org", secret="k1"),
                "staging": _prof(
                    backend, host="https://staging.example.org", secret="k2"
                ),
            },
            default="prod",
        )
        result = CliRunner().invoke(cli, [backend["key"], "config", "list"])
        assert result.exit_code == 0
        assert "prod" in result.output
        assert "staging" in result.output

    def test_list_marks_default(self, backend, config_file):
        """Default profile is marked with '(default)'."""
        _seed_config(
            backend,
            config_file,
            {"prod": _prof(backend, host="https://prod.example.org", secret="k1")},
            default="prod",
        )
        result = CliRunner().invoke(cli, [backend["key"], "config", "list"])
        assert "(default)" in result.output


# ===================================================================
# Test: config show
# ===================================================================


class TestConfigShow:
    """Tests for 'config show' CLI command."""

    def test_show_profile(self, backend, config_file):
        """Shows profile details."""
        _seed_config(
            backend,
            config_file,
            {
                "prod": _prof(
                    backend,
                    host="https://eln.example.org",
                    secret="abc123secret",
                    verify_ssl=True,
                ),
            },
            default="prod",
        )
        result = CliRunner().invoke(cli, [backend["key"], "config", "show", "prod"])
        assert result.exit_code == 0
        assert "https://eln.example.org" in result.output
        assert "(default)" in result.output

    def test_show_masks_secret(self, backend, config_file):
        """Secret credential is masked by default."""
        _seed_config(
            backend,
            config_file,
            {"prod": _prof(backend, secret="abc123secret")},
        )
        result = CliRunner().invoke(cli, [backend["key"], "config", "show", "prod"])
        assert "abc123secret" not in result.output
        assert "abc1" in result.output
        assert "..." in result.output
        # The tail of the secret must not be revealed by the mask.
        assert "cret" not in result.output

    def test_show_with_show_key(self, backend, config_file):
        """--show-key reveals the full secret credential."""
        _seed_config(
            backend,
            config_file,
            {"prod": _prof(backend, secret="abc123secret")},
        )
        result = CliRunner().invoke(
            cli, [backend["key"], "config", "show", "prod", "--show-key"]
        )
        assert "abc123secret" in result.output

    def test_show_nonexistent(self, backend, config_file):
        """Nonexistent profile produces an error."""
        result = CliRunner().invoke(cli, [backend["key"], "config", "show", "nope"])
        assert result.exit_code != 0
        assert "not found" in result.output


# ===================================================================
# Test: config remove
# ===================================================================


class TestConfigRemove:
    """Tests for 'config remove' CLI command."""

    def test_remove_profile(self, backend, config_file):
        """Removes a profile from the config file."""
        _seed_config(
            backend,
            config_file,
            {
                "prod": _prof(backend),
                "staging": _prof(backend, host="y", secret="k2"),
            },
            default="prod",
        )
        result = CliRunner().invoke(
            cli, [backend["key"], "config", "remove", "staging", "--yes"]
        )
        assert result.exit_code == 0
        assert "removed" in result.output
        cfg = load_config(config_file)
        assert "staging" not in cfg[backend["key"]]
        assert "prod" in cfg[backend["key"]]

    def test_remove_default_clears_default(self, backend, config_file):
        """Removing the default profile clears the default_profile key."""
        _seed_config(backend, config_file, {"prod": _prof(backend)}, default="prod")
        result = CliRunner().invoke(
            cli, [backend["key"], "config", "remove", "prod", "--yes"]
        )
        assert result.exit_code == 0
        assert "Default cleared" in result.output
        cfg = load_config(config_file)
        assert "default_profile" not in cfg.get(backend["key"], {})

    def test_remove_nonexistent(self, backend, config_file):
        """Removing a nonexistent profile produces an error."""
        result = CliRunner().invoke(
            cli, [backend["key"], "config", "remove", "nope", "--yes"]
        )
        assert result.exit_code != 0
        assert "not found" in result.output

    def test_remove_prompts_for_confirmation(self, backend, config_file):
        """Without --yes, remove prompts for confirmation."""
        _seed_config(backend, config_file, {"prod": _prof(backend)})
        # Send 'n' to abort
        result = CliRunner().invoke(
            cli, [backend["key"], "config", "remove", "prod"], input="n\n"
        )
        assert result.exit_code != 0
        # Profile should still exist
        cfg = load_config(config_file)
        assert "prod" in cfg[backend["key"]]


# ===================================================================
# Test: config set-default
# ===================================================================


class TestConfigSetDefault:
    """Tests for 'config set-default' CLI command."""

    def test_set_default(self, backend, config_file):
        """Sets the default profile."""
        _seed_config(
            backend,
            config_file,
            {
                "prod": _prof(backend),
                "staging": _prof(backend, host="y", secret="k2"),
            },
            default="prod",
        )
        result = CliRunner().invoke(
            cli, [backend["key"], "config", "set-default", "staging"]
        )
        assert result.exit_code == 0
        cfg = load_config(config_file)
        assert cfg[backend["key"]]["default_profile"] == "staging"

    def test_set_default_nonexistent(self, backend, config_file):
        """Setting nonexistent profile as default produces an error."""
        result = CliRunner().invoke(
            cli, [backend["key"], "config", "set-default", "nope"]
        )
        assert result.exit_code != 0
        assert "not found" in result.output
