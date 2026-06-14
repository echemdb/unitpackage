r"""
Shared Click command factory for ELN connection-profile management CLIs.

Both the eLabFTW and Kadi4Mat ``config`` subgroups manage connection profiles
in the unitpackage config file identically, differing only in the backend key,
display name, and the name of the secret credential (``api_key`` vs ``pat``).

:func:`make_config_group` builds the ``add`` / ``list`` / ``show`` / ``remove``
/ ``set-default`` subgroup from those few parameters.

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
import click

from unitpackage.config import (
    config_path,
    get_profile,
    list_profiles,
    load_config,
    save_config,
)


def make_config_group(  # pylint: disable=too-many-statements
    *,
    backend,
    display,
    secret_opt,
    secret_field,
    secret_label,
):
    r"""
    Build and return the ``config`` Click ``Group`` for an ELN backend.

    Parameters:

    - ``backend`` --- config-file section key (e.g. ``"elabftw"``), also used
      in command examples (``unitpackage <backend> config add ...``).
    - ``display`` --- human-readable backend name (e.g. ``"eLabFTW"``).
    - ``secret_opt`` --- credential option flag (e.g. ``"--api-key"``).
    - ``secret_field`` --- config-file key for the secret (e.g. ``"api_key"``).
    - ``secret_label`` --- human-readable secret name used in prompts and help
      (e.g. ``"API key"``).

    """

    @click.group(name="config", help=f"Manage {display} connection profiles.")
    def config():
        pass

    @config.command(help=f"Add a new {display} connection profile.")
    @click.argument("profile_name")
    @click.option("--host", prompt=f"{display} host URL", help=f"{display} server URL")
    @click.option(
        secret_opt,
        "secret",
        prompt=secret_label,
        hide_input=True,
        help=f"{display} {secret_label}",
    )
    @click.option(
        "--verify-ssl/--no-verify-ssl",
        default=True,
        help="Whether to verify SSL certificates (default: yes)",
    )
    @click.option(
        "--set-default/--no-set-default",
        "set_as_default",
        default=False,
        help="Set this profile as the default",
    )
    def add(profile_name, host, secret, verify_ssl, set_as_default):
        cfg = load_config()
        section = cfg.setdefault(backend, {})

        if profile_name in section and profile_name != "default_profile":
            raise click.ClickException(
                f"Profile '{profile_name}' already exists. "
                "Remove it first with 'config remove'."
            )

        section[profile_name] = {
            "host": host,
            secret_field: secret,
            "verify_ssl": verify_ssl,
        }

        # If this is the first profile or --set-default was given, set as default.
        actual_profiles = [k for k in section if k != "default_profile"]
        if set_as_default or len(actual_profiles) == 1:
            section["default_profile"] = profile_name

        save_config(cfg)
        click.echo(f"Profile '{profile_name}' added to {config_path()}.")
        if section.get("default_profile") == profile_name:
            click.echo(f"Set '{profile_name}' as the default profile.")

    @config.command("list", help=f"List all {display} connection profiles.")
    def list_cmd():
        cfg = load_config()
        profiles = list_profiles(backend, config=cfg)

        if not profiles:
            click.echo(f"No {display} profiles configured.")
            click.echo(f"Add one with: unitpackage {backend} config add PROFILE_NAME")
            return

        default = cfg.get(backend, {}).get("default_profile")
        for name in profiles:
            marker = " (default)" if name == default else ""
            profile = cfg[backend][name]
            click.echo(f"  {name}{marker} - {profile.get('host', '?')}")

    @config.command(help=f"Show details of a {display} connection profile.")
    @click.argument("profile_name")
    @click.option(
        "--show-key",
        is_flag=True,
        default=False,
        help=f"Show the {secret_label} in plain text (default: masked)",
    )
    def show(profile_name, show_key):
        cfg = load_config()
        profile = get_profile(backend, profile_name, config=cfg)

        if not profile:
            raise click.ClickException(
                f"Profile '{profile_name}' not found. "
                f"Available profiles: {', '.join(list_profiles(backend, config=cfg)) or 'none'}"
            )

        default = cfg.get(backend, {}).get("default_profile")
        is_default = " (default)" if profile_name == default else ""

        click.echo(f"Profile: {profile_name}{is_default}")
        click.echo(f"  host:       {profile.get('host', 'not set')}")

        secret = profile.get(secret_field, "not set")
        if show_key:
            click.echo(f"  {secret_field}:    {secret}")
        else:
            # Reveal only a short prefix for recognition; never the tail, so the
            # masked form leaks as little of the secret as possible.
            masked = secret[:4] + "..." if len(secret) > 4 else "****"
            click.echo(f"  {secret_field}:    {masked}")

        click.echo(f"  verify_ssl: {profile.get('verify_ssl', True)}")

    @config.command(help=f"Remove a {display} connection profile.")
    @click.argument("profile_name")
    @click.option("--yes", "-y", is_flag=True, help="Skip confirmation prompt")
    def remove(profile_name, yes):
        cfg = load_config()
        section = cfg.get(backend, {})
        profiles = list_profiles(backend, config=cfg)

        if profile_name not in profiles:
            raise click.ClickException(
                f"Profile '{profile_name}' not found. "
                f"Available profiles: {', '.join(profiles) or 'none'}"
            )

        if not yes:
            click.confirm(f"Remove profile '{profile_name}'?", abort=True)

        del section[profile_name]

        if section.get("default_profile") == profile_name:
            del section["default_profile"]
            click.echo(
                f"Note: '{profile_name}' was the default profile. Default cleared."
            )

        save_config(cfg)
        click.echo(f"Profile '{profile_name}' removed.")

    @config.command(
        "set-default", help=f"Set the default {display} connection profile."
    )
    @click.argument("profile_name")
    def set_default(profile_name):
        cfg = load_config()
        profiles = list_profiles(backend, config=cfg)

        if profile_name not in profiles:
            raise click.ClickException(
                f"Profile '{profile_name}' not found. "
                f"Available profiles: {', '.join(profiles) or 'none'}"
            )

        cfg[backend]["default_profile"] = profile_name
        save_config(cfg)
        click.echo(f"Default profile set to '{profile_name}'.")

    return config
