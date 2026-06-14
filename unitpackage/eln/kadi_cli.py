r"""
CLI commands for Kadi4Mat integration.

Provides commands to interact with a Kadi4Mat electronic lab notebook instance,
including fetching records as datapackages, exporting collections, and uploading
local datapackages.

The command group itself is built by :func:`unitpackage.eln._cli.make_eln_group`,
which is shared with the eLabFTW CLI; only the Kadi4Mat-specific wiring (the
``--pat`` option, the client class, and how instance info is printed) lives
here.

EXAMPLES::

    >>> from unitpackage.test.cli import invoke
    >>> from unitpackage.eln.kadi_cli import kadi
    >>> invoke(kadi, "--help")  # doctest: +NORMALIZE_WHITESPACE
    Usage: kadi [OPTIONS] COMMAND [ARGS]...
    <BLANKLINE>
      Interact with a Kadi4Mat electronic lab notebook instance.
    <BLANKLINE>
      Credentials are resolved in order: CLI options, environment variables
      (KADI_HOST / KADI_PAT), then the configuration file
      (~/.config/unitpackage/config.toml).
    <BLANKLINE>
    Options:
      --host TEXT      Kadi4Mat server URL
      --pat TEXT       Kadi4Mat Personal Access Token
      --no-verify-ssl  Disable SSL certificate verification
      --profile TEXT   Configuration profile name
      --help           Show this message and exit.
    <BLANKLINE>
    Commands:
      config  Manage Kadi4Mat connection profiles.
      export  Fetch multiple records from Kadi4Mat filtered by tags.
      fetch   Fetch a single record from Kadi4Mat and save as a datapackage.
      info    Show Kadi4Mat instance information.
      upload  Upload a local datapackage to Kadi4Mat.

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
import logging

import click

from unitpackage.eln._cli import make_eln_group
from unitpackage.eln._config_cli import make_config_group

logger = logging.getLogger("unitpackage")


def _create_client(host, secret, verify_ssl, settings):
    """Create a KadiClient (imported lazily so the optional ``kadi-apy``
    dependency is only required when the Kadi4Mat CLI is actually used)."""
    try:
        from unitpackage.eln.kadi import KadiClient
    except ImportError as e:
        raise RuntimeError(
            "The kadi-apy package is required for Kadi4Mat integration. "
            "Install it with: pip install kadi-apy"
        ) from e

    return KadiClient(
        host=host,
        pat=secret,
        verify_ssl=verify_ssl,
        base_path=settings.get("base_path"),
    )


def _print_info(server_info):
    """Print Kadi4Mat instance information as ``key: value`` lines."""
    if isinstance(server_info, dict):
        for key, value in server_info.items():
            click.echo(f"{key}: {value}")
    else:
        click.echo(f"Connected: {server_info}")


kadi = make_eln_group(
    name="kadi",
    display="Kadi4Mat",
    article="a Kadi4Mat",
    noun_singular="record",
    noun_plural="records",
    secret_opt="--pat",
    secret_envvar="KADI_PAT",
    secret_help="Kadi4Mat Personal Access Token",
    secret_label="PAT",
    secret_config_key="pat",
    host_envvar="KADI_HOST",
    section_hint="a [kadi.<name>]",
    client_factory=_create_client,
    info_printer=_print_info,
    info_help="Show Kadi4Mat instance information.",
    info_error_label="instance",
)

# Register the config management subgroup.
kadi.add_command(
    make_config_group(
        backend="kadi",
        display="Kadi4Mat",
        secret_opt="--pat",
        secret_field="pat",
        secret_label="Personal Access Token",
    )
)
