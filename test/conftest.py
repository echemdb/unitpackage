"""
Pytest configuration for ELN integration tests.

Registers custom markers so tests can be selected/deselected
via ``pytest -m elabftw``.
"""

import sys
from unittest.mock import MagicMock

import pytest


def pytest_configure(config):
    config.addinivalue_line(
        "markers",
        "elabftw: marks tests for the eLabFTW integration module",
    )


# ---------------------------------------------------------------------------
# Provide a fake elabapi_python module so tests can run without the real
# package installed.  The fake module is injected into sys.modules before any
# test imports unitpackage.elabftw.
# ---------------------------------------------------------------------------

_fake_elabapi = MagicMock()
# Ensure commonly accessed classes are stable Mock objects
_fake_elabapi.Configuration = MagicMock
_fake_elabapi.ApiClient = MagicMock
_fake_elabapi.InfoApi = MagicMock
_fake_elabapi.ExperimentsApi = MagicMock
_fake_elabapi.ItemsApi = MagicMock
_fake_elabapi.UploadsApi = MagicMock
# Set __spec__ so importlib.util.find_spec() works
_fake_elabapi.__spec__ = MagicMock()

sys.modules.setdefault("elabapi_python", _fake_elabapi)
