r"""
Utilities to work with local data packages such as
collecting packages and creating unitpackages.
"""
# ********************************************************************
#  This file is part of unitpackage.
#
#        Copyright (C) 2021-2023 Albert Engstfeld
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
import os
import os.path
from glob import glob

import pandas as pd
from frictionless import Package, Resource, Schema

def create_df_resource(package, resource_name='echemdb'):
    if not package.resources:
        raise ValueError("dataframe resource can not be created since package has no resources")
    descriptor_path = (
        package.resources[0].basepath + "/" + package.resources[0].path
    )
    df = pd.read_csv(descriptor_path)
    df_resource = Resource(df)
    df_resource.infer()
    df_resource.name = resource_name
    return df_resource

def collect_datapackage(filename):
    package = Package(filename)
    # if not package.resources:
    #     raise ValueError(f"package {filename} has no CSV resources")
    # descriptor_path = (
    #     package.resources[0].basepath + "/" + package.resources[0].path
    # )
    # df = pd.read_csv(descriptor_path)
    # df_resource = Resource(df)
    # df_resource.infer()
    # df_resource.name = "echemdb"
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

    descriptors = glob(os.path.join(data, "**", "*.json"), recursive=True)



    packages = []

    for descriptor in descriptors:
        # package = Package(descriptor)

        # if not package.resources:
        #     raise ValueError(f"package {descriptor} has no CSV resources")
        # descriptor_path = (
        #     package.resources[0].basepath + "/" + package.resources[0].path
        # )
        # df = pd.read_csv(descriptor_path)
        # df_resource = Resource(df)
        # df_resource.infer()
        # df_resource.name = "echemdb"
        # package.add_resource(df_resource)
        # package.get_resource("echemdb").schema = Schema.from_descriptor(
        #     package.resources[0].schema.to_dict()
        # )

        # packages.append(package)
        #--------------------------------------------
        # Read the package descriptors and append the data as pandas dataframe in a new resource
        packages.append(collect_datapackage(descriptor))

    return packages

def create_unitpackage(csvname, metadata=None, fields=[]):
    r"""
    Return a data package built from a :param:`metadata` dict and tabular data
    in :param:`csvname` str.

    The :param:`fields` list must must be structured such as
    `[{'name':'E', 'unit': 'mV}, {'name':'T', 'unit': 'K}]`.
    """

    csv_basename = os.path.basename(csvname)

    package = Package(
        resources=[
            Resource(
                path=csv_basename,
                # basepath=outdir or os.path.dirname(csvname),
                basepath= os.path.dirname(csvname),
            )
        ],
    )
    package.infer()
    resource = package.resources[0]

    resource.custom.setdefault("metadata", {})
    resource.custom["metadata"].setdefault("echemdb", metadata)

    # Update fields in the datapackage describing the data in the CSV
    package_schema = resource.schema

    # can probably be removed since validation is performed by frictionless schema
    if not isinstance(fields, list):
        raise ValueError(
            "'fields' must be a list such as \
            [{'name': '<fieldname>', 'unit':'<field unit>'}]`, \
            e.g., `[{'name':'E', 'unit': 'mV}, {'name':'T', 'unit': 'K}]`"
        )

    # remove field if it is not a Mapping instance
    from collections.abc import Mapping

    # can probably be removed since validation is performed by frictionless schema
    for field in fields:
        if not isinstance(field, Mapping):
            raise ValueError(
                "'field' must be a dict such as {'name': '<fieldname>', 'unit':'<field unit>'},\
                e.g., `{'name':'j', 'unit': 'uA / cm2'}`"
            )

    provided_schema = Schema.from_descriptor(
        {"fields": fields}, allow_invalid=True
    )

    new_fields = []
    for name in package_schema.field_names:
        if not name in provided_schema.field_names:
            # Raise only a warning
            raise KeyError(
                f"Field with name {name} is not specified in `data_description.fields`."
            )
        new_fields.append(
            provided_schema.get_field(name).to_dict()
            | package_schema.get_field(name).to_dict()
        )

    resource.schema = Schema.from_descriptor({"fields": new_fields})

    # with open(
    #     _outfile(csv_basename, suffix=".package.json", outdir=outdir),
    #     mode="w",
    #     encoding="utf-8",
    # ) as json:
    #     _write_metadata(json, package.to_dict())

    return package

# from svgdigitizer
# def _outfile(template, suffix=None, outdir=None):
#     r"""
#     Return a file name for writing.

#     The file is named like `template` but with the suffix changed to `suffix`
#     if specified. The file is created in `outdir`, if specified, otherwise in
#     the directory of `template`.

#     EXAMPLES::

#         >>> from svgdigitizer.test.cli import invoke, TemporaryData
#         >>> with TemporaryData("**/xy.svg") as directory:
#         ...     outname = _outfile(os.path.join(directory, "xy.svg"), suffix=".csv")
#         ...     with open(outname, mode="wb") as csv:
#         ...         _ = csv.write(b"...")
#         ...     os.path.exists(os.path.join(directory, "xy.csv"))
#         True

#     ::

#         >>> with TemporaryData("**/xy.svg") as directory:
#         ...     outname = _outfile(os.path.join(directory, "xy.svg"), suffix=".csv", outdir=os.path.join(directory, "subdirectory"))
#         ...     with open(outname, mode="wb") as csv:
#         ...         _ = csv.write(b"...")
#         ...     os.path.exists(os.path.join(directory, "subdirectory", "xy.csv"))
#         True

#     """
#     if suffix is not None:
#         template = f"{os.path.splitext(template)[0]}{suffix}"

#     if outdir is not None:
#         template = os.path.join(outdir, os.path.basename(template))

#     os.makedirs(os.path.dirname(template) or ".", exist_ok=True)

#     return template

# # from svgdigitizer
# def _write_metadata(out, metadata):
#     r"""
#     Write `metadata` to the `out` stream in JSON format.

#     This is a helper method for :meth:`_create_outfiles`.
#     """

#     def defaultconverter(item):
#         r"""
#         Return `item` that Python's json package does not know how to serialize
#         in a format that Python's json package does know how to serialize.
#         """
#         from datetime import date, datetime

#         # The YAML standard knows about dates and times, so we might see these
#         # in the metadata. However, standard JSON does not know about these so
#         # we need to serialize them as strings explicitly.
#         if isinstance(item, (datetime, date)):
#             return str(item)

#         raise TypeError(f"Cannot serialize ${item} of type ${type(item)} to JSON.")

#     import json

#     json.dump(metadata, out, default=defaultconverter, ensure_ascii=False, indent=4)
#     # json.dump does not save files with a newline, which compromises the tests
#     # where the output files are compared to an expected json.
#     out.write("\n")
