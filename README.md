[![Binder](https://mybinder.org/badge_logo.svg)](https://mybinder.org/v2/gh/echemdb/echemdb/0.6.0?urlpath=tree%2Fdoc%2Fusage%2Fentry_interactions.md)
[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.6502901.svg)](https://doi.org/10.5281/zenodo.6502901)

The unitpackage Python package can interact with a collection of
[frictionless datapackages](https://frictionlessdata.io/).
To use the full potential of unitpackage, the resource within a datapackage should contain:

* metadata nested within a list of metadata.
* a key `units` whose value is a string representation of an [astropy unit](https://docs.astropy.org/en/stable/units/index.html).

A short version of such a datapackage can be found [here](https://github.com/echemdb/echemdb/tree/main/doc/files/) and looks as follows

```json
{
    "resources": [
        {
            "name": "demo_package",
            "type": "table",
            "path": "demo_package.csv",
            "scheme": "file",
            "format": "csv",
            "mediatype": "text/csv",
            "encoding": "utf-8",
            "schema": {
                "fields": [
                    {
                        "name": "t",
                        "type": "number",
                        "unit": "s"
                    },
                    {
                        "name": "j",
                        "type": "number",
                        "unit": "A / m2"
                    }
                ]
            },
            "metadata": {
                "echemdb": {
                    "description": "Sample data for the unitpackage module.",
                    "curation": {
                        "process": [
                            {
                                "role": "experimentalist",
                                "name": "Joh Doe",
                                "laboratory": "Institute of Good Scientific Practice",
                                "date": "2021-07-09"
                            }
                        ]
                    }
                }
            }
        }
    ]
}
```

The metadata of an entries' resource in a collection is accessible from the python API.

```python
>>> from unitpackage.collection import Collection
>>> from unitpackage.local import collect_datapackages
>>> db = Collection(data_packages=collect_datapackages('./doc/files'))
>>> entry = db['demo_package_cv']
>>> entry.description
'Sample data for the unitpackage module.'
```

From the API also a simple 2D plot can be drawn.

```python
>>> entry.plot()
```
<img src=https://raw.githubusercontent.com/echemdb/unitpackage/main/doc/images/readme_demo_plot.png style="width:400px">

Ultimately, the `unitpackage` allows for simple transformation of data within a resource into different units.

```python
>>> entry.get_unit('j')
'A / m2'
>>> entry.df
          t         E        j
0  0.000000	-0.196962 0.043009
1  0.011368	-0.196393 0.051408
...
>>> entry.rescale({'E' : 'mV', 'j' : 'uA / m2'}).df
          t           E             j
0  0.000000 -196.961730  43008.842162
1  0.011368 -196.393321  51408.199892
...
```

Collections for specific measurement types can be created, which provide additional accessibility to the meatadata or simplify the representation of such data in common plot types. An example of such a collection can be found on [echemdb.org](https://www.echemdb.org), which shows Cyclic Voltammetry data annotated following [echemdb's metadata schema](https://github.com/echemdb/metadata-schema), which can be stored in a `CVCollection`

Collections can be generated from or from local files or data published in repositories such as on [echemdb.org](https://www.echemdb.org)

Detailed installation instructions, description of the modules, advanced usage examples, including
local collection creation, are provided in our
[documentation](https://echemdb.github.io/unitpackage/).

# Installation instructions

This package is available on [PiPY](https://pypi.org/project/unitpackage/) and can be installed with pip:

```sh .noeval
pip install unitpackage
```

The package is also available on [conda-forge](https://github.com/conda-forge/unitpackage-feedstock) an can be installed with conda

```sh .noeval
conda install -c conda-forge unitpackage
```

or mamba

```sh .noeval
mamba install -c conda-forge unitpackage
```

Please consult our [documentation](https://echemdb.github.io/unitpackage/) for
more detailed [installation instructions](https://echemdb.github.io/unitpackage/installation.html).

# License

The contents of this repository are licensed under the [GNU General Public
License v3.0](./LICENSE) or, at your option, any later version.
