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

# Kadi4Mat Integration

[Kadi4Mat](https://kadi4mat.iam.kit.edu/) is an open-source research data management platform that stores research data as *records*.
The `unitpackage.eln.kadi` module provides a client to exchange unitpackage entries with a Kadi4Mat instance: entries can be fetched from Kadi4Mat as Python objects and uploaded back after analysis.

## Entity Mapping

Kadi4Mat organises data as *records*, each of which can carry file attachments and structured metadata (*extras*).
Each Kadi4Mat record corresponds to one unitpackage `Entry`.
When an entry is uploaded, its tabular data is attached as a CSV file and the complete datapackage descriptor — including field units and metadata — is stored as a nested Kadi4Mat metadatum under the key `unitpackage`.
Tags on the record can be used to group and filter entries.
Only records that carry this `unitpackage` metadatum are recognised by the client; records created outside of unitpackage are ignored.

## Prerequisites

The `kadi-apy` package is required.  Install it alongside unitpackage with:

```sh
pip install "unitpackage[kadi]"
```

You also need a Kadi4Mat **Personal Access Token (PAT)**, which you can create in your Kadi4Mat user settings under *Settings > Access tokens*.
See the [Kadi4Mat documentation](https://kadi4mat.readthedocs.io/) for instructions.

## Configuration

The client resolves credentials in the following priority order:

1. Explicit arguments passed to the constructor
2. Environment variables (`KADI_HOST`, `KADI_PAT`)
3. Configuration file (`~/.config/unitpackage/config.toml`)

### Environment Variables

```sh
export KADI_HOST=https://kadi4mat.example.org
export KADI_PAT=your-personal-access-token
```

Then create a client with:

```python
from unitpackage.eln.kadi import KadiClient

client = KadiClient.from_env()
```

### Configuration File

The configuration file `~/.config/unitpackage/config.toml` stores named connection profiles:

```toml
[kadi]
default_profile = "production"

[kadi.production]
host = "https://kadi4mat.example.org"
pat = "abc123"
verify_ssl = true

[kadi.staging]
host = "https://kadi4mat-staging.example.org"
pat = "def456"
verify_ssl = false
```

Create a client from the default profile:

```python
from unitpackage.eln.kadi import KadiClient

client = KadiClient.from_config()

# Or specify a profile by name
client = KadiClient.from_config("staging")
```

## Python API

### Creating a Client

```python
from unitpackage.eln.kadi import KadiClient

# From explicit credentials
client = KadiClient(
    host="https://kadi4mat.example.org",
    pat="your-personal-access-token",
)

# From environment variables
client = KadiClient.from_env()

# From config file (uses default_profile or the only profile)
client = KadiClient.from_config()
```

### Server Information

```python
info = client.info()
print(info["version"])
```

### Fetching a Single Entry

`fetch_entry` retrieves a Kadi4Mat *record* by its numeric ID and returns a unitpackage `Entry`.
Only records whose extras contain the `unitpackage` metadatum (i.e. records previously uploaded via unitpackage) are supported.

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

`fetch_entries` retrieves all records that carry a `unitpackage` metadatum.
The optional `tags` parameter filters by Kadi4Mat tags (AND logic: all specified tags must be present).

```python
# Fetch all unitpackage-managed records
entries = client.fetch_entries()

# Fetch only records tagged 'electrochemistry'
entries = client.fetch_entries(tags=["electrochemistry"])

# Fetch records with multiple tags
entries = client.fetch_entries(tags=["electrochemistry", "platinum"])

print(f"Found {len(entries)} entries")
```

### Uploading an Entry

`upload_entry` creates a new Kadi4Mat record, uploads the CSV data as a file attachment, and stores the complete datapackage descriptor as a nested metadatum.
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

# Upload to Kadi4Mat
record_id = client.upload_entry(entry, title="CV on Pt(111)", tags=["electrochemistry"])
print(f"Uploaded as record {record_id}")
```

The uploaded record can be fetched back at any time:

```python
entry_restored = client.fetch_entry(record_id)
entry_restored.df
```

## CLI

The `unitpackage kadi` command group provides CLI access to all client operations.
Credentials can be supplied via `--host`/`--pat` options or environment variables.
If neither is provided, the first profile in the configuration file is used.

### Server Information

```sh
unitpackage kadi --host https://kadi4mat.example.org --pat TOKEN info
```

Or with environment variables set:

```sh
unitpackage kadi info
```

### Fetching a Single Entry

Fetch record 42 and save the datapackage to the current directory:

```sh
unitpackage kadi fetch 42
```

Save to a specific output directory:

```sh
unitpackage kadi fetch 42 --outdir my_data/
```

### Exporting Multiple Entries

Export all unitpackage-managed records tagged `electrochemistry`:

```sh
unitpackage kadi export --tag electrochemistry --outdir exported/
```

Multiple tags can be combined (AND logic):

```sh
unitpackage kadi export --tag electrochemistry --tag platinum --outdir exported/
```

### Uploading a Datapackage

Upload a local datapackage JSON file:

```sh
unitpackage kadi upload cv_on_pt.json --title "CV on Pt(111)" --tag electrochemistry
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

# 2. Build the descriptor (what would be stored as a Kadi4Mat metadatum)
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
