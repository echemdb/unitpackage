---
jupytext:
  formats: ipynb,md:myst
  text_representation:
    extension: .md
    format_name: myst
    format_version: 0.13
    jupytext_version: 1.18.1
kernelspec:
  name: python3
  display_name: Python 3 (ipykernel)
  language: python
---

# Loaders

`unitpackage.loaders` provides modules for loading non-standardized DSV (delimiter-separated value) files, e.g. TSV (tab-separated) or CSV (comma-separated), commonly created from software used to operate laboratory equipment.
Key issues of these files are, for example, lengthy header lines containing various metadata relevant to the recording software,
the use of `,` as a decimal separator in some world regions,
or files containing multiple data tables, etc.

`unitpackage.loaders` provides modules to parse non-standard files and load the data directly as a `pandas` Data Frame, which are used by unitpackage to create frictionless Data Packages (or [unitpackages](https://github.com/echemdb/) supporting the use of units).
The CLI allows conversion of data directly into such Data Packages for seamless integration in existing workflows.

Our approach aims at providing a single interface to load data into a certain format independent of the data source.
Filetypes supported and tested by `unitpackage.loaders` are:

| Manufacturer | Device type  | Software                    | Filesuffix | Loader      | device |
|--------------|--------------|-----------------------------|------------|-------------|--------|
| Biologic     | Potentiostat | EClab                       | mpt        | EClabLoader | eclab  |
| Gamry        | Potentiostat | Gamry Instruments Framework | DTA        | GamryLoader | gamry  |
|              |              |                             |            |             |        |

```{todo}
Improve table, such as including links.
```

## Examples

Consider the following DSV, that consists of three parts:

* the header, usually containing metadata relevant to the software and user predefined settings,
* column header lines, containing acronyms (dimensions) and often units for the data in one or more rows,
* the data part, where each column consists of identical data types.

```{code-cell} ipython3
:tags: [hide-input]

from io import StringIO
file = StringIO('''# I am messy data
Random stuff
maybe metadata : 3
in different formats = abc123
hopefully, some information
on where the data part starts!
t\tE\tj
s\tV\tA/cm2
0\t0\t0
1\t1\t1
2\t2\t2
''')
from unitpackage.loaders.baseloader import BaseLoader
csv = BaseLoader(file, header_lines=6, column_header_lines=2)
file.seek(0)
print(csv.file.read())
```

A pandas Data Frame can be created with limited input data.
The delimiter of the data part is evaluated automatically (unless specified as an argument).
Multiple column headers will be flattened.

```{code-cell} ipython3
from unitpackage.loaders.baseloader import BaseLoader
csv = BaseLoader(file, header_lines=6,
                 column_header_lines=2,
                 delimiters=None,
                 decimal=None)
csv.df
```

All parts of the file are accessible from the API for further use. For example the extraction of metadata from the header.

```{code-cell} ipython3
print(csv.header.read())
```

```{code-cell} ipython3
print(csv.column_headers.read())
```

```{code-cell} ipython3
print(csv.data.read())
```

## CLI

+++

The data can also be converted into frictionless Data Packages using the CLI.

```{note}
The input and output files for and from the following commands can be found in the [test folder](https://github.com/echemdb/unitpackage/tree/main/) of the repository.

The CLI only works for standard CSV without header and a single column header line, and specific converters summarized above.
```

A "standard" CSV

```{code-cell} ipython3
!unitpackage csv ../../test/loader_data/default.csv --outdir ../../test/generated/loader_data
```
