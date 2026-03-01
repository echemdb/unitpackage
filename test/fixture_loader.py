"""
Utilities for loading recorded ELN API fixtures into Mock objects.

Provides helper functions that read fixture JSON files produced by
``record_fixtures.py`` and construct ``unittest.mock.Mock`` objects
for use in ``test_elabftw.py`` and ``test_kadi.py``.

Typical usage in tests::

    from test.fixture_loader import get_versions, load_fixture

    @pytest.fixture(params=get_versions("elabftw"))
    def elabftw_version(request):
        return request.param

    def test_with_recorded_data(elabftw_version):
        csv_data = get_csv_bytes("elabftw", elabftw_version)
        ...

"""

import base64
import json
from pathlib import Path
from unittest.mock import Mock

FIXTURES_DIR = Path(__file__).parent / "fixtures"


def get_versions(backend="elabftw"):
    """
    Return a sorted list of recorded version strings.

    Returns
    -------
    list of str
        Version strings (e.g., ``["5.4.1"]``), sorted ascending.

    """
    backend_dir = FIXTURES_DIR / backend
    if not backend_dir.is_dir():
        return []
    return [
        p.name
        for p in sorted(backend_dir.iterdir())
        if p.is_dir() and not p.name.startswith(".")
    ]


def get_latest_version(backend="elabftw"):
    """
    Return the most recent recorded version string.

    Returns ``None`` if no fixtures exist.
    """
    versions = get_versions(backend)
    return versions[-1] if versions else None


def load_fixture(backend, version, operation):
    """
    Load a single fixture JSON file and return its contents as a dict.

    Parameters
    ----------
    backend : str
        The backend name (``"elabftw"``).
    version : str
        The ELN version string (directory name under the backend).
    operation : str
        The operation name (filename without ``.json``), e.g.,
        ``"info"``, ``"patch_metadata"``, ``"list_uploads"``.

    Returns
    -------
    dict
        The parsed JSON contents.

    Raises
    ------
    FileNotFoundError
        If the fixture file does not exist.

    """
    path = FIXTURES_DIR / backend / version / f"{operation}.json"
    with open(path, encoding="utf-8") as fh:
        return json.load(fh)


def load_manifest(backend, version):
    """Load the ``manifest.json`` for a given backend and version."""
    return load_fixture(backend, version, "manifest")


def get_csv_bytes(backend="elabftw", version=None):
    """
    Return the recorded CSV data as ``bytes``.

    Decodes the base64-encoded CSV content from the ``download_csv.json``
    fixture file.

    Parameters
    ----------
    backend : str
        The backend name (``"elabftw"``).
    version : str or None
        The ELN version string.  If ``None``, uses the latest version.

    Returns
    -------
    bytes
        The raw CSV file content.

    """
    version = version or get_latest_version(backend)
    if version is None:
        raise FileNotFoundError(f"No fixtures found for backend '{backend}'")
    data = load_fixture(backend, version, "download_csv")
    response = data.get("response", {})
    b64 = response.get("data_base64")
    if b64:
        return base64.b64decode(b64)
    return response.get("data", b"").encode("utf-8") if isinstance(response.get("data"), str) else b""


def make_mock_uploads(backend="elabftw", version=None):
    """
    Build a list of ``Mock`` upload objects from the recorded
    ``list_uploads.json`` fixture.

    Parameters
    ----------
    backend : str
        The backend name (``"elabftw"``).
    version : str or None
        The ELN version string.  If ``None``, uses the latest version.

    Returns
    -------
    list of unittest.mock.Mock

    """
    version = version or get_latest_version(backend)
    if version is None:
        raise FileNotFoundError(f"No fixtures found for backend '{backend}'")

    data = load_fixture(backend, version, "list_uploads")
    response = data.get("response", [])

    if not isinstance(response, list):
        response = [response]

    mocks = []
    for item in response:
        upload = Mock()
        for key, value in item.items():
            setattr(upload, key, value)
        mocks.append(upload)

    return mocks


def make_mock_kadi_record(version, csv_bytes, backend="kadi"):
    """
    Build a ``Mock`` Kadi4Mat record from recorded fixture data.

    Wires up ``get_filelist()`` from ``list_uploads.json`` and
    ``download_file()`` to write *csv_bytes* to the requested path,
    mirroring the behaviour of a real ``kadi_apy`` record object.

    Parameters
    ----------
    version : str
        The Kadi4Mat version string (directory name under the backend).
    csv_bytes : bytes
        Raw CSV content written by the ``download_file`` mock.
    backend : str
        The backend name (default ``"kadi"``).

    Returns
    -------
    unittest.mock.Mock

    """
    entity_data = load_fixture(backend, version, "get_entity")
    response = entity_data["response"]

    uploads_data = load_fixture(backend, version, "list_uploads")
    filelist_response = uploads_data["response"]

    record = Mock()
    record.id = response["id"]
    record.title = response["title"]
    record.identifier = response["identifier"]
    record.meta = response

    filelist_mock = Mock()
    filelist_mock.json.return_value = filelist_response
    record.get_filelist.return_value = filelist_mock

    def _download(file_id, file_path):
        with open(file_path, "wb") as fh:
            fh.write(csv_bytes)

    record.download_file = _download
    return record


def make_field_dict(entry):
    """
    Return a ``{name: field_descriptor}`` dict for an Entry's fields.

    Works with both frictionless ``Field`` objects (which have
    ``.to_dict()``) and plain dicts.

    Parameters
    ----------
    entry : unitpackage.entry.Entry

    Returns
    -------
    dict

    """
    def _as_dict(f):
        return f.to_dict() if hasattr(f, "to_dict") else f

    return {_as_dict(f)["name"]: _as_dict(f) for f in entry.fields}
