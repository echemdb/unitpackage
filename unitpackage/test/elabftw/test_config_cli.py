"""
Tests for the eLabFTW config CLI commands.

Run with:  pytest test/test_config_cli.py
"""

from unittest.mock import patch

import pytest
from click.testing import CliRunner

from unitpackage.config import load_config, save_config
from unitpackage.entrypoint import cli

BACKEND = "elabftw"


@pytest.fixture()
def config_file(tmp_path):
    """Provide a temp config file and patch config_path to point to it."""
    path = tmp_path / "config.toml"
    with patch("unitpackage.config.config_path", return_value=path):
        yield path


def _seed_config(path, profiles=None, default=None):
    """Write a config file with the given profiles."""
    cfg = {BACKEND: {}}
    if default:
        cfg[BACKEND]["default_profile"] = default
    for name, data in (profiles or {}).items():
        cfg[BACKEND][name] = data
    save_config(cfg, path=path)


# ===================================================================
# Test: config add
# ===================================================================


class TestConfigAdd:
    def test_add_profile(self, config_file):
        """Add a profile and verify it appears in the config file."""
        result = CliRunner().invoke(cli, [
            "elabftw", "config", "add", "production",
            "--host", "https://eln.example.org",
            "--api-key", "abc123",
        ])
        assert result.exit_code == 0
        assert "production" in result.output
        cfg = load_config(config_file)
        assert cfg[BACKEND]["production"]["host"] == "https://eln.example.org"
        assert cfg[BACKEND]["production"]["api_key"] == "abc123"
        assert cfg[BACKEND]["production"]["verify_ssl"] is True

    def test_first_profile_becomes_default(self, config_file):
        """First profile added is automatically set as default."""
        CliRunner().invoke(cli, [
            "elabftw", "config", "add", "prod",
            "--host", "https://eln.example.org",
            "--api-key", "key",
        ])
        cfg = load_config(config_file)
        assert cfg[BACKEND]["default_profile"] == "prod"

    def test_second_profile_no_auto_default(self, config_file):
        """Second profile does not change the default."""
        _seed_config(config_file, {"prod": {"host": "x", "api_key": "k"}}, default="prod")
        CliRunner().invoke(cli, [
            "elabftw", "config", "add", "staging",
            "--host", "https://staging.example.org",
            "--api-key", "key2",
        ])
        cfg = load_config(config_file)
        assert cfg[BACKEND]["default_profile"] == "prod"

    def test_add_duplicate_fails(self, config_file):
        """Adding an existing profile name produces an error."""
        _seed_config(config_file, {"prod": {"host": "x", "api_key": "k"}})
        result = CliRunner().invoke(cli, [
            "elabftw", "config", "add", "prod",
            "--host", "https://new.example.org",
            "--api-key", "newkey",
        ])
        assert result.exit_code != 0
        assert "already exists" in result.output

    def test_add_with_set_default(self, config_file):
        """--set-default flag sets the new profile as default."""
        _seed_config(config_file, {"prod": {"host": "x", "api_key": "k"}}, default="prod")
        CliRunner().invoke(cli, [
            "elabftw", "config", "add", "staging",
            "--host", "https://staging.example.org",
            "--api-key", "key2",
            "--set-default",
        ])
        cfg = load_config(config_file)
        assert cfg[BACKEND]["default_profile"] == "staging"

    def test_add_no_verify_ssl(self, config_file):
        """--no-verify-ssl sets verify_ssl to false."""
        result = CliRunner().invoke(cli, [
            "elabftw", "config", "add", "dev",
            "--host", "https://dev.example.org",
            "--api-key", "devkey",
            "--no-verify-ssl",
        ])
        assert result.exit_code == 0
        cfg = load_config(config_file)
        assert cfg[BACKEND]["dev"]["verify_ssl"] is False


# ===================================================================
# Test: config list
# ===================================================================


class TestConfigList:
    def test_list_empty(self, config_file):
        """No profiles shows a helpful message."""
        result = CliRunner().invoke(cli, ["elabftw", "config", "list"])
        assert result.exit_code == 0
        assert "No eLabFTW profiles" in result.output

    def test_list_profiles(self, config_file):
        """Lists profiles."""
        _seed_config(config_file, {
            "prod": {"host": "https://prod.example.org", "api_key": "k1"},
            "staging": {"host": "https://staging.example.org", "api_key": "k2"},
        }, default="prod")
        result = CliRunner().invoke(cli, ["elabftw", "config", "list"])
        assert result.exit_code == 0
        assert "prod" in result.output
        assert "staging" in result.output

    def test_list_marks_default(self, config_file):
        """Default profile is marked with '(default)'."""
        _seed_config(config_file, {
            "prod": {"host": "https://prod.example.org", "api_key": "k1"},
        }, default="prod")
        result = CliRunner().invoke(cli, ["elabftw", "config", "list"])
        assert "(default)" in result.output


# ===================================================================
# Test: config show
# ===================================================================


class TestConfigShow:
    def test_show_profile(self, config_file):
        """Shows profile details."""
        _seed_config(config_file, {
            "prod": {"host": "https://eln.example.org", "api_key": "abc123secret", "verify_ssl": True},
        }, default="prod")
        result = CliRunner().invoke(cli, ["elabftw", "config", "show", "prod"])
        assert result.exit_code == 0
        assert "https://eln.example.org" in result.output
        assert "(default)" in result.output

    def test_show_masks_api_key(self, config_file):
        """API key is masked by default."""
        _seed_config(config_file, {
            "prod": {"host": "x", "api_key": "abc123secret"},
        })
        result = CliRunner().invoke(cli, ["elabftw", "config", "show", "prod"])
        assert "abc123secret" not in result.output
        assert "abc1" in result.output
        assert "..." in result.output

    def test_show_with_show_key(self, config_file):
        """--show-key reveals the full API key."""
        _seed_config(config_file, {
            "prod": {"host": "x", "api_key": "abc123secret"},
        })
        result = CliRunner().invoke(cli, ["elabftw", "config", "show", "prod", "--show-key"])
        assert "abc123secret" in result.output

    def test_show_nonexistent(self, config_file):
        """Nonexistent profile produces an error."""
        result = CliRunner().invoke(cli, ["elabftw", "config", "show", "nope"])
        assert result.exit_code != 0
        assert "not found" in result.output


# ===================================================================
# Test: config remove
# ===================================================================


class TestConfigRemove:
    def test_remove_profile(self, config_file):
        """Removes a profile from the config file."""
        _seed_config(config_file, {
            "prod": {"host": "x", "api_key": "k"},
            "staging": {"host": "y", "api_key": "k2"},
        }, default="prod")
        result = CliRunner().invoke(cli, ["elabftw", "config", "remove", "staging", "--yes"])
        assert result.exit_code == 0
        assert "removed" in result.output
        cfg = load_config(config_file)
        assert "staging" not in cfg[BACKEND]
        assert "prod" in cfg[BACKEND]

    def test_remove_default_clears_default(self, config_file):
        """Removing the default profile clears the default_profile key."""
        _seed_config(config_file, {
            "prod": {"host": "x", "api_key": "k"},
        }, default="prod")
        result = CliRunner().invoke(cli, ["elabftw", "config", "remove", "prod", "--yes"])
        assert result.exit_code == 0
        assert "Default cleared" in result.output
        cfg = load_config(config_file)
        assert "default_profile" not in cfg.get(BACKEND, {})

    def test_remove_nonexistent(self, config_file):
        """Removing a nonexistent profile produces an error."""
        result = CliRunner().invoke(cli, ["elabftw", "config", "remove", "nope", "--yes"])
        assert result.exit_code != 0
        assert "not found" in result.output

    def test_remove_prompts_for_confirmation(self, config_file):
        """Without --yes, remove prompts for confirmation."""
        _seed_config(config_file, {"prod": {"host": "x", "api_key": "k"}})
        # Send 'n' to abort
        result = CliRunner().invoke(
            cli, ["elabftw", "config", "remove", "prod"], input="n\n"
        )
        assert result.exit_code != 0
        # Profile should still exist
        cfg = load_config(config_file)
        assert "prod" in cfg[BACKEND]


# ===================================================================
# Test: config set-default
# ===================================================================


class TestConfigSetDefault:
    def test_set_default(self, config_file):
        """Sets the default profile."""
        _seed_config(config_file, {
            "prod": {"host": "x", "api_key": "k"},
            "staging": {"host": "y", "api_key": "k2"},
        }, default="prod")
        result = CliRunner().invoke(cli, ["elabftw", "config", "set-default", "staging"])
        assert result.exit_code == 0
        cfg = load_config(config_file)
        assert cfg[BACKEND]["default_profile"] == "staging"

    def test_set_default_nonexistent(self, config_file):
        """Setting nonexistent profile as default produces an error."""
        result = CliRunner().invoke(cli, ["elabftw", "config", "set-default", "nope"])
        assert result.exit_code != 0
        assert "not found" in result.output
