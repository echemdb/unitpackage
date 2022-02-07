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

import os.path

import echemdb.data.cv.database
import echemdb.data.local

packages = echemdb.data.local.collect_datapackages(
    os.path.normpath(os.path.join(os.path.dirname(__file__), "..", "..", "..", "data"))
)

bibliography = echemdb.data.local.collect_bibliography(
    os.path.normpath(
        os.path.join(os.path.dirname(__file__), "..", "..", "..", "literature")
    )
)

cv = echemdb.data.cv.database.Database(packages, bibliography)
