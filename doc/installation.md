Installation
============

The recommended way to install the echemdb is to use your package manager,
(e.g., `apt-get` on Debian or Ubuntu, `pacman` on Arch Linux, `brew` on macOS.)

You can consult [repology](https://repology.org/project/python:echemdb/packages)
to see if the echemdb is available for your package manager.

Alternatively, the echemdb can be installed by one of the following
approaches.

Install with pip from PyPI
--------------------------

The latest stable version of the echemdb is available on
[PyPI](https://pypi.org/project/echemdb/) for all platforms and can be
installed if you have Python and pip installed already:

```sh
pip install echemdb
```

This command downloads and installs the echemdb and its dependencies into
your local Python installation.

If the above command fails because you do not have permission to modify your
Python installation, you can install the echemdb into your user account:

```sh
pip install --user echemdb
```

You can instead also install the latest unreleased version of the echemdb
from our [GitHub Repository](https://github.com/echemdb/echemdb) with

```sh
pip install git+https://github.com/echemdb/echemdb@main
```


Install with conda from conda-forge
-----------------------------------

The echemdb is [available on
conda-forge](https://github.com/conda-forge/echemdb-feedstock) for all
platforms.

If you don't have conda yet, we recommend to install
[Miniforge](https://github.com/conda-forge/miniforge#miniforge3).

Miniforge is already pre-configured for conda-forge. If you already had another
release of conda installed, make sure the conda-forge channel is
[configured correctly](https://conda-forge.org/docs/user/introduction.html#how-can-i-install-packages-from-conda-forge)

Once your conda setup is ready, create a new `echemdb` environment with
the latest stable version of the echemdb:

```sh
conda create -n echemdb echemdb
```

To use the echemdb, activate the `echemdb` environment:

```sh
conda activate echemdb
```

To install the echemdb into an existing environment, activate that environment and then

```sh
conda install echemdb
```

Install with pip for development
--------------------------------

If you want to work on the echemdb itself, get a copy of the latest
unreleased version of the echemdb:

```sh
git clone https://github.com/echemdb/echemdb.git
```

Create an [editable](https://pip.pypa.io/en/stable/cli/pip_install/#editable-installs) install of the echemdb:

```sh
pip install -e echemdb
```

Any changes you make to the files in your local copy of the echemdb should
now be available in your next Python session.

We would love to see your contribution to the echemdb.
