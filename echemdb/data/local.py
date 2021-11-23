r"""
Utilities to work with local data packages.
"""
# ********************************************************************
#  This file is part of echemdb.
#
#        Copyright (C) 2021 Albert Engstfeld
#        Copyright (C) 2021 Johannes Hermann
#        Copyright (C) 2021 Julian Rüth
#        Copyright (C) 2021 Nicolas Hörmann
#
#  echemdb is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  echemdb is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with echemdb. If not, see <https://www.gnu.org/licenses/>.
# ********************************************************************

def collect_datapackages(data):
    r"""
    Return a list of data packages defined in the directory `data` and its
    subdirectories.

    EXAMPLES::

        >>> packages = collect_datapackages(".")

    """
    # Collect all datapackage descriptors, see
    # https://specs.frictionlessdata.io/data-package/#metadata
    import os.path
    from glob import glob
    descriptors = glob(os.path.join(data, '**', '*.json'), recursive=True)

    # Read the package descriptors (does not read the actual data CSVs)
    from datapackage import Package
    return [Package(descriptor) for descriptor in descriptors]

def collect_bibliography(bibfiles):
    r"""
    Return a list of bibliography files (bibtex) defined in the directory `bibfiles` and its
    subdirectories.

    EXAMPLES::

        >>> bibfiles = collect_bibliography(".")

    """
    import os.path
    from glob import glob
    from pathlib import Path
    from pybtex.database import parse_file

    files = [Path(file) for file in glob(os.path.join(bibfiles, '**', '*.bib'), recursive=True)]
    print(files)
    bib_entries = []

    for file in files:
        bib_entry = parse_file(file, bib_format='bibtex')
        if not file.stem == list(bib_entry.entries.keys()): 
            raise Exception(f"Entry label {bib_entry.entries.keys()} does not match file named {file.stem}.")
        
        if len(list(bib_entry.entries.keys())) > 1:
            raise Exception(f"The bib file {file} contains more than one key, but only one is allowed.")

        bib_entries.append(bib_entry)

    return bib_entries