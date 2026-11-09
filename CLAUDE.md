# Instructions for Claude — unitpackage

Python library to create, interact with, and store collections of
[frictionless Data Packages](https://frictionlessdata.io/) whose tabular
resources carry **unit-aware field metadata**. Each Data Package pairs a CSV
file with a JSON descriptor (schema: column names, types, units) plus arbitrary
nested metadata. The unit-aware Data Package this library produces is a
**Unit Package**; `unitpackage` (backticked) refers to the module itself. Part
of the [echemdb](https://www.echemdb.org) community.

There is no `CONTRIBUTING.md`; installation is described in
`doc/installation.md`, and the workflow essentials are in the sections below.

## Keep the repository clean

- Do what the user asked and nothing more. No extra files, helper scripts,
  summaries or comments that the request did not call for.
- Files and text written by Claude are committed only if they document the
  **current state** of the project (code, docstrings, user docs, news entry).
  Session notes, design discussions and rejected alternatives belong in the
  related GitHub issue or PR comments, not in the repository.
- Scratch notebooks, CSVs or JSON files created while exploring go to a
  temporary directory, never the repository root.
- Keep each branch to one concern. If a request covers several independent
  changes, propose one branch per change.

## Git and GitHub

- Before answering questions about the current state of the repository (recent
  changes, what is merged, what is outdated), run `git fetch origin` and
  compare against `origin/main`. The local `main` and the current branch may be
  behind or already merged.
- Start new branches from `origin/main`.
- Never `git commit`, `git push`, or create, edit or comment on issues and PRs
  without showing exactly what will happen and getting an explicit "yes".
  Approval for one step does not cover the next.
- Every user-visible change needs a news fragment in `doc/news/` (copy
  `doc/news/TEMPLATE.rst`, keep only the relevant sections).

## Architecture

Core abstractions (generic, domain-agnostic):

- `unitpackage/collection.py` — `Collection`: a set of frictionless Resources.
  Construct with `Collection.from_local(dir)` / `Collection.from_remote()`.
  Supports filtering, slicing, iteration, and `rescale()`.
- `unitpackage/entry.py` — `Entry`: a single tabular Resource = CSV data +
  unit-aware fields + metadata. Exposes `.df` (pandas), `.field_unit()`,
  `.rescale()`, `.plot()`, and many `from_*` / `create_*` constructors.
- `unitpackage/descriptor.py` — `Descriptor()` factory wrapping nested
  JSON/dict metadata for attribute-style access + YAML dump.
  `QuantityDescriptor` adds astropy `.quantity` for `{value, unit}` dicts.
- `unitpackage/metadata.py` — `MetadataDescriptor`: dict + attribute access to
  an Entry's metadata; loaders for YAML/JSON/dict.
- `unitpackage/local.py` — build resources/packages from local CSVs.
- `unitpackage/remote.py` — fetch the echemdb database ZIP
  (`ECHEMDB_DATABASE_VERSION`, overridable via `ECHEMDB_DATABASE_URL`).
- `unitpackage/entrypoint.py` — `unitpackage` CLI (`click`): `csv` and `ec`
  subcommands convert files into Data Packages.

Domain extension (electrochemistry) — subclasses of the generic core:

- `unitpackage/database/echemdb.py` — `Echemdb(Collection)`.
- `unitpackage/database/echemdb_entry.py` — `EchemdbEntry(Entry)`: electrode
  access, CV plotting (I/j vs U/E), bibliography via `pybtex`.
- `unitpackage/electrochemistry/reference_electrode.py` — reference electrode
  potential conversions.

Device loaders (auto-detect delimiter/decimal; selected via
`BaseLoader.create`):

- `unitpackage/loaders/baseloader.py` — `BaseLoader` for header + column-name
  lines + delimited data.
- `eclabloader.py` (`ECLabLoader`, with `eclab_fields.py`), `gamryloader.py`
  (`GamryLoader`).

## Conventions

- Units are powered by **astropy** (`astropy.units`), e.g. `'V'`, `'A / m2'`.
- Metadata follows the echemdb schema; nested values reachable both as
  `entry.metadata['echemdb']['source']['citationKey']` and
  `entry.metadata.echemdb.source.citationKey`.
- Domain-specific behavior belongs in `database/` and `electrochemistry/`
  subclasses, NOT in the generic `Collection`/`Entry`.

## Tests = doctests (important)

There are **no `test_*.py` files**. The entire suite is doctests embedded in
module docstrings, run with `--doctest-modules`. When you change behavior or a
docstring example, the doctest output must match exactly.

- Run tests: `pixi run doctest`  (= `pytest -n auto --doctest-modules unitpackage`)
- Doctest directives in use: `+REMOTE_DATA` (network; gated by
  `pytest-remotedata`, enabled with `--remote-data`), `+ELLIPSIS`,
  `+NORMALIZE_WHITESPACE`.
- `unitpackage/test/cli.py` provides `invoke()` for testing the `click` CLI in
  doctests.
- `conftest.py` pins pandas display options (width 100, max 6 cols, max 4 rows)
  so DataFrame reprs in doctests are deterministic — don't assume a wider repr.
- `MPLBACKEND=Agg` is set via pytest env so `.plot()`/matplotlib don't open
  windows.

## Linting / formatting

- `pixi run lint` runs pylint, black and isort (profile black, config in
  `.pylintrc` / `pyproject.toml`). Note that it *applies* black and isort.
- CI (`.github/workflows/lint.yml`) runs them in check mode:
  `pixi run pylint`, `pixi run black --diff --check`,
  `pixi run isort --check --diff`.

## Tooling & environments

- Managed with **pixi** (`pyproject.toml`, `pixi.lock`). Envs: `python-311`..
  `python-314`, `dev`, `doc`, `release`. The huge `.pixi/` dir is the local env
  cache — **ignore it** in searches (it dominates glob results).
- Build backend: setuptools. Requires Python ≥ 3.11.
- Docs: Sphinx + MyST/myst-nb under `doc/` (`pixi run -e doc doc`). Usage pages
  in `doc/usage/` (`.md` + paired `.ipynb` via jupytext).
- Releases: `rever` via `pixi run -e release rever X.Y.Z`; changelog fragments
  in `doc/news/`, consolidated into `ChangeLog`.

## Working agreements

- Match surrounding style; keep docstring examples runnable (they ARE the tests).
- Prefer the generic core for general features; keep echemdb specifics in the
  subclasses.
- Before considering work done or proposing a push, run `pixi run doctest` and
  `pixi run lint`, and add a news fragment.
