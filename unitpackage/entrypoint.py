r"""
The echemdb-converter suite.

EXAMPLES::

    >>> from unitpackage.test.cli import invoke
    >>> invoke(cli, "--help")  # doctest: +NORMALIZE_WHITESPACE
    Usage: cli [OPTIONS] COMMAND [ARGS]...

      The echemdb-converter suite

    Options:
      --help  Show this message and exit.
    Commands:
      csv  Convert a file containing CSV data into an echemdb unitpackage.
      ec   Convert an electrochemistry file into an echemdb datapackage.

"""

# ********************************************************************
#  This file is part of unitpackage.
#
#        Copyright (C) 2024-2025 Albert Engstfeld
#        Copyright (C)      2022 Johannes Hermann
#        Copyright (C) 2022-2025 Julian Rüth
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
from pathlib import Path

import click

from unitpackage.entry import Entry

logger = logging.getLogger("unitpackage")


@click.group(help=__doc__.split("EXAMPLES")[0])
def cli():
    r"""
    Entry point of the command line interface.

    This redirects to the individual commands listed below.
    """


@click.command(name="csv")
@click.argument("csv", type=click.Path(exists=True))
@click.option("--device", type=str, default=None, help="selects a specific CSVloader")
@click.option(
    "--outdir",
    type=click.Path(file_okay=False),
    default=".",
    help="write output files to this directory",
)
@click.option(
    "--metadata", type=click.File("rb"), default=None, help="yaml file with metadata"
)
def convert(csv, device, outdir, metadata):
    """
    Convert a file containing CSV data into an echemdb unitpackage.
    \f

    EXAMPLES::

        >>> import os.path
        >>> from unitpackage.test.cli import invoke, TemporaryData
        >>> with TemporaryData("../**/default.csv") as directory:
        ...     invoke(cli, "csv", os.path.join(directory, "default.csv"), "--outdir", "test/generated/loaders/")

    TESTS:

    The command can be invoked on files in the current directory::

        >>> from unitpackage.test.cli import invoke, TemporaryData
        >>> cwd = os.getcwd()
        >>> with TemporaryData("../**/default.csv") as directory:
        ...     os.chdir(directory)
        ...     try:
        ...         invoke(cli, "csv", "default.csv", "--outdir", "test/generated/loaders/")
        ...     finally:
        ...         os.chdir(cwd)

    """
    import yaml

    from unitpackage.loaders.baseloader import BaseLoader

    fields = None

    if metadata:
        metadata = yaml.load(metadata, Loader=yaml.SafeLoader)
        try:
            fields = metadata["figure description"]["fields"]
        except (KeyError, AttributeError):
            logger.warning("No units to the fields provided in the metadata")

    if device:
        with open(csv, "r") as file:  # pylint: disable=unspecified-encoding
            loader = BaseLoader.create(device)(file)
    else:
        with open(csv, "r") as file:  # pylint: disable=unspecified-encoding
            loader = BaseLoader(file)

    entry = Entry.from_df(
        df=loader.df, basename=Path(csv).stem, metadata=metadata, fields=fields
    )
    entry.save(outdir=outdir)


cli.add_command(convert)


# Register command docstrings for doctesting.
# Since commands are not functions anymore due to their decorator, their
# docstrings would otherwise be ignored.
__test__ = {
    name: command.__doc__ for (name, command) in cli.commands.items() if command.__doc__
}
