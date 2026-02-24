"""
Root-level pytest configuration.

Skips doctest collection for optional ELN backend modules whose
dependencies are not installed.  The ``test/conftest.py`` provides
mock modules and markers for the unit tests in ``test/``.
"""
import importlib
import os

import pandas as pd

# ---------------------------------------------------------------------------
# Skip doctest collection for optional ELN modules whose dependencies
# are not installed (they cannot be imported by --doctest-modules).
# ---------------------------------------------------------------------------

collect_ignore_glob = []

if importlib.util.find_spec("elabapi_python") is None:
    collect_ignore_glob.extend([
        "unitpackage/eln/elabftw.py",
        "unitpackage/eln/elabftw_cli.py",
    ])


def pytest_configure():
    """Configure pandas display options for doctests.

    Controls DataFrame output formatting to produce consistent,
    truncated output with ellipsis in doctests.
    """
    os.environ.setdefault("COLUMNS", "100")

    # Terminal width for DataFrame display (in characters)
    width = int(os.environ.get("PANDAS_DISPLAY_WIDTH", 100))
    pd.set_option("display.width", width)

    # Number of columns to show before truncating with ellipsis
    max_cols = int(os.environ.get("PANDAS_MAX_COLUMNS", 6))
    pd.set_option("display.max_columns", max_cols)

    # Number of rows to display
    max_rows = int(os.environ.get("PANDAS_MAX_ROWS", 4))
    pd.set_option("display.max_rows", max_rows)

    # Don't expand DataFrame repr across multiple lines
    pd.set_option("display.expand_frame_repr", False)

    # Show summary info line if truncated (e.g., "[2 rows x 11 columns]")
    pd.set_option("display.show_dimensions", "truncate")
