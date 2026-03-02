r"""
CLI commands for Kadi4Mat integration.

Provides commands to interact with a Kadi4Mat electronic lab notebook instance,
including fetching records as datapackages, exporting collections, and uploading
local datapackages.

EXAMPLES::

    >>> from click.testing import CliRunner
    >>> from unitpackage.eln.kadi_cli import kadi
    >>> result = CliRunner().invoke(kadi, ["--help"])
    >>> "info" in result.output
    True

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

logger = logging.getLogger("unitpackage")


@click.group()
@click.option(
    "--host",
    type=str,
    envvar="KADI_HOST",
    default=None,
    help="Kadi4Mat server URL",
)
@click.option(
    "--pat",
    type=str,
    envvar="KADI_PAT",
    default=None,
    help="Kadi4Mat Personal Access Token",
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
def kadi(ctx, host, pat, no_verify_ssl, profile):
    r"""
    Interact with a Kadi4Mat electronic lab notebook instance.

    Credentials are resolved in order: CLI options, environment variables
    (KADI_HOST / KADI_PAT), then the configuration file
    (~/.config/unitpackage/config.toml).
    """
    ctx.ensure_object(dict)

    try:
        from unitpackage.eln.kadi import KadiClient
    except ImportError as e:
        raise click.ClickException(
            "The kadi-apy package is required for Kadi4Mat integration. "
            "Install it with: pip install kadi-apy"
        ) from e

    # Priority: CLI option > env var > config file.
    if host and pat:
        try:
            client = KadiClient(host=host, pat=pat, verify_ssl=not no_verify_ssl)
        except Exception as e:
            raise click.ClickException(f"Failed to create Kadi4Mat client: {e}") from e
    else:
        # Fall through to config file
        from unitpackage.config import config_path, get_profile

        settings = get_profile("kadi", profile=profile)
        if not settings:
            if profile:
                raise click.UsageError(
                    f"Profile '{profile}' not found in {config_path()}. "
                    "Check the profile name or provide --host and --pat."
                )
            raise click.UsageError(
                "Missing Kadi4Mat credentials. Provide --host and --pat, "
                "set KADI_HOST/KADI_PAT environment variables, "
                f"or add a [kadi.<name>] section to {config_path()}."
            )

        resolved_host = host or settings.get("host")
        resolved_pat = pat or settings.get("pat")

        if not resolved_host:
            raise click.UsageError(
                "Missing host URL (not in CLI, env, or config profile)."
            )
        if not resolved_pat:
            raise click.UsageError("Missing PAT (not in CLI, env, or config profile).")

        if no_verify_ssl:
            verify_ssl = False
        else:
            verify_ssl = settings.get("verify_ssl", True)

        try:
            client = KadiClient(
                host=resolved_host, pat=resolved_pat, verify_ssl=verify_ssl
            )
        except Exception as e:
            raise click.ClickException(
                f"Failed to create Kadi4Mat client from config: {e}"
            ) from e

    ctx.obj["client"] = client


@kadi.command()
@click.pass_context
def info(ctx):
    r"""
    Show Kadi4Mat instance information.
    \f

    Print basic information about the connected Kadi4Mat instance.
    """
    client = ctx.obj["client"]

    try:
        server_info = client.info()
    except Exception as e:
        raise click.ClickException(f"Failed to fetch instance info: {e}") from e

    if isinstance(server_info, dict):
        for key, value in server_info.items():
            click.echo(f"{key}: {value}")
    else:
        click.echo(f"Connected: {server_info}")


@kadi.command()
@click.argument("record_id", type=int)
@click.option(
    "--outdir",
    type=click.Path(file_okay=False),
    default=".",
    help="Output directory for the datapackage",
)
@click.pass_context
def fetch(ctx, record_id, outdir):
    r"""
    Fetch a single record from Kadi4Mat and save as a datapackage.
    \f

    EXAMPLES::

        >>> # Fetch record 42 and save to the current directory
        >>> # unitpackage kadi --host https://kadi.example.edu --pat TOKEN fetch 42

    """
    import os

    client = ctx.obj["client"]

    try:
        entry = client.fetch_entry(record_id)
    except Exception as e:
        raise click.ClickException(f"Failed to fetch record {record_id}: {e}") from e

    os.makedirs(outdir, exist_ok=True)
    entry.save(outdir=outdir)
    click.echo(f"Saved record {record_id} to {outdir}")


@kadi.command(name="export")
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
def export_records(ctx, tags, outdir):
    r"""
    Fetch multiple records from Kadi4Mat filtered by tags.
    \f

    EXAMPLES::

        >>> # Export all records tagged 'electrochemistry'
        >>> # unitpackage kadi --host https://kadi.example.edu --pat TOKEN export --tag electrochemistry

    """
    import os

    client = ctx.obj["client"]

    try:
        entries = client.fetch_entries(list(tags) if tags else None)
    except Exception as e:
        raise click.ClickException(f"Failed to fetch records: {e}") from e

    if not entries:
        click.echo("No records found matching the specified tags.")
        return

    os.makedirs(outdir, exist_ok=True)

    for entry in entries:
        entry.save(outdir=outdir)

    click.echo(f"Saved {len(entries)} records to {outdir}")


@kadi.command()
@click.argument("file", type=click.Path(exists=True))
@click.option(
    "--title",
    type=str,
    default=None,
    help="Title for the Kadi4Mat record",
)
@click.option(
    "--tag",
    "tags",
    multiple=True,
    help="Tag to add to the record (can be specified multiple times)",
)
@click.pass_context
def upload(ctx, file, title, tags):
    r"""
    Upload a local datapackage to Kadi4Mat.
    \f

    Load an Entry from a local JSON datapackage file and upload it to the
    Kadi4Mat instance.

    EXAMPLES::

        >>> # Upload a datapackage to Kadi4Mat
        >>> # unitpackage kadi --host https://kadi.example.edu --pat TOKEN upload my_entry.json

    """
    from unitpackage.entry import Entry

    client = ctx.obj["client"]

    try:  # pylint: disable=duplicate-code
        entry = Entry.from_local(file)
    except Exception as e:
        raise click.ClickException(
            f"Failed to load datapackage from {file}: {e}"
        ) from e

    try:
        record_id = client.upload_entry(
            entry, title=title, tags=list(tags) if tags else None
        )
    except Exception as e:
        raise click.ClickException(f"Failed to upload entry to Kadi4Mat: {e}") from e

    if record_id is not None:
        click.echo(f"Uploaded {file} to Kadi4Mat as record {record_id}")
    else:
        click.echo(f"Uploaded {file} to Kadi4Mat")
