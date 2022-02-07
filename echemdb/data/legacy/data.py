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

datadir = os.path.normpath(os.path.join(os.path.dirname(__file__), "..", "data"))


def make_cvs_dataframe(packages, data=datadir):
    import pandas as pd

    data = [
        [
            package.descriptor["electrode material"],
            package.descriptor["surface"],
            package.descriptor["electrolyte"],
            package.descriptor["reference"],
            package.descriptor["echemdb-id"],
            f"{package.base_path}/datapackage.json",
            os.path.relpath(package.base_path, datadir),
        ]
        for package in packages
    ]

    return pd.DataFrame(
        data,
        columns=[
            "electrode material",
            "surface",
            "electrolyte",
            "reference",
            "echemdb-id",
            "path",
            "relpath",
        ],
    )
