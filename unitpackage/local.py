r"""
Utilities to work with local data packages such as
collecting packages and creating unitpackages.
"""

# ********************************************************************
#  This file is part of unitpackage.
#
#        Copyright (C) 2021-2024 Albert Engstfeld
#        Copyright (C)      2021 Johannes Hermann
#        Copyright (C)      2021 Julian Rüth
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

import logging
import os
import os.path
from glob import glob

import pandas as pd
from frictionless import Package, Resource, Schema

logger = logging.getLogger("unitpackage")

def create_df_resource(package, resource_name="echemdb"):
    r"""
    Return a pandas dataframe resource from a data packages,
    where the first resource refers to a CSV.

    EXAMPLES::

        >>> from frictionless import Package
        >>> package = Package("./examples/no_bibliography/no_bibliography.json")
        >>> df_resource = create_df_resource(package) # doctest: +NORMALIZE_WHITESPACE
        >>> df_resource
        {'name': 'echemdb',
        ...

        >>> df_resource.data
                      t         E         j
        ...

    """
    if not package.resources:
        raise ValueError(
            "dataframe resource can not be created since package has no resources"
        )
    descriptor_path = package.resources[0].basepath + "/" + package.resources[0].path
    df = pd.read_csv(descriptor_path)
    df_resource = Resource(df)
    df_resource.infer()
    df_resource.name = resource_name
    return df_resource


def collect_datapackage(filename):
    r"""
    Return data packages from a :param filename:.

    EXAMPLES::

        >>> package = collect_datapackage("./examples/no_bibliography/no_bibliography.json")
        >>> package # doctest: +NORMALIZE_WHITESPACE
        {'resources': [{'name':
        ...

    """
    package = Package(filename)

    package.add_resource(create_df_resource(package))
    package.get_resource("echemdb").schema = Schema.from_descriptor(
        package.resources[0].schema.to_dict()
    )

    return package


def collect_datapackages(data):
    r"""
    Return a list of data packages defined in the directory `data` and its
    subdirectories.

    EXAMPLES::

        >>> packages = collect_datapackages("./examples")
        >>> packages[0] # doctest: +NORMALIZE_WHITESPACE
        {'resources': [{'name':
        ...

    """
    # Collect all datapackage descriptors, see
    # https://specs.frictionlessdata.io/data-package/#metadata

    descriptors = sorted(glob(os.path.join(data, "**", "*.json"), recursive=True))

    # Read the package descriptors and append the data as pandas dataframe in a new resource
    return [collect_datapackage(descriptor) for descriptor in descriptors]


def create_unitpackage(csvname, metadata=None, fields=None):
    r"""
    Return a data package built from a :param metadata: dict and tabular data
    in :param csvname: str.

    The :param fields: list must must be structured such as
    `[{'name':'E', 'unit': 'mV'}, {'name':'T', 'unit': 'K'}]`.

    EXAMPLES::

        >>> fields = [{'name':'E', 'unit': 'mV'}, {'name':'I', 'unit': 'A'}]
        >>> package = create_unitpackage("./examples/from_csv/from_csv.csv", fields=fields)
        >>> package # doctest: +NORMALIZE_WHITESPACE
        {'resources': [{'name':
        ...

    TESTS:

    Fields are not valid::

        >>> fields = 'not a list'
        >>> package = create_unitpackage("./examples/from_csv/from_csv.csv", fields=fields) # doctest: +NORMALIZE_WHITESPACE
        Traceback (most recent call last):
        ...
        ValueError: 'fields' must be a list such as
        [{'name': '<fieldname>', 'unit':'<field unit>'}]`,
        e.g., `[{'name':'E', 'unit': 'mV}, {'name':'T', 'unit': 'K}]`

    More fields than required::

        >>> fields = [{'name':'E', 'unit': 'mV'}, {'name':'I', 'unit': 'A'}, {'name':'x', 'unit': 'm'}]
        >>> package = create_unitpackage("./examples/from_csv/from_csv.csv", fields=fields) # doctest: +NORMALIZE_WHITESPACE

    Part of the fields specified:

        >>> fields = [{'name':'E', 'unit': 'mV'}]
        >>> package = create_unitpackage("./examples/from_csv/from_csv.csv", fields=fields) # doctest: +NORMALIZE_WHITESPACE

    """

    csv_basename = os.path.basename(csvname)

    package = Package(
        resources=[
            Resource(
                path=csv_basename,
                basepath=os.path.dirname(csvname),
            )
        ],
    )
    package.infer()
    resource = package.resources[0]

    resource.custom.setdefault("metadata", {})
    resource.custom["metadata"].setdefault("echemdb", metadata)

    if fields:
        # Update fields in the datapackage describing the data in the CSV
        package_schema = resource.schema
        if not isinstance(fields, list):
            raise ValueError(
                "'fields' must be a list such as \
                [{'name': '<fieldname>', 'unit':'<field unit>'}]`, \
                e.g., `[{'name':'E', 'unit': 'mV}, {'name':'T', 'unit': 'K}]`"
            )

        # remove field if it is not a Mapping instance
        from collections.abc import Mapping
        for field in fields:
            if not isinstance(field, Mapping):
                raise ValueError(
                    "'field' must be a dict such as {'name': '<fieldname>', 'unit':'<field unit>'},\
                    e.g., `{'name':'j', 'unit': 'uA / cm2'}`"
                )

        provided_schema = Schema.from_descriptor({"fields": fields}, allow_invalid=True)

        new_fields = []
        for name in package_schema.field_names:
            if name in provided_schema.field_names:
                new_fields.append(
                    provided_schema.get_field(name).to_dict()
                    | package_schema.get_field(name).to_dict()
                )
            else:
                logger.warning(
                            f"Field with name {name} is not specified."
                        )


        resource.schema = Schema.from_descriptor({"fields": new_fields})

    return package
