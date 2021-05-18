import os.path

datadir = os.path.normpath(os.path.join(os.path.dirname(__file__), '..', 'data'))

def collect_datapackages(data = datadir):
    # Collect all datapackage descriptors, see
    # https://specs.frictionlessdata.io/data-package/#metadata
    import os.path
    from glob import glob
    descriptors = glob(os.path.join(data, '**', 'datapackage.json'), recursive=True)

    # Read the package descriptors (does not read the actual data CSVs)
    from datapackage import Package
    packages = [Package(descriptor) for descriptor in descriptors]

    return packages

def make_cvs_dataframe(packages, data = datadir):
    import pandas as pd

    data = [[
        package.descriptor['electrode material'],
        package.descriptor['surface'],
        package.descriptor['electrolyte'],
        package.descriptor['reference'],
        package.descriptor['echemdb-id'],
        f"{package.base_path}/datapackage.json",
        os.path.relpath(package.base_path, datadir),
    ] for package in packages]

    return pd.DataFrame(data, columns=['electrode material', 'surface', 'electrolyte', 'reference', 'echemdb-id', 'path', 'relpath'])
