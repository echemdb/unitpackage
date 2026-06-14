r"""
CLI commands for eLabFTW integration.

Provides commands to interact with an eLabFTW electronic lab notebook instance,
including fetching items (eLabFTW resources) as datapackages, exporting
collections, and uploading local datapackages.

Only the eLabFTW ``items`` entity type is supported at the moment; eLabFTW
*experiments* are not yet supported.

The command group itself is built by :func:`unitpackage.eln._cli.make_eln_group`,
which is shared with the Kadi4Mat CLI; only the eLabFTW-specific wiring (the
``--api-key`` option, the client class, and how server info is printed) lives
here.

EXAMPLES::

    >>> from unitpackage.test.cli import invoke
    >>> from unitpackage.eln.elabftw_cli import elabftw
    >>> invoke(elabftw, "--help")  # doctest: +NORMALIZE_WHITESPACE
    Usage: elabftw [OPTIONS] COMMAND [ARGS]...
    <BLANKLINE>
      Interact with an eLabFTW electronic lab notebook instance.
    <BLANKLINE>
      Credentials are resolved in order: CLI options, environment variables
      (ELABFTW_HOST / ELABFTW_API_KEY), then the configuration file
      (~/.config/unitpackage/config.toml).
    <BLANKLINE>
    Options:
      --host TEXT      eLabFTW server URL
      --api-key TEXT   eLabFTW API key
      --no-verify-ssl  Disable SSL certificate verification
      --profile TEXT   Configuration profile name
      --help           Show this message and exit.
    <BLANKLINE>
    Commands:
      config  Manage eLabFTW connection profiles.
      export  Fetch multiple entries from eLabFTW filtered by tags.
      fetch   Fetch a single entry from eLabFTW and save as a datapackage.
      info    Show eLabFTW server information.
      upload  Upload a local datapackage to eLabFTW.

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


def _create_client(host, secret, verify_ssl, _settings):
    """Create an ElabFTWClient (imported lazily so the optional dependency is
    only required when the eLabFTW CLI is actually used)."""
    from unitpackage.eln.elabftw import ElabFTWClient

    return ElabFTWClient(host=host, api_key=secret, verify_ssl=verify_ssl)


def _print_info(server_info):
    """Print eLabFTW server version, team count, and user count."""
    click.echo(
        f"Version: {server_info.get('elabftw_version', server_info.get('version', 'unknown'))}"
    )
    click.echo(f"Teams: {server_info.get('teams_count', 'unknown')}")
    click.echo(
        f"Users: {server_info.get('all_users_count', server_info.get('users_count', 'unknown'))}"
    )


elabftw = make_eln_group(
    name="elabftw",
    display="eLabFTW",
    article="an eLabFTW",
    noun_singular="entry",
    noun_plural="entries",
    secret_opt="--api-key",
    secret_envvar="ELABFTW_API_KEY",
    secret_help="eLabFTW API key",
    secret_label="API key",
    secret_config_key="api_key",
    host_envvar="ELABFTW_HOST",
    section_hint="an [elabftw.<name>]",
    client_factory=_create_client,
    info_printer=_print_info,
    info_help="Show eLabFTW server information.",
    info_error_label="server",
)

# Register the config management subgroup.
elabftw.add_command(
    make_config_group(
        backend="elabftw",
        display="eLabFTW",
        secret_opt="--api-key",
        secret_field="api_key",
        secret_label="API key",
    )
)
