r"""
Configuration file support for unitpackage ELN backends.

Loads a TOML configuration file from the XDG config directory
(``~/.config/unitpackage/config.toml`` by default, or
``$XDG_CONFIG_HOME/unitpackage/config.toml`` if set).

The file uses named profiles grouped by backend type.  A
``default_profile`` key selects which profile is used when none is
specified explicitly::

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

EXAMPLES:

Get the default config file path::

    >>> from pathlib import Path
    >>> p = config_path()
    >>> p.name
    'config.toml'
    >>> p.parent.name
    'unitpackage'

Load config from a nonexistent file::

    >>> load_config("/nonexistent/path/config.toml")
    {}

Look up a profile from a pre-loaded config dict::

    >>> cfg = {"elabftw": {"default_profile": "prod", "prod": {"host": "https://eln.example.org", "api_key": "key"}}}
    >>> get_profile("elabftw", "prod", config=cfg)
    {'host': 'https://eln.example.org', 'api_key': 'key'}

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
import os
import sys
from pathlib import Path


def config_path():
    r"""
    Return the path to the unitpackage configuration file.

    On Linux and macOS, respects the ``XDG_CONFIG_HOME`` environment
    variable, falling back to ``~/.config``.  On Windows, uses
    ``%APPDATA%`` (typically ``C:\Users\<user>\AppData\Roaming``),
    falling back to ``~/.config``.

    EXAMPLES::

        >>> import os
        >>> os.environ["XDG_CONFIG_HOME"] = "/tmp/xdg"
        >>> str(config_path()).replace("\\", "/")
        '/tmp/xdg/unitpackage/config.toml'

    """
    xdg_config_home = os.environ.get("XDG_CONFIG_HOME", "").strip()
    if xdg_config_home:
        base = Path(xdg_config_home)
    elif sys.platform == "win32":
        appdata = os.environ.get("APPDATA", "").strip()
        base = Path(appdata) if appdata else Path.home() / ".config"
    else:
        base = Path.home() / ".config"
    return base / "unitpackage" / "config.toml"


def load_config(path=None):
    r"""
    Load the unitpackage configuration file and return it as a dict.

    If ``path`` is ``None``, the default :func:`config_path` is used.
    Returns an empty dict if the file does not exist.

    Raises ``ValueError`` if the file exists but cannot be parsed.

    EXAMPLES::

        >>> load_config("/nonexistent/path/config.toml")
        {}

    """
    if path is None:
        path = config_path()
    path = Path(path)

    if not path.is_file():
        return {}

    if sys.version_info >= (3, 11):
        import tomllib
    else:
        try:
            import tomli as tomllib
        except ImportError as exc:
            raise ImportError(
                "The 'tomli' package is required for config file support "
                "on Python < 3.11. Install it with: pip install tomli"
            ) from exc

    try:
        with open(path, "rb") as f:
            return tomllib.load(f)
    except Exception as exc:
        raise ValueError(f"Failed to parse configuration file {path}: {exc}") from exc


def get_profile(backend, profile=None, config=None):
    r"""
    Return the configuration dict for a named profile of a backend.

    If ``profile`` is ``None``, the ``default_profile`` key in the
    backend section selects the profile.  If ``config`` is ``None``,
    :func:`load_config` is called.  Returns an empty dict if the
    backend or profile is not found.

    EXAMPLES::

        >>> cfg = {"elabftw": {"default_profile": "prod", "prod": {"host": "https://eln.example.org", "api_key": "key"}}}
        >>> get_profile("elabftw", "prod", config=cfg)
        {'host': 'https://eln.example.org', 'api_key': 'key'}

        >>> get_profile("elabftw", config=cfg)
        {'host': 'https://eln.example.org', 'api_key': 'key'}

        >>> get_profile("elabftw", "nonexistent", config=cfg)
        {}


    Auto-selects when there is exactly one profile and no default::

        >>> cfg2 = {"elabftw": {"myhost": {"host": "https://eln.example.org", "api_key": "key"}}}
        >>> get_profile("elabftw", config=cfg2)
        {'host': 'https://eln.example.org', 'api_key': 'key'}

    """
    if config is None:
        config = load_config()

    backend_section = config.get(backend, {})
    if not backend_section:
        return {}

    if profile is not None:
        return backend_section.get(profile, {})

    # Use the explicitly configured default profile
    default_name = backend_section.get("default_profile")
    if default_name:
        return backend_section.get(default_name, {})

    # Auto-select when there is exactly one profile
    profiles = [
        k
        for k, v in backend_section.items()
        if k != "default_profile" and isinstance(v, dict)
    ]
    if len(profiles) == 1:
        return backend_section[profiles[0]]

    return {}


def list_profiles(backend, config=None):
    r"""
    Return the profile names available for a backend.

    The ``default_profile`` key is excluded from the result.

    EXAMPLES::

        >>> cfg = {"elabftw": {"default_profile": "prod", "prod": {}, "staging": {}}}
        >>> list_profiles("elabftw", config=cfg)
        ['prod', 'staging']

        >>> list_profiles("kadi", config=cfg)
        []

    """
    if config is None:
        config = load_config()
    return [k for k in config.get(backend, {}) if k != "default_profile"]


def _toml_value(value):
    r"""
    Format a Python value as a TOML literal.

    Only the scalar types the unitpackage config actually stores --- ``bool``,
    ``int``, ``float`` and ``str`` --- are supported. Anything else (e.g. a
    nested ``dict`` or a ``list``) raises ``TypeError`` instead of being
    silently stringified into invalid TOML.

    EXAMPLES::

        >>> _toml_value(True)
        'true'
        >>> _toml_value(False)
        'false'
        >>> _toml_value(42)
        '42'
        >>> _toml_value("hello")
        '"hello"'
        >>> _toml_value('say "hi"')
        '"say \\"hi\\""'

    Unsupported types are rejected rather than mis-emitted::

        >>> _toml_value(["a", "b"])
        Traceback (most recent call last):
        ...
        TypeError: Cannot serialize value of type 'list' to TOML; only bool, int, float and str are supported.

    """
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, (int, float)):
        return str(value)
    if isinstance(value, str):
        escaped = value.replace("\\", "\\\\").replace('"', '\\"')
        return f'"{escaped}"'
    raise TypeError(
        f"Cannot serialize value of type {type(value).__name__!r} to TOML; "
        "only bool, int, float and str are supported."
    )


def _serialize_toml(config):
    r"""
    Serialize a nested config dict to a TOML-formatted string.

    Supports exactly the shape the unitpackage config uses: top-level
    sections (tables) holding scalar keys and at most one level of
    sub-table profiles. Structures that fall outside this shape --- a
    non-table top-level value, or a table nested more than one level deep
    --- raise instead of being silently dropped or mis-emitted, since this
    is a purpose-built serializer, not a general TOML writer.

    EXAMPLES::

        >>> print(_serialize_toml({"b": {"x": "1", "sub": {"k": "v"}}}), end="")
        [b]
        x = "1"
        <BLANKLINE>
        [b.sub]
        k = "v"

    A top-level value that is not a table is rejected::

        >>> _serialize_toml({"b": "scalar"})
        Traceback (most recent call last):
        ...
        ValueError: Cannot serialize 'b': top-level config values must be tables (sections), not str.

    A table nested more than one level deep is rejected::

        >>> _serialize_toml({"b": {"prof": {"nested": {"k": "v"}}}})
        Traceback (most recent call last):
        ...
        ValueError: Cannot serialize nested table [b.prof].nested: only one level of sub-tables is supported.

    """
    lines = []
    for section, content in config.items():
        if not isinstance(content, dict):
            raise ValueError(
                f"Cannot serialize {section!r}: top-level config values must "
                f"be tables (sections), not {type(content).__name__}."
            )
        lines.append(f"[{section}]")
        for key, value in content.items():
            if not isinstance(value, dict):
                lines.append(f"{key} = {_toml_value(value)}")
        lines.append("")
        for key, value in content.items():
            if isinstance(value, dict):
                lines.append(f"[{section}.{key}]")
                for k, v in value.items():
                    if isinstance(v, dict):
                        raise ValueError(
                            f"Cannot serialize nested table [{section}.{key}].{k}: "
                            "only one level of sub-tables is supported."
                        )
                    lines.append(f"{k} = {_toml_value(v)}")
                lines.append("")
    return "\n".join(lines) + "\n" if lines else ""


def save_config(config, path=None):
    r"""
    Write the configuration dict to the TOML config file.

    If ``path`` is ``None``, the default :func:`config_path` is used.
    Creates parent directories if they do not exist.

    The file holds API keys and access tokens in plain text, so on POSIX
    systems it is written with owner-only permissions (``0o600``) and its
    parent directory with ``0o700`` to keep the secrets out of reach of
    other users. File-permission bits are a no-op on Windows.

    EXAMPLES::

        >>> import tempfile, os
        >>> d = tempfile.mkdtemp()
        >>> p = os.path.join(d, "sub", "config.toml")
        >>> save_config({"elabftw": {"default_profile": "prod", "prod": {"host": "https://example.org", "api_key": "key"}}}, path=p)
        >>> load_config(p)["elabftw"]["prod"]["host"]
        'https://example.org'

    On POSIX systems the file is owner-readable only::

        >>> import stat, sys
        >>> sys.platform == "win32" or stat.S_IMODE(os.stat(p).st_mode) == 0o600
        True

    """
    if path is None:
        path = config_path()
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    if sys.platform != "win32":
        # Restrict the directory before the secret-bearing file lands in it.
        try:
            os.chmod(path.parent, 0o700)
        except OSError:
            pass
    # Create (or truncate) the file with owner-only permissions from the start,
    # so the secrets are never briefly world-readable between write and chmod.
    if sys.platform == "win32":
        path.write_text(_serialize_toml(config), encoding="utf-8")
    else:
        fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o600)
        with os.fdopen(fd, "w", encoding="utf-8") as handle:
            handle.write(_serialize_toml(config))
        # Enforce 0o600 even if the file pre-existed with looser bits
        # (O_CREAT does not change an existing file's mode).
        os.chmod(path, 0o600)
