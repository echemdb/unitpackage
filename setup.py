# ********************************************************************
#  This file is part of unitpackage.
#
#        Copyright (C) 2021-2024 Albert Engstfeld
#        Copyright (C)      2021 Johannes Hermann
#        Copyright (C) 2021-2022 Julian Rüth
#        Copyright (C)      2021 Nicolas Hörmann
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

from distutils.core import setup

setup(
    name='unitpackage',
    version="0.8.3",
    packages=['unitpackage', 'unitpackage.cv'],
    license='GPL 3.0+',
    description="a Python library to interact with a collection of frictionless datapackages",
    long_description=open('README.md', encoding="UTF-8").read(),
    long_description_content_type="text/markdown",
    include_package_data=True,
    install_requires=[
      "astropy>=5,<6",
      "filelock>=3,<4",
      "frictionless>=5.10.1,<6",
      "matplotlib>=3.5.0,<4",
      "pandas>=2,<3",
      "plotly>=5,<6",
      "pybtex>=0.24,<0.25",
    ],
    python_requires=">=3.9",
)
