> Write something meaningful about this project here :)

# Build Process

The website is built automatically with [GitHub Actions](https://github.com/echemdb/website/blob/main/.github/workflows/build.yml).

To build the website locally, you can (re)create a [conda environment](https://conda.io/projects/conda/en/latest/user-guide/tasks/manage-environments.html):

```
conda config --add channels conda-forge
conda config --set channel_priority strict
conda env create --force -f environment.yml
```

Build the website and follow the link to preview the pages:

```
conda activate echemdb
mkdocs serve
```
