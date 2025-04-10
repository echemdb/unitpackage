r"""
Utilities to work with local frictionless Data Packages such as
collecting Data Packages and creating unitpackages.
"""

# ********************************************************************
#  This file is part of unitpackage.
#
#        Copyright (C) 2021-2025 Albert Engstfeld
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


def create_df_resource(resource):
    r"""
    Return a pandas dataframe resource for a frictionless Tabular Resource.

    EXAMPLES::

        >>> from frictionless import Package
        >>> resource = Package("./examples/local/no_bibliography/no_bibliography.json").resources[0]
        >>> df_resource = create_df_resource(resource) # doctest: +NORMALIZE_WHITESPACE
        >>> df_resource
        {'name': 'memory',
        ...
        'format': 'pandas',
        ...

        >>> df_resource.data
                      t         E         j
        ...

    """
    if not resource:
        raise ValueError(
            "dataframe resource can not be created since the Data Package has no resources."
        )
    descriptor_path = resource.basepath + "/" + resource.path
    df = pd.read_csv(descriptor_path)
    df_resource = Resource(df)
    df_resource.infer()

    return df_resource


def collect_resources(datapackages):
    r"""
    Return a list of resources from a list of Data Packages.

    EXAMPLES::

        >>> packages = collect_datapackages("./examples/local")
        >>> resources = collect_resources(packages)
        >>> [resource.name for resource in resources] # doctest: +NORMALIZE_WHITESPACE
        ['alves_2011_electrochemistry_6010_f1a_solid',
        'engstfeld_2018_polycrystalline_17743_f4b_1',
        'no_bibliography']

    """

    return [
        resource for datapackage in datapackages for resource in datapackage.resources
    ]


def collect_datapackages(data):
    r"""
    Return a list of data packages defined in the directory `data` and its
    subdirectories.

    EXAMPLES::

        >>> packages = collect_datapackages("./examples/local")
        >>> packages[0] # doctest: +NORMALIZE_WHITESPACE
        {'resources': [{'name':
        ...

    """
    packages = sorted(glob(os.path.join(data, "**", "*.json"), recursive=True))

    return [Package(package) for package in packages]


def create_unitpackage(csvname, metadata=None, fields=None):
    r"""
    Return a Data Package built from a :param metadata: dict and tabular data
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

    Invalid fields::

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

    resource = Resource(
        path=csv_basename,
        basepath=os.path.dirname(csvname) or ".",
    )

    resource.infer()

    resource.custom.setdefault("metadata", {})
    resource.custom["metadata"].setdefault("echemdb", metadata)

    if fields:
        # Update fields in the Resource describing the data in the CSV
        resource_schema = resource.schema
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
        unspecified_fields = []

        for name in resource_schema.field_names:
            if name in provided_schema.field_names:
                new_fields.append(
                    provided_schema.get_field(name).to_dict()
                    | resource_schema.get_field(name).to_dict()
                )
            else:
                new_fields.append(resource_schema.get_field(name).to_dict())

        if len(unspecified_fields) != 0:
            logger.warning(
                f"Additional information were not provided for fields {unspecified_fields}."
            )

        unused_provided_fields = []
        for name in provided_schema.field_names:
            if name not in resource_schema.field_names:
                unused_provided_fields.append(name)
        if len(unused_provided_fields) != 0:
            logger.warning(
                f"Fields with names {unused_provided_fields} was provided but does not appear in the field names of tabular resource {resource_schema.field_names}."
            )

        resource.schema = Schema.from_descriptor({"fields": new_fields})

    package = Package(resources=[resource])

    return package


def write_metadata(out, metadata):
    r"""
    Write `metadata` to the `out` stream in JSON format.

    """

    def defaultconverter(item):
        r"""
        Return `item` that Python's json package does not know how to serialize
        in a format that Python's json package does know how to serialize.
        """
        from datetime import date, datetime

        # The YAML standard knows about dates and times, so we might see these
        # in the metadata. However, standard JSON does not know about these so
        # we need to serialize them as strings explicitly.
        if isinstance(item, (datetime, date)):
            return str(item)

        raise TypeError(f"Cannot serialize ${item} of type ${type(item)} to JSON.")

    import json

    json.dump(metadata, out, default=defaultconverter, ensure_ascii=False, indent=4)
    # json.dump does not save files with a newline, which compromises the tests
    # where the output files are compared to an expected json.
    out.write("\n")
