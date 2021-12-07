r"""
A Data Package decribing a Cyclic Voltammogram.

These are the individual elements of a :class:`Database`.
"""
# ********************************************************************
#  This file is part of echemdb.
#
#        Copyright (C) 2021 Albert Engstfeld
#        Copyright (C) 2021 Johannes Hermann
#        Copyright (C) 2021 Julian Rüth
#        Copyright (C) 2021 Nicolas Hörmann
#
#  echemdb is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  echemdb is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with echemdb. If not, see <https://www.gnu.org/licenses/>.
# ********************************************************************


from echemdb.data.cv.descriptor import Descriptor

class Entry:
    r"""
    A [data packages](https://github.com/frictionlessdata/datapackage-py)
    describing a Cyclic Voltammogram.

    EXAMPLES:

    Entries could be created directly from a datapackage that has been created
    with svgdigitizer's `cv` command. However, they are normally obtained by
    opening a :class:`Database` of entries::

        >>> from echemdb.data.cv.database import Database
        >>> database = Database.create_example()
        >>> entry = next(iter(database))

    """
    def __init__(self, package, bibliography):
        self.package = package
        self.bibliography = bibliography

    @property
    def identifier(self):
        r"""
        Return a unique identifier for this entry, i.e., its filename in the echemdb.

        EXAMPLES::

            >>> entry = Entry.create_examples()[0]
            >>> entry.identifier
            'alves_2011_electrochemistry_6010_p2_2a_solid'

        """
        return self.package.resources[0].name

    def __dir__(self):
        r"""
        Return the attributes of this entry.

        Implement to support tab-completion into the data package's descriptor.

        EXAMPLES::

            >>> entry = Entry.create_examples()[0]
            >>> dir(entry)
            ['__class__', '__delattr__', '__dict__', '__dir__', '__doc__', '__eq__', '__format__', '__ge__', '__getattr__', '__getattribute__', '__getitem__', '__gt__', '__hash__', '__init__', '__init_subclass__', '__le__', '__lt__', '__module__', '__ne__', '__new__', '__reduce__', '__reduce_ex__', '__repr__', '__setattr__', '__sizeof__', '__str__', '__subclasshook__', '__weakref__', '_descriptor', 'bibliography', 'create_examples', 'curator', 'df', 'electrochemical_system', 'figure_description', 'identifier', 'package', 'plot', 'profile', 'resources', 'source', 'yaml']

        """
        return list(set(dir(self._descriptor) + object.__dir__(self)))

    def __getattr__(self, name):
        r"""
        Return a property of the data package's descriptor.

        EXAMPLES::

            >>> entry = Entry.create_examples()[0]
            >>> entry.source
            {'version': 1, 'doi': 'https://doi.org/10.1039/C0CP01001D', 'bib': 'alves_2011_electrochemistry_6010', 'figure': '2a', 'curve': 'solid'}

        The returned descriptor can again be accessed in the same way::

            >>> entry.electrochemical_system.electrolyte.components[0].name
            'H2O'

        """
        return getattr(self._descriptor, name)

    def __getitem__(self, name):
        r"""
        Return a property of the data package's descriptor.

        EXAMPLES::

            >>> entry = Entry.create_examples()[0]
            >>> entry["source"]
            {'version': 1, 'doi': 'https://doi.org/10.1039/C0CP01001D', 'bib': 'alves_2011_electrochemistry_6010', 'figure': '2a', 'curve': 'solid'}

        """
        return self._descriptor[name]

    @property
    def _descriptor(self):
        return Descriptor(self.package.descriptor)

    def df(self, yunit=None):
        r"""
        Return the CSV resource attached to this entry as a data frame.

        EXAMPLES::

            >>> entry = Entry.create_examples()[0]
            >>> entry.df()
                         t         U         j
            0     0.000000 -0.103158 -0.099828
            1     0.100000 -0.098158 -0.091664
            ...

            >>> from astropy import units as u
            >>> entry.df(yunit=u.A / u.m**2)
                         t         U         j
            0     0.000000 -0.103158 -0.998277
            1     0.100000 -0.098158 -0.916644
            ...

        """
        from astropy import units as u
        if yunit is None:
            yunit = self.figure_description.current.unit
        if isinstance(yunit, str):
            yunit = u.Unit(yunit)

        import pandas
        df = pandas.read_csv(self.package.resources[0].raw_iter(stream=False))

        if 'j' in df.columns:
            df['j'] *= (u.A / u.m**2).to(yunit)
        if 'I' in df.columns:
            df['I'] *= (u.A).to(yunit)

        return df

    def __repr__(self):
        r"""
        Return a printable representation of this entry.

        EXAMPLES::

            >>> entry = Entry.create_examples()[0]
            >>> entry
            Entry('alves_2011_electrochemistry_6010_p2_2a_solid')

        """
        return f"Entry({repr(self.identifier)})"

    def plot(self, yunit=None):
        r"""
        Return a plot of the database in this data package.

        EXAMPLES::

            >>> entry = Entry.create_examples()[0]
            >>> entry.plot()
            Figure(...)

        """
        import plotly.graph_objects

        fig = plotly.graph_objects.Figure()
        df = self.df(yunit=yunit)
        fig.add_trace(plotly.graph_objects.Scatter(x=df['U'], y=df['j'], mode='lines'))
        fig.update_layout(template="simple_white", showlegend=True, autosize=True, width=450, height=350, margin=dict(l=70, r=70, b=70, t=70, pad=7))

        return fig

    @classmethod
    def create_examples(cls, name="alves_2011_electrochemistry_6010"):
        r"""
        Return some example entries for use in doctesting.

        The examples are built on-demand from data in echemdb's literature directory.

        EXAMPLES::

            >>> Entry.create_examples()
            [Entry('alves_2011_electrochemistry_6010_p2_2a_solid')]

        """
        import os.path

        source = os.path.join(
            os.path.dirname(__file__),
            '..',
            '..',
            '..',
            'literature',
            name)

        if not os.path.exists(source):
            raise ValueError(f"No subdirectory in literature/ for {name}, i.e., could not find {source}.")

        outdir = os.path.join(
            os.path.dirname(__file__),
            '..',
            '..',
            '..',
            'data',
            'generated',
            'svgdigitizer',
            name)

        if not os.path.exists(outdir):
            from glob import glob
            for yaml in glob(os.path.join(source, "*.yaml")):
                svg = os.path.splitext(yaml)[0] + ".svg"

                from svgdigitizer.test.cli import invoke
                from svgdigitizer.__main__ import cv
                invoke(cv, "--sampling_interval", ".005", "--package", "--metadata", yaml, svg, "--outdir", outdir)

        assert os.path.exists(outdir), f"Ran digitizer to generate {outdir}. But directory is still missing after invoking digitizer."

        from echemdb.data.local import collect_datapackages, collect_bibliography
        packages = collect_datapackages(outdir)
        bibliography = collect_bibliography(source)
        assert len(bibliography) == 1, f"No bibliography found for {name}."
        bibliography = next(iter(bibliography))

        if len(packages) == 0:
            raise ValueError(f"No literature data found for {name}. There is probably some outdated data in {outdir}.")

        return [Entry(package=package, bibliography=bibliography) for package in packages]
