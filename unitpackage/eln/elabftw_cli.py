r"""
CLI commands for eLabFTW integration.

Provides commands to interact with an eLabFTW electronic lab notebook instance,
including fetching experiments and items as datapackages, exporting collections,
and uploading local datapackages.

EXAMPLES::

    >>> from unitpackage.test.cli import invoke
    >>> from unitpackage.entrypoint import cli
    >>> invoke(cli, "elabftw", "--help")  # doctest: +NORMALIZE_WHITESPACE
    Usage: cli elabftw [OPTIONS] COMMAND [ARGS]...
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

from unitpackage.eln.elabftw_config_cli import config

logger = logging.getLogger("unitpackage")


@click.group()
@click.option(
    "--host",
    type=str,
    envvar="ELABFTW_HOST",
    default=None,
    help="eLabFTW server URL",
)
@click.option(
    "--api-key",
    type=str,
    envvar="ELABFTW_API_KEY",
    default=None,
    help="eLabFTW API key",
)
@click.option(
    "--no-verify-ssl",
    is_flag=True,
    default=False,
    help="Disable SSL certificate verification",
)
@click.option(
    "--profile",
    type=str,
    default=None,
    help="Configuration profile name",
)
@click.pass_context
def elabftw(ctx, host, api_key, no_verify_ssl, profile):
    r"""
    Interact with an eLabFTW electronic lab notebook instance.

    Credentials are resolved in order: CLI options, environment variables
    (ELABFTW_HOST / ELABFTW_API_KEY), then the configuration file
    (~/.config/unitpackage/config.toml).
    """
    ctx.ensure_object(dict)
    # Store raw options; client creation is deferred to _resolve_client().
    ctx.obj["_host"] = host
    ctx.obj["_api_key"] = api_key
    ctx.obj["_no_verify_ssl"] = no_verify_ssl
    ctx.obj["_profile"] = profile


def _resolve_client(ctx):
    r"""Lazily create and cache the ElabFTWClient in ``ctx.obj["client"]``."""
    if "client" in ctx.obj:
        return ctx.obj["client"]

    from unitpackage.eln.elabftw import ElabFTWClient

    host = ctx.obj["_host"]
    api_key = ctx.obj["_api_key"]
    no_verify_ssl = ctx.obj["_no_verify_ssl"]
    profile = ctx.obj["_profile"]

    # Priority: CLI option > env var > config file.
    if host and api_key:
        try:
            client = ElabFTWClient(
                host=host,
                api_key=api_key,
                verify_ssl=not no_verify_ssl,
            )
        except Exception as e:
            raise click.ClickException(f"Failed to create eLabFTW client: {e}") from e
    else:
        from unitpackage.config import config_path, get_profile

        settings = get_profile("elabftw", profile=profile)
        if not settings:
            if profile:
                raise click.UsageError(
                    f"Profile '{profile}' not found in {config_path()}. "
                    "Check the profile name or provide --host and --api-key."
                )
            raise click.UsageError(
                "Missing eLabFTW credentials. Provide --host and --api-key, "
                "set ELABFTW_HOST/ELABFTW_API_KEY environment variables, "
                f"or add an [elabftw.<name>] section to {config_path()}."
            )

        resolved_host = host or settings.get("host")
        resolved_api_key = api_key or settings.get("api_key")

        if not resolved_host:
            raise click.UsageError(
                "Missing host URL (not in CLI, env, or config profile)."
            )
        if not resolved_api_key:
            raise click.UsageError(
                "Missing API key (not in CLI, env, or config profile)."
            )

        verify_ssl = False if no_verify_ssl else settings.get("verify_ssl", True)

        try:
            client = ElabFTWClient(
                host=resolved_host,
                api_key=resolved_api_key,
                verify_ssl=verify_ssl,
            )
        except Exception as e:
            raise click.ClickException(
                f"Failed to create eLabFTW client from config: {e}"
            ) from e

    ctx.obj["client"] = client
    return client


@elabftw.command()
@click.pass_context
def info(ctx):
    r"""
    Show eLabFTW server information.
    \f

    Print the server version, number of teams, and number of users.
    """
    client = _resolve_client(ctx)

    try:
        server_info = client.info()
    except Exception as e:
        raise click.ClickException(f"Failed to fetch server info: {e}") from e

    click.echo(
        f"Version: {server_info.get('elabftw_version', server_info.get('version', 'unknown'))}"
    )
    click.echo(f"Teams: {server_info.get('teams_count', 'unknown')}")
    click.echo(
        f"Users: {server_info.get('all_users_count', server_info.get('users_count', 'unknown'))}"
    )


@elabftw.command()
@click.argument("entity_id", type=int)
@click.option(
    "--outdir",
    type=click.Path(file_okay=False),
    default=".",
    help="Output directory for the datapackage",
)
@click.pass_context
def fetch(ctx, entity_id, outdir):
    r"""
    Fetch a single entry from eLabFTW and save as a datapackage.
    \f

    EXAMPLES::

        >>> # Fetch experiment 42 and save to the current directory
        >>> # unitpackage elabftw --host https://eln.example.org --api-key KEY fetch 42

    """
    import os

    client = _resolve_client(ctx)

    try:
        entry = client.fetch_entry(entity_id)
    except Exception as e:
        raise click.ClickException(f"Failed to fetch entry {entity_id}: {e}") from e

    os.makedirs(outdir, exist_ok=True)
    entry.save(outdir=outdir)
    click.echo(f"Saved entry {entity_id} to {outdir}")


@elabftw.command(name="export")
@click.option(
    "--tag",
    "tags",
    multiple=True,
    help="Filter by tag (can be specified multiple times)",
)
@click.option(
    "--outdir",
    type=click.Path(file_okay=False),
    default=".",
    help="Output directory for the datapackages",
)
@click.pass_context
def export_entries(ctx, tags, outdir):
    r"""
    Fetch multiple entries from eLabFTW filtered by tags.
    \f

    EXAMPLES::

        >>> # Export all experiments tagged 'electrochemistry'
        >>> # unitpackage elabftw --host https://eln.example.org --api-key KEY export --tag electrochemistry

    """
    import os

    client = _resolve_client(ctx)

    try:
        entries = client.fetch_entries(list(tags))
    except Exception as e:
        raise click.ClickException(f"Failed to fetch entries: {e}") from e

    if not entries:
        click.echo("No entries found matching the specified tags.")
        return

    os.makedirs(outdir, exist_ok=True)

    for entry in entries:
        entry.save(outdir=outdir)

    click.echo(f"Saved {len(entries)} entries to {outdir}")


@elabftw.command()
@click.argument("file", type=click.Path(exists=True))
@click.option(
    "--title",
    type=str,
    default=None,
    help="Title for the eLabFTW entry",
)
@click.option(
    "--tag",
    "tags",
    multiple=True,
    help="Tag to add to the entry (can be specified multiple times)",
)
@click.pass_context
def upload(ctx, file, title, tags):
    r"""
    Upload a local datapackage to eLabFTW.
    \f

    Load an Entry from a local JSON datapackage file and upload it to the
    eLabFTW instance.

    EXAMPLES::

        >>> # Upload a datapackage to eLabFTW
        >>> # unitpackage elabftw --host https://eln.example.org --api-key KEY upload my_entry.json

    """
    from unitpackage.entry import Entry

    client = _resolve_client(ctx)

    try:  # pylint: disable=duplicate-code
        entry = Entry.from_local(file)
    except Exception as e:
        raise click.ClickException(
            f"Failed to load datapackage from {file}: {e}"
        ) from e

    try:
        entity_id = client.upload_entry(entry, title=title, tags=list(tags))
    except Exception as e:
        raise click.ClickException(f"Failed to upload entry to eLabFTW: {e}") from e

    click.echo(f"Uploaded {file} to eLabFTW as entity {entity_id}")


# Register the config management subgroup.
elabftw.add_command(config)
