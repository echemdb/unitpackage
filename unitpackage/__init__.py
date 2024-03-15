import yaml

from unitpackage.entry import Entry


def csv_to_package(csvname, yamlname, outdir, fields=None):
    r"""
    Create a unitpackage, i.e., a CSV file and a JSON file,
    in the directory ``outdir``, from a CSV file and YAML file.

    Additional details on the fields/columns in the CV can be provided
    in the YAML. The file must be structured as follows:

    figure description:
        fields:
            - name: FirstFieldName
              unit: FirstFieldUnit
              OtherKey: SomeDescription
            - name: SecondFieldName
              unit: SecondFieldUnit
            - ...

    EXAMPLES:

    CSV and YAML file without a field description::

        >>> csvname = 'examples/from_csv/from_csv.csv'
        >>> yamlfile = 'examples/from_csv/from_csv.csv.yaml'
        >>> outdir = 'test/generated/created_packages'
        >>> unitpackage.csv_to_package(csvname=csvname, yamlname=yamlfile, outdir=outdir)

    CSV and YAML file with field descriptions::

        >>> csvname = 'examples/from_csv/from_csv_units.csv'
        >>> yamlfile = 'examples/from_csv/from_csv_units.csv.yaml'
        >>> outdir = 'test/generated/created_packages'
        >>> unitpackage.csv_to_package(csvname=csvname, yamlname=yamlfile, outdir=outdir)

    """

    with open(yamlname, "rb") as f:
        metadata = yaml.load(f, Loader=yaml.SafeLoader)

    metadata.setdefault("figure description", {})
    metadata["figure description"].setdefault("fields", {})

    fields = fields or metadata["figure description"]["fields"]

    entry = Entry.from_csv(csvname=csvname, metadata=metadata, fields=fields)
    entry.save(outdir=outdir)
