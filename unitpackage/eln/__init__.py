r"""
Electronic Lab Notebook (ELN) backend integrations.

This package provides clients for fetching and uploading unitpackage entries
to ELN instances (:mod:`unitpackage.eln.elabftw` and
:mod:`unitpackage.eln.kadi`).

The backend-agnostic building blocks they share --- the
:class:`~unitpackage.eln._base.BaseELNClient` abstract base class and the
datapackage-descriptor helpers --- live in :mod:`unitpackage.eln._base` and are
re-exported here so they can be imported directly from ``unitpackage.eln``::

    >>> from unitpackage.eln import BaseELNClient

"""

# ********************************************************************
#  This file is part of unitpackage.
#
#        Copyright (C) 2026 Johannes Hermann
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
# ********************************************************************
from unitpackage.eln._base import (
    DATAPACKAGE_FILENAME,
    BaseELNClient,
    apply_datapackage_descriptor,
    build_datapackage_descriptor,
    first_resource,
)

__all__ = [
    "DATAPACKAGE_FILENAME",
    "BaseELNClient",
    "apply_datapackage_descriptor",
    "build_datapackage_descriptor",
    "first_resource",
]
