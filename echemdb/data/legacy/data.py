import os.path

datadir = os.path.normpath(os.path.join(os.path.dirname(__file__), '..', 'data'))

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
