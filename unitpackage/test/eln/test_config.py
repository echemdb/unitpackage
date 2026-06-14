"""
Tests for unitpackage.config -- the multi-backend configuration system.

Run with:  pytest test/test_config.py
"""

# pylint: disable=redefined-outer-name,missing-function-docstring

from pathlib import Path
from unittest.mock import patch

import pytest

from unitpackage.config import (
    _serialize_toml,
    _toml_value,
    config_path,
    get_profile,
    list_profiles,
    load_config,
    save_config,
)

SAMPLE_TOML = """\
[elabftw]
default_profile = "production"

[elabftw.production]
host = "https://eln.example.org"
api_key = "abc123"
verify_ssl = true

[elabftw.staging]
host = "https://staging-eln.example.org"
api_key = "def456"
verify_ssl = false
"""


# ===================================================================
# Test: config_path
# ===================================================================


class TestConfigPath:
    """Tests for config_path()."""

    def test_default_path(self):
        """Without XDG_CONFIG_HOME, returns ~/.config/unitpackage/config.toml."""
        with patch.dict("os.environ", {}, clear=False):
            # Remove XDG_CONFIG_HOME if present
            import os

            env = os.environ.copy()
            env.pop("XDG_CONFIG_HOME", None)
            with patch.dict("os.environ", env, clear=True):
                p = config_path()
                assert p == Path.home() / ".config" / "unitpackage" / "config.toml"

    def test_xdg_config_home(self):
        """Respects XDG_CONFIG_HOME when set."""
        with patch.dict("os.environ", {"XDG_CONFIG_HOME": "/custom/config"}):
            p = config_path()
            assert p == Path("/custom/config/unitpackage/config.toml")

    def test_xdg_empty_string(self):
        """Empty XDG_CONFIG_HOME falls back to ~/.config."""
        with patch.dict("os.environ", {"XDG_CONFIG_HOME": ""}):
            p = config_path()
            assert p == Path.home() / ".config" / "unitpackage" / "config.toml"

    def test_windows_appdata(self):
        """On Windows, uses APPDATA when XDG_CONFIG_HOME is not set."""
        env = {"APPDATA": "C:\\Users\\testuser\\AppData\\Roaming"}
        with (
            patch("unitpackage.config.sys") as mock_sys,
            patch.dict("os.environ", env, clear=True),
        ):
            mock_sys.platform = "win32"
            mock_sys.version_info = __import__("sys").version_info
            p = config_path()
            assert (
                p
                == Path("C:\\Users\\testuser\\AppData\\Roaming")
                / "unitpackage"
                / "config.toml"
            )

    def test_windows_xdg_overrides_appdata(self):
        """On Windows, XDG_CONFIG_HOME takes precedence over APPDATA."""
        env = {
            "XDG_CONFIG_HOME": "D:\\custom\\config",
            "APPDATA": "C:\\Users\\testuser\\AppData\\Roaming",
        }
        with (
            patch("unitpackage.config.sys") as mock_sys,
            patch.dict("os.environ", env, clear=True),
        ):
            mock_sys.platform = "win32"
            p = config_path()
            assert p == Path("D:\\custom\\config") / "unitpackage" / "config.toml"

    def test_windows_no_appdata_falls_back(self):
        """On Windows without APPDATA, falls back to ~/.config."""
        with (
            patch("unitpackage.config.sys") as mock_sys,
            patch.dict("os.environ", {}, clear=True),
        ):
            mock_sys.platform = "win32"
            p = config_path()
            assert p == Path.home() / ".config" / "unitpackage" / "config.toml"


# ===================================================================
# Test: load_config
# ===================================================================


class TestLoadConfig:
    """Tests for load_config()."""

    def test_missing_file_returns_empty_dict(self):
        """Nonexistent file returns empty dict without error."""
        assert not load_config("/nonexistent/path/config.toml")

    def test_valid_toml(self, tmp_path):
        """Valid TOML is parsed correctly."""
        config_file = tmp_path / "config.toml"
        config_file.write_text(SAMPLE_TOML)

        cfg = load_config(config_file)
        assert cfg["elabftw"]["production"]["host"] == "https://eln.example.org"
        assert cfg["elabftw"]["production"]["api_key"] == "abc123"
        assert cfg["elabftw"]["production"]["verify_ssl"] is True
        assert cfg["elabftw"]["staging"]["verify_ssl"] is False

    def test_malformed_toml_raises(self, tmp_path):
        """Malformed TOML raises ValueError."""
        config_file = tmp_path / "config.toml"
        config_file.write_text("[invalid\nthis is not valid toml")

        with pytest.raises(ValueError, match="Failed to parse"):
            load_config(config_file)

    def test_empty_file(self, tmp_path):
        """Empty TOML file returns empty dict."""
        config_file = tmp_path / "config.toml"
        config_file.write_text("")

        assert not load_config(config_file)


# ===================================================================
# Test: get_profile
# ===================================================================


SAMPLE_CONFIG = {
    "elabftw": {
        "default_profile": "production",
        "production": {
            "host": "https://eln.example.org",
            "api_key": "abc123",
            "verify_ssl": True,
        },
        "staging": {
            "host": "https://staging.example.org",
            "api_key": "def456",
            "verify_ssl": False,
        },
    },
}


class TestGetProfile:
    """Tests for get_profile()."""

    def test_explicit_profile(self):
        """get_profile with explicit name returns the correct profile."""
        result = get_profile("elabftw", "production", config=SAMPLE_CONFIG)
        assert result["host"] == "https://eln.example.org"
        assert result["api_key"] == "abc123"

    def test_default_profile(self):
        """get_profile without name uses default_profile."""
        result = get_profile("elabftw", config=SAMPLE_CONFIG)
        assert result["host"] == "https://eln.example.org"

    def test_single_profile_auto_selected(self):
        """get_profile auto-selects the only profile when no default is set."""
        cfg = {
            "elabftw": {
                "production": {"host": "https://eln.example.org", "api_key": "abc"},
            },
        }
        assert get_profile("elabftw", config=cfg) == {
            "host": "https://eln.example.org",
            "api_key": "abc",
        }

    def test_multiple_profiles_no_default_returns_empty(self):
        """get_profile returns empty dict when multiple profiles exist but no default is set."""
        cfg = {
            "elabftw": {
                "prod": {"host": "https://prod.example.org", "api_key": "k1"},
                "staging": {"host": "https://staging.example.org", "api_key": "k2"},
            },
        }
        assert get_profile("elabftw", config=cfg) == {}

    def test_default_profile_points_to_missing(self):
        """get_profile returns empty dict when default_profile references a nonexistent profile."""
        cfg = {
            "elabftw": {
                "default_profile": "deleted",
                "production": {"host": "https://eln.example.org", "api_key": "abc"},
            },
        }
        assert get_profile("elabftw", config=cfg) == {}

    def test_explicit_second_profile(self):
        """get_profile with second profile name returns it correctly."""
        result = get_profile("elabftw", "staging", config=SAMPLE_CONFIG)
        assert result["host"] == "https://staging.example.org"
        assert result["verify_ssl"] is False

    def test_nonexistent_profile(self):
        """Nonexistent profile returns empty dict."""
        assert get_profile("elabftw", "nonexistent", config=SAMPLE_CONFIG) == {}

    def test_nonexistent_backend(self):
        """Nonexistent backend returns empty dict."""
        assert get_profile("kadi", config=SAMPLE_CONFIG) == {}


# ===================================================================
# Test: list_profiles
# ===================================================================


class TestListProfiles:
    """Tests for list_profiles()."""

    def test_list_profiles(self):
        """Returns profile names, excluding default_profile key."""
        result = list_profiles("elabftw", config=SAMPLE_CONFIG)
        assert result == ["production", "staging"]

    def test_list_empty_backend(self):
        """Nonexistent backend returns empty list."""
        assert list_profiles("kadi", config=SAMPLE_CONFIG) == []


# ===================================================================
# Test: _toml_value
# ===================================================================


class TestTomlValue:
    """Tests for _toml_value()."""

    def test_bool_true(self):
        assert _toml_value(True) == "true"

    def test_bool_false(self):
        assert _toml_value(False) == "false"

    def test_int(self):
        assert _toml_value(42) == "42"

    def test_float(self):
        assert _toml_value(3.14) == "3.14"

    def test_string(self):
        assert _toml_value("hello") == '"hello"'

    def test_string_with_quotes(self):
        assert _toml_value('say "hi"') == '"say \\"hi\\""'

    def test_string_with_backslash(self):
        assert _toml_value("a\\b") == '"a\\\\b"'

    def test_rejects_list(self):
        """Lists are not serializable and raise TypeError."""
        with pytest.raises(TypeError, match="list"):
            _toml_value(["a", "b"])

    def test_rejects_dict(self):
        """Dicts are not serializable as a scalar and raise TypeError."""
        with pytest.raises(TypeError, match="dict"):
            _toml_value({"k": "v"})

    def test_rejects_none(self):
        """None is not serializable and raises TypeError."""
        with pytest.raises(TypeError, match="NoneType"):
            _toml_value(None)


# ===================================================================
# Test: _serialize_toml
# ===================================================================


class TestSerializeToml:
    """Tests for _serialize_toml()."""

    def test_basic_structure(self):
        """Produces valid TOML with section headers."""
        result = _serialize_toml({"s": {"key": "val"}})
        assert "[s]" in result
        assert 'key = "val"' in result

    def test_sub_tables(self):
        """Sub-dicts become [section.key] tables."""
        result = _serialize_toml({"s": {"sub": {"k": "v"}}})
        assert "[s.sub]" in result
        assert 'k = "v"' in result

    def test_bool_values(self):
        """Booleans are serialized as true/false."""
        result = _serialize_toml({"s": {"sub": {"flag": True}}})
        assert "flag = true" in result

    def test_empty_config(self):
        """Empty dict produces empty string."""
        assert _serialize_toml({}) == ""

    def test_rejects_non_table_section(self):
        """A non-table top-level value raises rather than being dropped."""
        with pytest.raises(ValueError, match="top-level"):
            _serialize_toml({"b": "scalar"})

    def test_rejects_deeply_nested_table(self):
        """A table nested more than one level deep raises."""
        with pytest.raises(ValueError, match="nested table"):
            _serialize_toml({"b": {"prof": {"nested": {"k": "v"}}}})

    def test_rejects_list_value_in_profile(self):
        """A list value inside a profile raises via the value serializer."""
        with pytest.raises(TypeError, match="list"):
            _serialize_toml({"b": {"prof": {"tags": ["a", "b"]}}})


# ===================================================================
# Test: save_config
# ===================================================================


class TestSaveConfig:
    """Tests for save_config()."""

    def test_round_trip(self, tmp_path):
        """save_config + load_config round-trip preserves data."""
        cfg = {
            "elabftw": {
                "default_profile": "prod",
                "prod": {
                    "host": "https://eln.example.org",
                    "api_key": "abc123",
                    "verify_ssl": True,
                },
            },
        }
        p = tmp_path / "config.toml"
        save_config(cfg, path=p)
        loaded = load_config(p)
        assert loaded["elabftw"]["default_profile"] == "prod"
        assert loaded["elabftw"]["prod"]["host"] == "https://eln.example.org"
        assert loaded["elabftw"]["prod"]["api_key"] == "abc123"
        assert loaded["elabftw"]["prod"]["verify_ssl"] is True

    def test_creates_parent_dirs(self, tmp_path):
        """Creates missing parent directories."""
        p = tmp_path / "deep" / "nested" / "config.toml"
        save_config({"elabftw": {"prod": {"host": "x"}}}, path=p)
        assert p.is_file()

    def test_preserves_bool_types(self, tmp_path):
        """Boolean values survive round-trip as booleans (not strings)."""
        cfg = {"elabftw": {"p": {"verify_ssl": False}}}
        p = tmp_path / "config.toml"
        save_config(cfg, path=p)
        loaded = load_config(p)
        assert loaded["elabftw"]["p"]["verify_ssl"] is False

    def test_empty_config(self, tmp_path):
        """Empty dict writes a valid (empty) file."""
        p = tmp_path / "config.toml"
        save_config({}, path=p)
        assert not load_config(p)


# ===================================================================
# Test: ElabFTWClient.from_config
# ===================================================================


class TestElabFTWFromConfig:
    """Tests for ElabFTWClient.from_config()."""

    def test_from_config_valid(self):
        """from_config with valid profile creates a client."""
        from unitpackage.eln.elabftw import ElabFTWClient

        with (
            patch("unitpackage.eln.elabftw.elabapi_python"),
            patch("unitpackage.config.load_config", return_value=SAMPLE_CONFIG),
        ):
            client = ElabFTWClient.from_config("production")
            assert client is not None

    def test_from_config_default_profile(self):
        """from_config without name uses default_profile."""
        from unitpackage.eln.elabftw import ElabFTWClient

        with (
            patch("unitpackage.eln.elabftw.elabapi_python"),
            patch("unitpackage.config.load_config", return_value=SAMPLE_CONFIG),
        ):
            client = ElabFTWClient.from_config()
            assert client is not None

    def test_from_config_missing_profile(self):
        """from_config raises ValueError for missing profile."""
        from unitpackage.eln.elabftw import ElabFTWClient

        with patch("unitpackage.config.load_config", return_value=SAMPLE_CONFIG):
            with pytest.raises(ValueError, match="No eLabFTW profile 'nonexistent'"):
                ElabFTWClient.from_config("nonexistent")

    def test_from_config_no_profiles(self):
        """from_config raises ValueError when no profiles exist."""
        from unitpackage.eln.elabftw import ElabFTWClient

        with patch("unitpackage.config.load_config", return_value={}):
            with pytest.raises(ValueError, match="No eLabFTW profiles found"):
                ElabFTWClient.from_config()

    def test_from_config_missing_host(self):
        """from_config raises ValueError when host is missing."""
        from unitpackage.eln.elabftw import ElabFTWClient

        bad_config = {"elabftw": {"broken": {"api_key": "key"}}}
        with patch("unitpackage.config.load_config", return_value=bad_config):
            with pytest.raises(ValueError, match="Missing 'host'"):
                ElabFTWClient.from_config("broken")

    def test_from_config_missing_api_key(self):
        """from_config raises ValueError when api_key is missing."""
        from unitpackage.eln.elabftw import ElabFTWClient

        bad_config = {"elabftw": {"broken": {"host": "https://eln.example.org"}}}
        with patch("unitpackage.config.load_config", return_value=bad_config):
            with pytest.raises(ValueError, match="Missing 'api_key'"):
                ElabFTWClient.from_config("broken")


# ===================================================================
# Test: KadiClient.from_config
# ===================================================================


SAMPLE_KADI_CONFIG = {
    "kadi": {
        "default_profile": "production",
        "production": {
            "host": "https://kadi.example.edu",
            "pat": "abc123",
            "verify_ssl": True,
        },
        "staging": {
            "host": "https://staging-kadi.example.edu",
            "pat": "def456",
            "verify_ssl": False,
        },
    },
}


@pytest.mark.kadi
class TestKadiFromConfig:
    """Tests for KadiClient.from_config()."""

    def test_from_config_valid(self):
        """from_config with valid profile creates a client."""
        from unitpackage.eln.kadi import KadiClient

        with (
            patch("unitpackage.eln.kadi.KadiManager"),
            patch("unitpackage.config.load_config", return_value=SAMPLE_KADI_CONFIG),
        ):
            client = KadiClient.from_config("production")
            assert client is not None

    def test_from_config_default_profile(self):
        """from_config without name uses default_profile."""
        from unitpackage.eln.kadi import KadiClient

        with (
            patch("unitpackage.eln.kadi.KadiManager"),
            patch("unitpackage.config.load_config", return_value=SAMPLE_KADI_CONFIG),
        ):
            client = KadiClient.from_config()
            assert client is not None

    def test_from_config_missing_profile(self):
        """from_config raises ValueError for missing profile."""
        from unitpackage.eln.kadi import KadiClient

        with patch("unitpackage.config.load_config", return_value=SAMPLE_KADI_CONFIG):
            with pytest.raises(ValueError, match="No Kadi profile 'nonexistent'"):
                KadiClient.from_config("nonexistent")

    def test_from_config_no_profiles(self):
        """from_config raises ValueError when no profiles exist."""
        from unitpackage.eln.kadi import KadiClient

        with patch("unitpackage.config.load_config", return_value={}):
            with pytest.raises(ValueError, match="No Kadi profiles found"):
                KadiClient.from_config()

    def test_from_config_missing_host(self):
        """from_config raises ValueError when host is missing."""
        from unitpackage.eln.kadi import KadiClient

        bad_config = {"kadi": {"broken": {"pat": "abc"}}}
        with patch("unitpackage.config.load_config", return_value=bad_config):
            with pytest.raises(ValueError, match="Missing 'host'"):
                KadiClient.from_config("broken")

    def test_from_config_missing_pat(self):
        """from_config raises ValueError when pat is missing."""
        from unitpackage.eln.kadi import KadiClient

        bad_config = {"kadi": {"broken": {"host": "https://kadi.example.edu"}}}
        with patch("unitpackage.config.load_config", return_value=bad_config):
            with pytest.raises(ValueError, match="Missing 'pat'"):
                KadiClient.from_config("broken")
