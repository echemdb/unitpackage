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

# eLabFTW Integration

[eLabFTW](https://www.elabftw.net/) is an open-source electronic lab notebook (ELN) that stores experiments and resources online.
The `unitpackage.eln.elabftw` module provides a client to exchange unitpackage entries with an eLabFTW instance: entries can be fetched from eLabFTW as Python objects and uploaded back after analysis.

## Entity Mapping

eLabFTW organises data as *items* (resources) and *experiments*.
The unitpackage integration works with **items** exclusively: each eLabFTW item corresponds to one unitpackage `Entry`.
When an entry is uploaded, its tabular data is attached as a CSV file and the complete datapackage descriptor — including field units and metadata — is stored in the item's metadata field under the key `unitpackage`.
Tags on the item can be used to group and filter entries.
Only items that carry this `unitpackage` metadata key are recognised by the client; items created outside of unitpackage are ignored.

## Prerequisites

The `elabapi-python` package is required.  Install it alongside unitpackage with:

```sh
pip install "unitpackage[elabftw]"
```

You also need an eLabFTW **API key**, which you can generate in your eLabFTW user settings under *API Keys*.
See the [eLabFTW API documentation](https://doc.elabftw.net/docs/usage/api/) for instructions.

## Configuration

The client resolves credentials in the following priority order:

1. Explicit arguments passed to the constructor
2. Environment variables (`ELABFTW_HOST`, `ELABFTW_API_KEY`)
3. Configuration file (`~/.config/unitpackage/config.toml` on Linux/macOS, `%APPDATA%\unitpackage\config.toml` on Windows)

### Environment Variables

```sh
export ELABFTW_HOST=https://eln.example.org
export ELABFTW_API_KEY=your-api-key
```

Then create a client with:

```python
from unitpackage.eln.elabftw import ElabFTWClient

client = ElabFTWClient.from_env()
```

### Configuration File

The configuration file `~/.config/unitpackage/config.toml` stores named connection profiles:

```toml
[elabftw]
default_profile = "production"

[elabftw.production]
host = "https://eln.example.org"
api_key = "abc123"
verify_ssl = true

[elabftw.staging]
host = "https://staging-eln.example.org"
api_key = "def456"
verify_ssl = false
```

Profiles are managed with the CLI:

```sh
# Add a new profile (prompts for host and API key)
unitpackage elabftw config add production

# List all profiles
unitpackage elabftw config list

# Show details of a profile
unitpackage elabftw config show production

# Set a different default
unitpackage elabftw config set-default staging

# Remove a profile
unitpackage elabftw config remove staging
```

Create a client from the default profile:

```python
from unitpackage.eln.elabftw import ElabFTWClient

client = ElabFTWClient.from_config()

# Or specify a profile by name
client = ElabFTWClient.from_config("staging")
```

## Python API

### Creating a Client

```python
from unitpackage.eln.elabftw import ElabFTWClient

# From explicit credentials
client = ElabFTWClient(
    host="https://eln.example.org",
    api_key="your-api-key",
)

# From environment variables
client = ElabFTWClient.from_env()

# From config file (uses default_profile or the only profile)
client = ElabFTWClient.from_config()
```

### Server Information

```python
info = client.info()
print(info["elabftw_version"])
```

### Fetching a Single Entry

`fetch_entry` retrieves an eLabFTW *item* by its numeric ID and returns a unitpackage `Entry`.
Only items whose metadata contains the `unitpackage` key (i.e. items previously uploaded via unitpackage) are supported.

```python
entry = client.fetch_entry(42)

# Access the tabular data as a pandas DataFrame
entry.df.head()

# Access metadata
entry.metadata
```

After fetching, the entry behaves exactly like any other unitpackage entry:

```python
# Rescale columns
rescaled = entry.rescale({"E": "mV"})

# Save to disk as a datapackage
entry.save(outdir="my_data/")
```

### Fetching Multiple Entries

`fetch_entries` retrieves all items that have unitpackage metadata.
The optional `tags` parameter filters by eLabFTW tags (AND logic: all specified tags must be present).

```python
# Fetch all unitpackage-managed items
entries = client.fetch_entries()

# Fetch only items tagged 'electrochemistry'
entries = client.fetch_entries(tags=["electrochemistry"])

# Fetch items with multiple tags
entries = client.fetch_entries(tags=["electrochemistry", "platinum"])

print(f"Found {len(entries)} entries")
```

### Uploading an Entry

`upload_entry` creates a new eLabFTW item, uploads the CSV data as an attachment, and stores the complete datapackage descriptor in the item's metadata.
This enables a lossless round-trip: any entry uploaded this way can be fetched back with `fetch_entry`.

```python
import pandas as pd
from unitpackage.entry import Entry

# Create or load an entry
df = pd.DataFrame({"t": [0, 1, 2], "E": [0.1, 0.2, 0.3]})
entry = Entry.from_df(df=df, basename="cv_on_pt")
entry = entry.update_fields([
    {"name": "t", "unit": "s"},
    {"name": "E", "unit": "V"},
])

# Upload to eLabFTW
entity_id = client.upload_entry(entry, title="CV on Pt(111)", tags=["electrochemistry"])
print(f"Uploaded as item {entity_id}")
```

The uploaded item can be fetched back at any time:

```python
entry_restored = client.fetch_entry(entity_id)
entry_restored.df
```

## CLI

The `unitpackage elabftw` command group provides CLI access to all client operations.
Credentials can be supplied via `--host`/`--api-key` options, environment variables, or the configuration file.

### Server Information

```sh
unitpackage elabftw --host https://eln.example.org --api-key KEY info
```

Or with a configured profile:

```sh
unitpackage elabftw info
```

### Fetching a Single Entry

Fetch item 42 and save the datapackage to the current directory:

```sh
unitpackage elabftw fetch 42
```

Save to a specific output directory:

```sh
unitpackage elabftw fetch 42 --outdir my_data/
```

### Exporting Multiple Entries

Export all unitpackage-managed items tagged `electrochemistry`:

```sh
unitpackage elabftw export --tag electrochemistry --outdir exported/
```

Multiple tags can be combined (AND logic):

```sh
unitpackage elabftw export --tag electrochemistry --tag platinum --outdir exported/
```

### Uploading a Datapackage

Upload a local datapackage JSON file:

```sh
unitpackage elabftw upload cv_on_pt.json --title "CV on Pt(111)" --tag electrochemistry
```

### Managing Connection Profiles

```sh
# Interactive setup (prompts for host and API key)
unitpackage elabftw config add mylab

# List all configured profiles
unitpackage elabftw config list

# Show a profile (API key is masked by default)
unitpackage elabftw config show mylab

# Show the API key in plain text
unitpackage elabftw config show mylab --show-key

# Change the default profile
unitpackage elabftw config set-default mylab

# Remove a profile
unitpackage elabftw config remove mylab --yes
```

## Round-Trip Workflow

A typical round-trip workflow looks like this:

```{code-cell} ipython3
:tags: [hide-input]

# Demonstrate the in-memory part of a round-trip without a live ELN
import pandas as pd
from unitpackage.entry import Entry
from unitpackage.eln import build_datapackage_descriptor, apply_datapackage_descriptor
import json

# 1. Create an entry
df = pd.DataFrame({"t": [0.0, 1.0, 2.0], "E": [0.1, 0.2, 0.15]})
entry = Entry.from_df(df=df, basename="cv_demo")
entry = entry.update_fields([
    {"name": "t", "unit": "s"},
    {"name": "E", "unit": "V"},
])

# 2. Build the descriptor (what would be stored in eLabFTW metadata)
descriptor = build_datapackage_descriptor(entry)
print("Descriptor keys:", list(descriptor.keys()))
print("Resource name:", descriptor["resources"][0]["name"])
print("Fields:", [f["name"] for f in descriptor["resources"][0]["schema"]["fields"]])
```

```{code-cell} ipython3
:tags: [hide-input]

# 3. Simulate what fetch_entry does: restore from stored descriptor
entry_restored = Entry.from_df(df=df, basename="cv_demo")
entry_restored = apply_datapackage_descriptor(entry_restored, json.dumps(descriptor))

# Field units are preserved
entry_restored.field_unit("t"), entry_restored.field_unit("E")
```