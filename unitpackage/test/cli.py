r"""
Helpers for click CLI testing.

Click's own CliRunner is quite cumbersome to work with in some simple test
scenarios so we wrap it in more convenient ways here.

The code has been adapted from https://github.com/echemdb/svgdigitizer/.

"""

# *********************************************************************
#  This file is part of unitpackage.
#
#        Copyright (C) 2024-2025 Albert Engstfeld
#        Copyright (C) 2021-2024 Julian Rüth
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
# *********************************************************************

import pytest


def invoke(command, *args):
    r"""
    Invoke the click ``command`` with the given list of string arguments.

    >>> import click
    >>> @click.command()
    ... def hello(): print("Hello World")
    >>> invoke(hello)
    Hello World

    >>> @click.command()
    ... def fails(): raise Exception("expected error")
    >>> invoke(fails)
    Traceback (most recent call last):
    ...
    Exception: expected error

    """
    from click.testing import CliRunner

    invocation = CliRunner().invoke(command, args, catch_exceptions=False)
    output = invocation.output.strip()
    if output:
        print(output)


class TemporaryData:
    r"""
    Provides a temporary directory with test files.

    EXAMPLES::

        >>> import os
        >>> with TemporaryData("unit.*") as directory:
        ...     'unit.csv' in os.listdir(directory)
        True

    """

    def __init__(self, *patterns):
        self._patterns = patterns
        self._tmpdir = None

    def __enter__(self):
        import tempfile

        self._tmpdir = tempfile.TemporaryDirectory()

        try:
            import glob
            import os
            import os.path
            import shutil

            import unitpackage

            cwd = os.getcwd()
            os.chdir(
                os.path.join(
                    os.path.dirname(unitpackage.__file__), "..", "test", "loader_data"
                )
            )
            try:
                for pattern in self._patterns:
                    for filename in glob.glob(pattern):
                        shutil.copy(filename, self._tmpdir.name)

                return self._tmpdir.name
            finally:
                os.chdir(cwd)

        except Exception:
            self._tmpdir.cleanup()
            raise

    def __exit__(self, *args):
        self._tmpdir.__exit__(*args)


@pytest.mark.parametrize(
    "name,args",
    [
        (  # "Standard" CSV with a single column header line.
            "default",
            ["csv", "default.csv"],
        ),
        (  # "Standard" CSV for which the units to the columns are included in an additional metadata file.
            "unit",
            ["csv", "unit.csv", "--metadata", "unit.csv.metadata"],
        ),
        (  # Biologic EClab file for cyclic voltammetry (using `,` as decimal separator)
            "eclab_cv",
            [
                "csv",
                "eclab_cv.mpt",
                "--metadata",
                "eclab_cv.mpt.metadata",
                "--device",
                "eclab",
            ],
        ),
        (  # Biologic EClab file for chronoamperrometry or chronopotentiometry (using `,` as decimal separator)
            "eclab_ca",
            [
                "csv",
                "eclab_ca.mpt",
                "--metadata",
                "eclab_ca.mpt.metadata",
                "--device",
                "eclab",
            ],
        ),
        (  # Gamry Instruments Framework software file for cyclic voltammetry
            "gamry_cv",
            [
                "csv",
                "gamry_cv.DTA",
                "--metadata",
                "gamry_cv.DTA.metadata",
                "--device",
                "gamry",
            ],
        ),
    ],
)
def test_csv(name, args):
    r"""
    Test that the csv command from the command line interface works correctly.

    This function is executed by pytest and checks that "csv" produces JSON and
    CSV files that match expected outputs.
    """
    import os

    cwd = os.getcwd()
    with TemporaryData(f"{name}.*") as workdir:
        os.chdir(workdir)
        try:
            from unitpackage.entrypoint import cli

            invoke(cli, *args, "--outdir", "outdir")

            import json

            with open(f"outdir/{name}.json", encoding="ASCII") as actual:
                with open(f"{name}.json.expected", encoding="ASCII") as expected:
                    assert json.load(actual) == json.load(expected)

            import pandas
            import pandas.testing

            pandas.testing.assert_frame_equal(
                pandas.read_csv(f"outdir/{name}.csv"),
                pandas.read_csv(f"{name}.csv.expected"),
            )
        finally:
            os.chdir(cwd)
