> Write something meaningful about this project here :)

# Build Process

The website is built automatically with [GitHub Actions](https://github.com/echemdb/website/blob/main/.github/workflows/build.yml).

To build the website locally, you can (re)create a [conda environment](https://conda.io/projects/conda/en/latest/user-guide/tasks/manage-environments.html):

```
conda config --add channels conda-forge
conda config --set channel_priority strict
conda env create --force -f environment.yml
```

Alternatively, if you want to install the required packages into an existing, environment use:

```
conda env update --name <your_env_name> --file environment.yml
```

Build the website and follow the link to preview the pages:

```
conda activate echemdb
mkdocs serve
```

# License

The contents of this repository are licensed under the [GNU General Public
License v3.0](./LICENSE) or, at your option, any later version.  The contents
of [data/](./data/) and [literature/](./literature/) are additionally licensed
under the [Creative Commons Attribution 4.0 International
License](https://creativecommons.org/licenses/by/4.0/).
