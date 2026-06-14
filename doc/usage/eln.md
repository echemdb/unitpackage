---
jupytext:
  formats: ipynb,md:myst
  text_representation:
    extension: .md
    format_name: myst
    format_version: 0.13
    jupytext_version: 1.16.6
kernelspec:
  display_name: Python 3 (ipykernel)
  language: python
  name: python3
---

# Electronic Lab Notebook (ELN) Integration

unitpackage can exchange entries with **Electronic Lab Notebooks (ELNs)** and research data management platforms.
Each integration provides a client class with a consistent interface for fetching, uploading, and managing unitpackage entries stored in the respective system.

Supported backends:

- [eLabFTW](elabftw.md) — open-source ELN; entries are stored as *items*
- [Kadi4Mat](kadi.md) — open-source research data management platform; entries are stored as *records*

## How It Works

Each ELN backend maps a unitpackage `Entry` to a native entity (item or record) in the target system.
When an entry is uploaded:

1. The tabular data is attached as a **CSV file**.
2. The complete datapackage descriptor — including field units and metadata — is stored as structured metadata under the key `unitpackage`.

Only entities that carry this `unitpackage` metadata key are recognised by the client; entities created outside of unitpackage are ignored.
Tags on the entity can be used to group and filter entries.

This design enables a **lossless round-trip**: any entry uploaded via unitpackage can be fetched back with all units and metadata intact.

## Installation

Each backend requires an optional dependency.
Install the one you need:

```sh
# eLabFTW
pip install "unitpackage[elabftw]"

# Kadi4Mat
pip install "unitpackage[kadi]"
```

## Configuration

All backends share the same configuration file at
`~/.config/unitpackage/config.toml` (Linux/macOS) or
`%APPDATA%\unitpackage\config.toml` (Windows).

Each backend has its own section, and each section can hold multiple named **connection profiles**
(shown here for `<eln>` = `elabftw` or `kadi`):

```toml
[<eln>]
default_profile = "production"

[<eln>.production]
host = "https://eln.example.org"
api_key = "abc123"          # elabftw: api_key, kadi: pat
verify_ssl = true
```

Profiles are managed with the CLI:

```sh
unitpackage <eln> config add production
unitpackage <eln> config list
```

Credentials can also be supplied via **environment variables** or passed directly to the client constructor.
The priority order is: constructor arguments > environment variables > configuration file.

| Backend  | Environment variables              | Auth type           |
|----------|------------------------------------|---------------------|
| eLabFTW  | `ELABFTW_HOST`, `ELABFTW_API_KEY`  | API key             |
| Kadi4Mat | `KADI_HOST`, `KADI_PAT`            | Personal access token |

## Common Python API

All clients share the same three core operations.
In the examples below, replace `<ELNClient>` with `ElabFTWClient` (from `unitpackage.eln.elabftw`)
or `KadiClient` (from `unitpackage.eln.kadi`).

### Creating a Client

```python
client = <ELNClient>.from_config()   # from config file
client = <ELNClient>.from_env()      # from environment variables
```

### Fetching Entries

```python
# Single entry by numeric ID
entry = client.fetch_entry(42)

# All unitpackage-managed entries
entries = client.fetch_entries()

# Filter by tags (AND logic)
entries = client.fetch_entries(tags=["electrochemistry", "platinum"])
```

The returned `Entry` objects behave exactly like any other unitpackage entry:

```python
entry.df.head()                      # tabular data as a DataFrame
entry.field_unit("E")                # unit of a column
entry.rescale({"E": "mV"})           # rescale to different units
entry.save(outdir="my_data/")        # save to disk
```

### Uploading an Entry

```python
import pandas as pd
from unitpackage.entry import Entry

df = pd.DataFrame({"t": [0, 1, 2], "E": [0.1, 0.2, 0.3]})
entry = Entry.from_df(df=df, basename="cv_on_pt")
entry = entry.update_fields([
    {"name": "t", "unit": "s"},
    {"name": "E", "unit": "V"},
])

entity_id = client.upload_entry(entry, title="CV on Pt(111)", tags=["electrochemistry"])
```

## Common CLI

Both backends expose the same subcommands under `unitpackage <eln>` (`elabftw` or `kadi`):

```sh
# Check server connectivity
unitpackage <eln> info

# Fetch a single entry by ID and save to disk
unitpackage <eln> fetch 42 --outdir my_data/

# Export all tagged entries
unitpackage <eln> export --tag electrochemistry --outdir exported/

# Upload a local datapackage JSON
unitpackage <eln> upload cv_on_pt.json --title "CV on Pt(111)" --tag electrochemistry
```

## Backend-Specific Documentation

For authentication details, advanced configuration options, and backend-specific behaviour, see:

- [eLabFTW Integration](elabftw.md)
- [Kadi4Mat Integration](kadi.md)

```{toctree}
:hidden:
elabftw.md
kadi.md
```
