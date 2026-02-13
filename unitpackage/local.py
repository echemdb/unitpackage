r"""
Utilities to work with local frictionless Data Packages such as
collecting Data Packages and creating unitpackages.
"""

# ********************************************************************
#  This file is part of unitpackage.
#
#        Copyright (C) 2021-2026 Albert Engstfeld
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


def create_tabular_resource_from_csv(
    csvname,
    encoding=None,
    header_lines=None,
    column_header_lines=None,
    decimal=None,
    delimiters=None,
):
    r"""
    Return a resource built from a provided CSV.

    EXAMPLES::

    For standard CSV files (single header line and subsequent
    lines with data, using `.` as decimal separator.)
    a tabular data resource is created::

        >>> filename = './examples/from_csv/from_csv.csv'
        >>> resource = create_tabular_resource_from_csv(filename)
        >>> resource # doctest: +NORMALIZE_WHITESPACE
        {'name': 'from_csv',
        'type': 'table',
        'path': 'from_csv.csv',
        'scheme': 'file',
        'format': 'csv',
        'mediatype': 'text/csv', ...

    For CSV files with a more complex structure (header, multiple column header lines, or other separators)
    a pandas dataframe resource is created instead::

        >>> filename = 'examples/from_csv/from_csv_multiple_headers.csv'
        >>> resource = create_tabular_resource_from_csv(csvname=filename, column_header_lines=2)
        >>> resource # doctest: +NORMALIZE_WHITESPACE
        {'name': 'memory',
        'type': 'table',
        'data': [],
        'format': 'pandas',
        'mediatype': 'application/pandas',
        'schema': {'fields': [{'name': 'E / V', 'type': 'integer'},
                              {'name': 'j / A / cm2', 'type': 'integer'}]}}


    """
    csv_basename = os.path.basename(csvname)

    if not header_lines and not column_header_lines and not decimal and not delimiters:
        resource = Resource(
            path=csv_basename,
            basepath=os.path.dirname(csvname) or ".",
        )
        resource.infer()
        return resource

    # pylint: disable=duplicate-code
    return create_df_resource_from_csv(
        csvname,
        encoding=encoding,
        header_lines=header_lines,
        column_header_lines=column_header_lines,
        decimal=decimal,
        delimiters=delimiters,
    )


def create_df_resource_from_csv(
    csvname,
    encoding=None,
    header_lines=None,
    column_header_lines=None,
    decimal=None,
    delimiters=None,
):
    r"""
    Create a pandas dataframe resource from a CSV file.

    EXAMPLES::

        >>> from unitpackage.local import create_df_resource_from_csv
        >>> filename = 'examples/from_csv/from_csv_multiple_headers.csv'
        >>> resource = create_df_resource_from_csv(csvname='examples/from_csv/from_csv_multiple_headers.csv', column_header_lines=2)
        >>> resource # doctest: +NORMALIZE_WHITESPACE
        {'name': 'memory',
        'type': 'table',
        'data': [],
        'format': 'pandas',
        'mediatype': 'application/pandas',
        'schema': {'fields': [{'name': 'E / V', 'type': 'integer'},
                              {'name': 'j / A / cm2', 'type': 'integer'}]}}

    """

    from unitpackage.loaders.baseloader import BaseLoader

    with open(csvname, "r", encoding=encoding or "utf-8") as f:
        csv = BaseLoader(
            f,
            header_lines=header_lines,
            column_header_lines=column_header_lines,
            decimal=decimal,
            delimiters=delimiters,
        )

    return create_df_resource_from_df(csv.df)


def create_df_resource_from_df(df):
    r"""
    Return a pandas dataframe resource for a pandas DataFrame.

    EXAMPLES::

        >>> data = {'x': [1, 2, 3], 'y': [4, 5, 6]}
        >>> import pandas as pd
        >>> df = pd.DataFrame(data)
        >>> from unitpackage.local import create_df_resource_from_df
        >>> resource = create_df_resource_from_df(df)
        >>> resource # doctest: +NORMALIZE_WHITESPACE
        {'name': 'memory',
        'type': 'table',
        'data': [],
        'format': 'pandas', ...

        >>> resource.data
           x  y
        0  1  4
        1  2  5
        2  3  6

        >>> resource.format
        'pandas'


    """
    df_resource = Resource(df)
    df_resource.infer()

    return df_resource


def create_df_resource_from_tabular_resource(resource):
    r"""
    Return a pandas dataframe resource for a frictionless Tabular Resource.

    EXAMPLES::

        >>> from frictionless import Package
        >>> from unitpackage.local import create_df_resource_from_tabular_resource
        >>> tabular_resource = Package("./examples/local/no_bibliography/no_bibliography.json").resources[0]
        >>> df_resource = create_df_resource_from_tabular_resource(tabular_resource) # doctest: +NORMALIZE_WHITESPACE
        >>> df_resource
        {'name': 'memory',
        ...
        'format': 'pandas',
        ...

        >>> df_resource.data
                      t         E         j
        ...

    TESTS::

        >>> data = {'x': [1, 2, 3], 'y': [4, 5, 6]}
        >>> df = pd.DataFrame(data)
        >>> from unitpackage.entry import Entry
        >>> entry = Entry.from_df(df, basename='test_parent_directory')
        >>> entry.save(outdir=".")
        >>> entry_ = Entry.from_local('test_parent_directory.json')
        >>> entry_.df
               x  y
            0  1  4
            1  2  5
            2  3  6

    """
    descriptor_path = (
        resource.basepath + "/" + resource.path if resource.basepath else resource.path
    )

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


def update_fields(original_fields, new_fields):
    r"""
    Return a new list of fields where a list of fields has been updated
    based on a new list of fields.

    The :param: original_fields: list and :param new_fields: list
    must must be structured such as
    `[{'name':'E', 'unit': 'mV'}, {'name':'T', 'unit': 'K'}]`
    and each entry must contain a key `name` corresponding to a field name
    in the original fields.

    EXAMPLES::

        >>> from unitpackage.local import update_fields, create_tabular_resource_from_csv
        >>> schema = create_tabular_resource_from_csv("./examples/from_csv/from_csv.csv").schema
        >>> original_fields = schema.to_dict()['fields']
        >>> original_fields # doctest: +NORMALIZE_WHITESPACE
        [{'name': 'E', 'type': 'integer'},
        {'name': 'I', 'type': 'integer'}]

        >>> new_fields = [{'name':'E', 'unit': 'mV'}, {'name':'I', 'unit': 'A'}, {'name':'x', 'unit': 'm'}]
        >>> updated_fields = update_fields(original_fields, new_fields)
        >>> updated_fields # doctest: +NORMALIZE_WHITESPACE
        [{'name': 'E', 'type': 'integer', 'unit': 'mV'},
        {'name': 'I', 'type': 'integer', 'unit': 'A'}]

    TESTS:

    Invalid fields::

        >>> fields = 'not a list'
        >>> updated_fields = update_fields(original_fields, fields)
        Traceback (most recent call last):
        ...
        ValueError: 'fields' must be a list such as
        [{'name': '<fieldname>', 'unit':'<field unit>'}]`,
        e.g., `[{'name':'E', 'unit': 'mV}, {'name':'T', 'unit': 'K}]`

    More fields than required::

        >>> fields = [{'name':'E', 'unit': 'mV'}, {'name':'I', 'unit': 'A'}, {'name':'x', 'unit': 'm'}]
        >>> updated_fields = update_fields(original_fields, fields)
        >>> updated_fields  # doctest: +NORMALIZE_WHITESPACE
        [{'name': 'E', 'type': 'integer', 'unit': 'mV'},
        {'name': 'I', 'type': 'integer', 'unit': 'A'}]

    Part of the fields specified:

        >>> fields = [{'name':'E', 'unit': 'mV'}]
        >>> updated_fields = update_fields(original_fields, fields)
        >>> updated_fields  # doctest: +NORMALIZE_WHITESPACE
        [{'name': 'E', 'type': 'integer', 'unit': 'mV'},
        {'name': 'I', 'type': 'integer'}]

    """

    def validate_field_structure(fields):
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

    validate_field_structure(original_fields)
    validate_field_structure(new_fields)

    # Use frictionless Schema for field management
    schema = Schema({"fields": original_fields})

    # Create a lookup dict for provided fields by name
    provided_fields_dict = {
        field["name"]: field for field in new_fields if "name" in field
    }

    unspecified_fields = []
    unused_provided_fields = []

    # Update fields that exist in the original schema using schema.update_field()
    for field_name in schema.field_names:
        if field_name in provided_fields_dict:
            # Extract updates (excluding 'name' since update_field takes name separately)
            updates = {
                k: v for k, v in provided_fields_dict[field_name].items() if k != "name"
            }
            schema.update_field(field_name, updates)
        else:
            unspecified_fields.append(field_name)

    # Record any provided fields that are not present in the original schema
    for name in provided_fields_dict.keys():
        if name not in schema.field_names:
            unused_provided_fields.append(name)

    if len(unspecified_fields) != 0:
        logger.warning(
            f"Additional information was not provided for fields {unspecified_fields}."
        )

    if len(unused_provided_fields) != 0:
        logger.warning(
            f"Fields with names {unused_provided_fields} were provided but do not appear in the field names of tabular resource {schema.field_names}."
        )

    # Return the updated fields as a list of dicts
    return [field.to_dict() for field in schema.fields]


def create_unitpackage(resource, metadata=None, fields=None):
    r"""
    Return a Data Package built from a :param metadata: dict and tabular data
    in :param resource: frictionless.Resource.

    The :param fields: list must be structured such as
    `[{'name':'E', 'unit': 'mV'}, {'name':'T', 'unit': 'K'}]`.

    EXAMPLES::

        >>> from unitpackage.local import create_tabular_resource_from_csv, create_unitpackage
        >>> resource = create_tabular_resource_from_csv("./examples/from_csv/from_csv.csv")
        >>> new_fields = [{'name':'E', 'unit': 'mV'}, {'name':'I', 'unit': 'A'}]
        >>> package = create_unitpackage(resource=resource, fields=new_fields)
        >>> package # doctest: +NORMALIZE_WHITESPACE
        {'resources': [{'name':
        ...

    """
    resource.custom.setdefault("metadata", {})
    resource.custom["metadata"] = metadata

    if fields:
        # Use update_fields() for field updates with proper validation and logging
        original_fields = [field.to_dict() for field in resource.schema.fields]
        updated_fields = update_fields(original_fields, fields)

        # Update the resource schema with the updated fields
        resource.schema = Schema({"fields": updated_fields})

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
