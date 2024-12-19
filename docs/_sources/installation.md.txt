Installation
============

The recommended way to install the unitpackage is to use your package manager,
(e.g., `apt-get` on Debian or Ubuntu, `pacman` on Arch Linux, `brew` on macOS.)

You can consult [repology](https://repology.org/project/python:unitpackage/packages)
to see if the unitpackage is available for your package manager.

Alternatively, the unitpackage can be installed by one of the following
approaches.

Install with pip from PyPI
--------------------------

The latest stable version of the unitpackage is available on
[PyPI](https://pypi.org/project/unitpackage/) for all platforms and can be
installed if you have Python and pip installed already:

```sh
pip install unitpackage
```

This command downloads and installs the unitpackage and its dependencies into
your local Python installation.

If the above command fails because you do not have permission to modify your
Python installation, you can install the unitpackage into your user account:

```sh
pip install --user unitpackage
```

You can instead also install the latest unreleased version of the unitpackage
from our [GitHub Repository](https://github.com/echemdb/unitpackage) with

```sh
pip install git+https://github.com/echemdb/unitpackage@main
```

Install with conda from conda-forge
-----------------------------------

The unitpackage is [available on
conda-forge](https://github.com/conda-forge/unitpackage-feedstock) for all
platforms.

If you don't have conda yet, we recommend to install
[Miniforge](https://github.com/conda-forge/miniforge#miniforge3).

Miniforge is already pre-configured for conda-forge. If you already had another
release of conda installed, make sure the conda-forge channel is
[configured correctly](https://conda-forge.org/docs/user/introduction.html#how-can-i-install-packages-from-conda-forge)

Once your conda setup is ready, create a new `unitpackage` environment with
the latest stable version of the unitpackage:

```sh
conda create -n unitpackage
```

To use the unitpackage, activate the `unitpackage` environment:

```sh
conda activate unitpackage
```

To install the unitpackage into an existing environment, activate that environment and then

```sh
conda install unitpackage
```

Install with pip for development
--------------------------------

If you want to work on the unitpackage itself, get a copy of the latest
unreleased version of the unitpackage:

```sh
git clone https://github.com/echemdb/unitpackage.git
```

Move to the directory and install the dependencies

```sh
conda env create --file environment.yaml
conda activate unitpackage
```

Create an [editable](https://pip.pypa.io/en/stable/cli/pip_install/#editable-installs) install of the unitpackage:

```sh
pip install -e unitpackage
```

Any changes you make to the files in your local copy of the unitpackage should
now be available in your next Python session.

We would love to see your contribution to the unitpackage.
