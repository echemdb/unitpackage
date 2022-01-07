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
            ['__class__', '__delattr__', '__dict__', '__dir__', '__doc__', '__eq__', '__format__', '__ge__', '__getattr__', '__getattribute__', '__getitem__', '__gt__', '__hash__', '__init__', '__init_subclass__', '__le__', '__lt__', '__module__', '__ne__', '__new__', '__reduce__', '__reduce_ex__', '__repr__', '__setattr__', '__sizeof__', '__str__', '__subclasshook__', '__weakref__', '_descriptor', 'bibliography', 'create_examples', 'curator', 'df', 'electrochemical_system', 'figure_description', 'identifier', 'package', 'plot', 'profile', 'resources', 'source', 'x', 'x_unit', 'y', 'y_unit', 'yaml']

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

    def x(self):
        r"""
        Return the name of the variable on the x-axis, i.e., `"U"`.

        TODO: Adapt along with https://github.com/echemdb/svgdigitizer/issues/106.

        EXAMPLES::

            >>> entry = Entry.create_examples()[0]
            >>> entry.x()
            'U'

        """
        from astropy import units as u
        if u.Unit(self.figure_description.potential_scale.unit).is_equivalent('V'):
            return 'U'

    def y(self):
        r"""
        Return the name of the variable on the y-axis, i.e., `"j"` or `"I"`.

        TODO: Adapt along with https://github.com/echemdb/svgdigitizer/issues/106.

        EXAMPLES::

            >>> entry = Entry.create_examples()[0]
            >>> entry.y()
            'j'

        """
        from astropy import units as u

        if u.Unit(self.figure_description.current.unit).is_equivalent('A / m2'):
            return 'j' 
        if u.Unit(self.figure_description.current.unit).is_equivalent('A'):
            return 'I'

    def x_unit(self, xunit=None):
        r"""
        Return the unit on the x-axis as an astropy unit.

        EXAMPLES:

        Without parameters, SI units are returned::

            >>> entry = Entry.create_examples()[0]
            >>> entry.x_unit()
            Unit("V")

        When set to `"original"`, the original units of the published figure are returned::

            >>> entry.x_unit(xunit='original')
            Unit("V")

        Units can be specified explicitly::

            >>> entry = Entry.create_examples()[0]
            >>> entry.x_unit(xunit='mV')
            Unit("mV")

        """
        from astropy import units as u

        if xunit is None:
            xunit = u.V
        if xunit == 'original':
            xunit = self.figure_description.potential_scale.unit

        return u.Unit(xunit)

    def y_unit(self, yunit=None):
        r"""
        Return the unit of the y-axis as an astropy unit.

        EXAMPLES:

        Without parameters, SI units are returned::

            >>> entry = Entry.create_examples()[0]
            >>> entry.y_unit()
            Unit("A / m2")

        When set to `"original"`, the original units of the published figure are returned::

            >>> entry.y_unit(yunit='original')
            Unit("mA / cm2")

        Units can be specified explicitly::

            >>> entry = Entry.create_examples()[0]
            >>> entry.y_unit(yunit='uA / cm2')
            Unit("uA / cm2")

        """
        from astropy import units as u

        if yunit is None:
            if self.y() == 'j':
                yunit = u.A / u.m**2
            elif self.y() == 'I':
                yunit = u.A
            else:
                raise NotImplementedError("Unexpected naming of y axis.")

        if yunit == 'original':
            yunit = self.figure_description.current.unit

```suggestion
        return u.Unit(yunit)

    def df(self, xunit=None, yunit=None):
        r"""
        Return the CSV resource attached to this entry as a data frame.

        If the x and y-units are not specified, all values
        are in SI units. The data frame can also be returned 
        with the original figure units or with custom units as shown in the following examples.

        EXAMPLES:
        
        A data frame in SI units::

            >>> entry = Entry.create_examples()[0]
            >>> entry.df()
                         t         U         j
            0     0.000000 -0.103158 -0.998277
            1     0.100000 -0.098158 -0.916644
            ...

        A data frame in the original units of the figure::

            >>> entry.df(xunit='original', yunit='original')
                         t         U         j
            0     0.000000 -0.103158 -0.099828
            1     0.100000 -0.098158 -0.091664
            ...

        A data frame with custom units::

            >>> from astropy import units as u
            >>> entry.df(xunit='mV', yunit=u.uA / u.cm**2)
                         t           U          j
            0     0.000000 -103.158422 -99.827664
            1     0.100000  -98.158422 -91.664367
            ...

        """
        import pandas as pd

        df = pd.read_csv(self.package.resources[0].raw_iter(stream=False))

        if xunit or yunit:
            df[self.x()] *= self.x_unit().to(self.x_unit(xunit))
            df[self.y()] *= self.y_unit().to(self.y_unit(yunit))
        
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

    def plot(self, xunit=None, yunit=None):
        r"""
        Return a plot of the data in this data package.

        EXAMPLES::

            >>> entry = Entry.create_examples()[0]
            >>> entry.plot()
            Figure(...)

        """
        import plotly.graph_objects

        xunit = self.x_unit(xunit)
        yunit = self.y_unit(yunit)

        df = self.df(xunit=xunit, yunit=yunit)

        fig = plotly.graph_objects.Figure()

        fig.add_trace(plotly.graph_objects.Scatter(x=df[self.x()], y=df[self.y()], mode='lines', name=f'Fig. {self.source.figure}: {self.source.curve}'))

        reference = f' vs {self.figure_description.potential_scale.reference}' if self.figure_description.potential_scale.reference else ''

        fig.update_layout(template="simple_white", showlegend=True, autosize=True, width=600, height=400, 
                            margin=dict(l=70, r=70, b=70, t=70, pad=7),
                            xaxis_title=f"{self.x()} [{xunit}{reference}]",
                            yaxis_title=f"{self.y()} [{yunit}]")

        fig.update_xaxes(showline=True, mirror=True)
        fig.update_yaxes(showline=True, mirror=True)

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

        # We now might have to digitize some files on demand. When running
        # tests in parallel, this introduces a race condition that we avoid
        # with a global lock in the file system.
        lockfile = f"{outdir}.lock"
        os.makedirs(os.path.dirname(lockfile), exist_ok=True)

        from filelock import FileLock
        with FileLock(lockfile):
            if not os.path.exists(outdir):
                from glob import glob
                for yaml in glob(os.path.join(source, "*.yaml")):
                    svg = os.path.splitext(yaml)[0] + ".svg"

                    from svgdigitizer.test.cli import invoke
                    from svgdigitizer.__main__ import digitize_cv
                    invoke(digitize_cv, "--sampling_interval", ".005", "--package", "--metadata", yaml, svg, "--outdir", outdir)

                assert os.path.exists(outdir), f"Ran digitizer to generate {outdir}. But directory is still missing after invoking digitizer."
                assert any(os.scandir(outdir)), f"Ran digitizer to generate {outdir}. But the directory generated is empty after invoking digitizer."

        from echemdb.data.local import collect_datapackages, collect_bibliography
        packages = collect_datapackages(outdir)
        bibliography = collect_bibliography(source)
        assert len(bibliography) == 1, f"No bibliography found for {name}."
        bibliography = next(iter(bibliography))

        if len(packages) == 0:
            from glob import glob
            raise ValueError(f"No literature data found for {name}. The directory for this data {outdir} exists. But we could not find any datapackages in there. There is probably some outdated data in {outdir}. The contents of that directory are: { glob(os.path.join(outdir,'**')) }")

        return [Entry(package=package, bibliography=bibliography) for package in packages]
