def collect_datapackages(data):
    # Collect all datapackage descriptors, see
    # https://specs.frictionlessdata.io/data-package/#metadata
    import os.path
    from glob import glob
    descriptors = glob(os.path.join(data, '**', '*.json'), recursive=True)

    # Read the package descriptors (does not read the actual data CSVs)
    from datapackage import Package
    return [Package(descriptor) for descriptor in descriptors]


