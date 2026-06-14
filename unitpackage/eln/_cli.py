r"""
Shared Click command factory for ELN backend CLIs.

Both the eLabFTW and Kadi4Mat command groups expose the same surface --- a
group with ``--host`` / secret / ``--no-verify-ssl`` / ``--profile`` options
and ``info`` / ``fetch`` / ``export`` / ``upload`` subcommands --- differing
only in backend names, the secret option (``--api-key`` vs ``--pat``), the
client class, and how server info is printed.

:func:`make_eln_group` builds a fully wired group from those few parameters so
the two backend CLI modules can stay thin wrappers around it.

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
import os

import click

logger = logging.getLogger("unitpackage")


def make_eln_group(  # pylint: disable=too-many-locals,too-many-statements
    *,
    name,
    display,
    article,
    noun_singular,
    noun_plural,
    secret_opt,
    secret_envvar,
    secret_help,
    secret_label,
    secret_config_key,
    host_envvar,
    section_hint,
    client_factory,
    info_printer,
    info_help,
    info_error_label,
):
    r"""
    Build and return a Click ``Group`` for an ELN backend.

    Parameters describe the backend's identity and wiring:

    - ``name`` --- config/backend key (e.g. ``"elabftw"``).
    - ``display`` --- human-readable backend name (e.g. ``"eLabFTW"``).
    - ``article`` --- ``display`` with its grammatical article
      (e.g. ``"an eLabFTW"``), used in the group help text.
    - ``noun_singular`` / ``noun_plural`` --- what one/many entities are called
      (e.g. ``"entry"`` / ``"entries"``).
    - ``secret_opt`` / ``secret_envvar`` / ``secret_help`` / ``secret_label``
      / ``secret_config_key`` --- the credential option flag, environment
      variable, option help, error-message label, and config-file key.
    - ``host_envvar`` --- environment variable for the host URL.
    - ``section_hint`` --- config-file section example for error messages
      (e.g. ``"an [elabftw.<name>]"``).
    - ``client_factory(host, secret, verify_ssl, settings)`` --- builds the
      backend client.
    - ``info_printer(server_info)`` --- prints ``client.info()`` output.
    - ``info_help`` / ``info_error_label`` --- help text and error label for
      the ``info`` command.

    """
    group_help = (
        f"Interact with {article} electronic lab notebook instance.\n\n"
        f"Credentials are resolved in order: CLI options, environment "
        f"variables ({host_envvar} / {secret_envvar}), then the configuration "
        f"file (~/.config/unitpackage/config.toml)."
    )

    @click.group(name=name, help=group_help)
    @click.option(
        "--host",
        type=str,
        envvar=host_envvar,
        default=None,
        help=f"{display} server URL",
    )
    @click.option(
        secret_opt,
        "secret",
        type=str,
        envvar=secret_envvar,
        default=None,
        help=secret_help,
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
    def group(ctx, host, secret, no_verify_ssl, profile):
        # Store raw options; client creation is deferred to _resolve_client().
        ctx.ensure_object(dict)
        ctx.obj["_host"] = host
        ctx.obj["_secret"] = secret
        ctx.obj["_no_verify_ssl"] = no_verify_ssl
        ctx.obj["_profile"] = profile

    def _resolve_client(ctx):
        r"""Lazily create and cache the backend client in ``ctx.obj["client"]``."""
        if "client" in ctx.obj:
            return ctx.obj["client"]

        host = ctx.obj["_host"]
        secret = ctx.obj["_secret"]
        no_verify_ssl = ctx.obj["_no_verify_ssl"]
        profile = ctx.obj["_profile"]

        settings = None
        # Priority: CLI option > env var > config file.
        if not (host and secret):
            from unitpackage.config import config_path, get_profile

            settings = get_profile(name, profile=profile)
            if not settings:
                if profile:
                    raise click.UsageError(
                        f"Profile '{profile}' not found in {config_path()}. "
                        f"Check the profile name or provide --host and {secret_opt}."
                    )
                raise click.UsageError(
                    f"Missing {display} credentials. Provide --host and "
                    f"{secret_opt}, set {host_envvar}/{secret_envvar} environment "
                    f"variables, or add {section_hint} section to {config_path()}."
                )

        resolved_host = host or (settings.get("host") if settings else None)
        resolved_secret = secret or (
            settings.get(secret_config_key) if settings else None
        )

        if not resolved_host:
            raise click.UsageError(
                "Missing host URL (not in CLI, env, or config profile)."
            )
        if not resolved_secret:
            raise click.UsageError(
                f"Missing {secret_label} (not in CLI, env, or config profile)."
            )

        if no_verify_ssl:
            verify_ssl = False
        elif settings:
            verify_ssl = settings.get("verify_ssl", True)
        else:
            verify_ssl = True

        try:
            client = client_factory(
                resolved_host, resolved_secret, verify_ssl, settings or {}
            )
        except Exception as e:
            raise click.ClickException(f"Failed to create {display} client: {e}") from e

        ctx.obj["client"] = client
        return client

    @group.command(help=info_help)
    @click.pass_context
    def info(ctx):
        client = _resolve_client(ctx)

        try:
            server_info = client.info()
        except Exception as e:
            raise click.ClickException(
                f"Failed to fetch {info_error_label} info: {e}"
            ) from e

        info_printer(server_info)

    @group.command(
        help=f"Fetch a single {noun_singular} from {display} and save as a datapackage."
    )
    @click.argument("entity_id", type=int)
    @click.option(
        "--outdir",
        type=click.Path(file_okay=False),
        default=".",
        help="Output directory for the datapackage",
    )
    @click.pass_context
    def fetch(ctx, entity_id, outdir):
        client = _resolve_client(ctx)

        try:
            entry = client.fetch_entry(entity_id)
        except Exception as e:
            raise click.ClickException(
                f"Failed to fetch {noun_singular} {entity_id}: {e}"
            ) from e

        os.makedirs(outdir, exist_ok=True)
        entry.save(outdir=outdir)
        click.echo(f"Saved {noun_singular} {entity_id} to {outdir}")

    @group.command(
        name="export",
        help=f"Fetch multiple {noun_plural} from {display} filtered by tags.",
    )
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
    def export_cmd(ctx, tags, outdir):
        client = _resolve_client(ctx)

        try:
            entries = client.fetch_entries(list(tags) if tags else None)
        except Exception as e:
            raise click.ClickException(f"Failed to fetch {noun_plural}: {e}") from e

        if not entries:
            click.echo(f"No {noun_plural} found matching the specified tags.")
            return

        os.makedirs(outdir, exist_ok=True)
        for entry in entries:
            entry.save(outdir=outdir)

        click.echo(f"Saved {len(entries)} {noun_plural} to {outdir}")

    @group.command(help=f"Upload a local datapackage to {display}.")
    @click.argument("file", type=click.Path(exists=True))
    @click.option(
        "--title",
        type=str,
        default=None,
        help=f"Title for the {display} {noun_singular}",
    )
    @click.option(
        "--tag",
        "tags",
        multiple=True,
        help="Tag to add to the entry (can be specified multiple times)",
    )
    @click.pass_context
    def upload(ctx, file, title, tags):
        from unitpackage.entry import Entry

        client = _resolve_client(ctx)

        try:
            entry = Entry.from_local(file)
        except Exception as e:
            raise click.ClickException(
                f"Failed to load datapackage from {file}: {e}"
            ) from e

        try:
            entity_id = client.upload_entry(
                entry, title=title, tags=list(tags) if tags else None
            )
        except Exception as e:
            raise click.ClickException(
                f"Failed to upload entry to {display}: {e}"
            ) from e

        if entity_id is not None:
            click.echo(f"Uploaded {file} to {display} as {noun_singular} {entity_id}")
        else:
            click.echo(f"Uploaded {file} to {display}")

    return group
