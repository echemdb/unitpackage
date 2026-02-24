r"""
CLI commands for managing eLabFTW configuration profiles.

Provides commands to add, list, show, remove, and set the default
eLabFTW connection profile in the unitpackage config file.

EXAMPLES::

    >>> from click.testing import CliRunner
    >>> from unitpackage.eln.elabftw_config_cli import config
    >>> result = CliRunner().invoke(config, ["--help"])
    >>> "add" in result.output
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
import click

from unitpackage.config import (
    config_path,
    get_profile,
    list_profiles,
    load_config,
    save_config,
)

BACKEND = "elabftw"


@click.group()
def config():
    r"""Manage eLabFTW connection profiles."""


@config.command()
@click.argument("profile_name")
@click.option("--host", prompt="eLabFTW host URL", help="eLabFTW server URL")
@click.option("--api-key", prompt="API key", hide_input=True, help="eLabFTW API key")
@click.option(
    "--verify-ssl/--no-verify-ssl",
    default=True,
    help="Whether to verify SSL certificates (default: yes)",
)
@click.option(
    "--set-default/--no-set-default",
    default=False,
    help="Set this profile as the default",
)
def add(profile_name, host, api_key, verify_ssl, set_default):
    r"""Add a new eLabFTW connection profile."""
    cfg = load_config()
    backend = cfg.setdefault(BACKEND, {})

    if profile_name in backend and profile_name != "default_profile":
        raise click.ClickException(
            f"Profile '{profile_name}' already exists. "
            "Remove it first with 'config remove'."
        )

    backend[profile_name] = {
        "host": host,
        "api_key": api_key,
        "verify_ssl": verify_ssl,
    }

    # If this is the first profile or --set-default was given, set as default.
    actual_profiles = [k for k in backend if k != "default_profile"]
    if set_default or len(actual_profiles) == 1:
        backend["default_profile"] = profile_name

    save_config(cfg)
    click.echo(f"Profile '{profile_name}' added to {config_path()}.")
    if backend.get("default_profile") == profile_name:
        click.echo(f"Set '{profile_name}' as the default profile.")


@config.command("list")
def list_cmd():
    r"""List all eLabFTW connection profiles."""
    cfg = load_config()
    profiles = list_profiles(BACKEND, config=cfg)

    if not profiles:
        click.echo("No eLabFTW profiles configured.")
        click.echo("Add one with: unitpackage elabftw config add PROFILE_NAME")
        return

    default = cfg.get(BACKEND, {}).get("default_profile")
    for name in profiles:
        marker = " (default)" if name == default else ""
        profile = cfg[BACKEND][name]
        click.echo(f"  {name}{marker} - {profile.get('host', '?')}")


@config.command()
@click.argument("profile_name")
@click.option(
    "--show-key",
    is_flag=True,
    default=False,
    help="Show the API key in plain text (default: masked)",
)
def show(profile_name, show_key):
    r"""Show details of an eLabFTW connection profile."""
    cfg = load_config()
    profile = get_profile(BACKEND, profile_name, config=cfg)

    if not profile:
        raise click.ClickException(
            f"Profile '{profile_name}' not found. "
            f"Available profiles: {', '.join(list_profiles(BACKEND, config=cfg)) or 'none'}"
        )

    default = cfg.get(BACKEND, {}).get("default_profile")
    is_default = " (default)" if profile_name == default else ""

    click.echo(f"Profile: {profile_name}{is_default}")
    click.echo(f"  host:       {profile.get('host', 'not set')}")

    api_key = profile.get("api_key", "not set")
    if show_key:
        click.echo(f"  api_key:    {api_key}")
    else:
        masked = api_key[:4] + "..." + api_key[-4:] if len(api_key) > 8 else "****"
        click.echo(f"  api_key:    {masked}")

    click.echo(f"  verify_ssl: {profile.get('verify_ssl', True)}")


@config.command()
@click.argument("profile_name")
@click.option("--yes", "-y", is_flag=True, help="Skip confirmation prompt")
def remove(profile_name, yes):
    r"""Remove an eLabFTW connection profile."""
    cfg = load_config()
    backend = cfg.get(BACKEND, {})
    profiles = list_profiles(BACKEND, config=cfg)

    if profile_name not in profiles:
        raise click.ClickException(
            f"Profile '{profile_name}' not found. "
            f"Available profiles: {', '.join(profiles) or 'none'}"
        )

    if not yes:
        click.confirm(f"Remove profile '{profile_name}'?", abort=True)

    del backend[profile_name]

    if backend.get("default_profile") == profile_name:
        del backend["default_profile"]
        click.echo(f"Note: '{profile_name}' was the default profile. Default cleared.")

    save_config(cfg)
    click.echo(f"Profile '{profile_name}' removed.")


@config.command("set-default")
@click.argument("profile_name")
def set_default(profile_name):
    r"""Set the default eLabFTW connection profile."""
    cfg = load_config()
    profiles = list_profiles(BACKEND, config=cfg)

    if profile_name not in profiles:
        raise click.ClickException(
            f"Profile '{profile_name}' not found. "
            f"Available profiles: {', '.join(profiles) or 'none'}"
        )

    cfg[BACKEND]["default_profile"] = profile_name
    save_config(cfg)
    click.echo(f"Default profile set to '{profile_name}'.")
