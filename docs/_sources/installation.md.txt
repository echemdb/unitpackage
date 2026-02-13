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
[Miniforge](https://github.com/conda-forge/miniforge).

Miniforge is already pre-configured for conda-forge. If you already had another
release of conda installed, make sure the conda-forge channel is
[configured correctly](https://conda-forge.org/docs/user/introduction/#how-can-i-install-packages-from-conda-forge)

Once your conda setup is ready, create a new `unitpackage` environment with
the latest stable version of the unitpackage:

```sh
conda create -n unitpackage unitpackage
```

To use the unitpackage, activate the `unitpackage` environment:

```sh
conda activate unitpackage
```

To install the unitpackage into an existing environment, activate that environment and then

```sh
conda install unitpackage
```

Install with pixi for development
--------------------------------

We recommend [pixi](https://pixi.prefix.dev) for developers of unitpackage to use a
curated list of dependencies that are tested to work on all platforms. These
are also exactly the dependencies that are used in our CI, which makes it
easier to test things locally.

If you don't have pixi yet, follow the [pixi installation
instructions](https://pixi.prefix.dev/latest/getting_started/).

Once pixi is installed, get a copy of the latest unitpackage and install the
dependencies:

```sh
git clone https://github.com/echemdb/unitpackage.git
cd unitpackage
pixi install
```

### Running tests

Run the full test suite (doctests) with:

```sh
pixi run test
```

This is equivalent to running the doctests directly:

```sh
pixi run doctest
```

To run the tests against a specific Python version, use one of the
`python-3XX` environments:

```sh
pixi run -e python-312 doctest
```

Available test environments are: `python-310`, `python-311`, `python-312`,
`python-313`, and `python-314`.

### Linting

Run all linters (pylint, black, isort) at once:

```sh
pixi run lint
```

Or run them individually:

```sh
pixi run black
pixi run isort
pixi run pylint
```

### Building the documentation

Rebuild the documentation with:

```sh
pixi run doc
```

Check for broken links in the documentation with:

```sh
pixi run linkcheck
```

### Interactive development

You can explore unitpackage in an interactive IPython session:

```sh
pixi run -e dev ipython
```

Or launch a Jupyter notebook:

```sh
pixi run -e dev jupyter lab
```

You can also drop into an interactive shell with all development dependencies
available:

```sh
pixi shell -e dev
```

Note that any changes you make to the files in your local copy of unitpackage
should be immediately available when you restart your Python kernel.

We would love to see your contribution to unitpackage.
