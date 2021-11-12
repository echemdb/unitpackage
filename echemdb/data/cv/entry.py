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
    def __init__(self, package):
        self.package = package

    @property
    def identifier(self):
        r"""
        Return a unique identifier for this entry, i.e., its filename in the echemdb.

        EXAMPLES::

            >>> entry = Entry.create_examples()[0]
            >>> entry.identifier
            'Engstfeld_2018_polycrystalline_17743_4b_1'

        """
        return self.package.resources[0].name

    def __dir__(self):
        r"""
        Return the attributes of this entry.

        Implement to support tab-completion into the data package's descriptor.

        EXAMPLES::

            >>> entry = Entry.create_examples()[0]
            >>> dir(entry)
            ['__class__', '__delattr__', '__dict__', '__dir__', '__doc__', '__eq__', '__format__', '__ge__', '__getattr__', '__getattribute__', '__getitem__', '__gt__', '__hash__', '__init__', '__init_subclass__', '__le__', '__lt__', '__module__', '__ne__', '__new__', '__reduce__', '__reduce_ex__', '__repr__', '__setattr__', '__sizeof__', '__str__', '__subclasshook__', '__weakref__', '_descriptor', 'create_examples', 'curator', 'df', 'electrochemical_system', 'electrochemical_system_metadata', 'figure_description', 'identifier', 'package', 'plot', 'profile', 'resources', 'source', 'version']

        """
        return list(set(dir(Descriptor(self.package.descriptor)) + object.__dir__(self)))

    def __getattr__(self, name):
        r"""
        Return a property of the data package's descriptor.

        EXAMPLES::

            >>> entry = Entry.create_examples()[0]
            >>> entry.source
            {'doi': 'https://doi.org/10.1002/chem.201803418', 'bib': 'Engstfeld_2018_Polycrystalline_17747', 'figure': '4b', 'curve': 1}

        """
        return getattr(Descriptor(self.package.descriptor), name)

    def __getitem__(self, name):
        r"""
        Return a property of the data package's descriptor.

        EXAMPLES::

            >>> entry = Entry.create_examples()[0]
            >>> entry["source"]
            {'doi': 'https://doi.org/10.1002/chem.201803418', 'bib': 'Engstfeld_2018_Polycrystalline_17747', 'figure': '4b', 'curve': 1}
        """
        return Descriptor(self.package.descriptor)[name]

    def df(self, yunit=None):
        r"""
        Return the CSV resource attached to this entry as a data frame.

        EXAMPLES::

            >>> entry = Entry.create_examples()[0]
            >>> entry.df()
                         t         U         j
            0     0.000000 -0.196962  4.300884
            1     0.011368 -0.196393  5.140820
            ...

            >>> from astropy import units as u
            >>> entry.df(yunit=u.A / u.m**2)
                         t         U         j
            0     0.000000 -0.196962  0.043009
            1     0.011368 -0.196393  0.051408
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
            Entry('Engstfeld_2018_polycrystalline_17743_4b_1')

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
    def create_examples(cls, name="Engstfeld_2018_polycristalline_17743"):
        r"""
        Return some example entries for use in doctesting.

        The examples are built on-demand from data in echemdb's literature directory.

        EXAMPLES::

            >>> Entry.create_examples()
            [Entry('Engstfeld_2018_polycrystalline_17743_4b_1')]

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

        from echemdb.data.local import collect_datapackages
        packages = collect_datapackages(outdir)

        if len(packages) == 0:
            raise ValueError(f"No literature data found for {name}. There is probably some outdated data in {outdir}.")

        return [Entry(package) for package in packages]

    def electrochemical_system_metadata(self):
        r'''Return the electrochemical metadata as string

        EXAMPLES::

            >>> entry = Entry.create_examples()[0]
            >>> entry.electrochemical_system_metadata()
            'electrodes:\n  configuration: three\n  counter electrode:\n    crystallographic orientation: poly\n    material: Au\n    shape: mesh\n  reference electrode:\n    source:\n      supplier: homemade\n    type: RHE\n  working electrode:\n    crystallographic orientation: 100\n    geometric electrolyte contact area:\n      unit: cm-2\n      value: null\n    material: Cu\n    preparation procedure: sputter and heating under UHV conditions\n    shape:\n      diameter:\n        unit: mm\n        value: 4.4\n      height:\n        unit: mm\n        value: 2\n      type: head shaped\n    source:\n      LOT: null\n      supplier: Mateck\nelectrolyte:\n  components:\n  - name: water\n    proportion:\n      unit: volume percent\n      value: 100\n    source:\n      quality: ultrapure water\n      refinement: Millipore MilliQ\n      total organic carbon:\n        unit: none\n        value: none\n    sum formula: H2O\n    type: solvent\n  - concentration:\n      unit: M\n      value: 0.1\n    name: potassium hydroxide\n    source:\n      LOT: null\n      supplier: Merck Suprapur\n    sum formula: KOH\n    type: alkaline\n  ph:\n    uncertainty: none\n    value: 13\n  temperature:\n    unit: K\n    value: 298.15\n  type: aq\n'

        '''
        import yaml
        meta = self.package.to_dict() # `to_dict` is apparently deprecated. Find another way to turn the package into a dict.
        return yaml.dump(meta['electrochemical system'])

class Descriptor:
    r"""
    Wrapper for a data package's descriptor to make searching in metadata easier.

    EXAMPLES::

        >>> Descriptor({'a': 0})
        {'a': 0}

    """
    def __init__(self, descriptor):
        self._descriptor = descriptor

    def __dir__(self):
        r"""
        Return the attributes of this descriptor.

        Implemented to allow tab-completion in a package's descriptor.

        EXAMPLES::

            >>> descriptor = Descriptor({'a': 0})
            >>> 'a' in dir(descriptor)
            True

        """
        return list(key.replace(' ', '_') for key in self._descriptor.keys()) + object.__dir__(self)

    def __getattr__(self, name):
        r"""
        Return the attribute `name` of the descriptor.

        EXAMPLES::

            >>> descriptor = Descriptor({'a': 0})
            >>> descriptor.a
            0

        """
        name = name.replace('_', ' ')
        if name in self._descriptor:
            value = self._descriptor[name]
            return Descriptor(value) if isinstance(value, dict) else value

        raise AttributeError(f"Descriptor has no entry {name}. Did you mean one of {list(self._descriptor.keys())}?")

    def __getitem__(self, name):
        r"""
        Return the attribute `name` of the descriptor.

        EXAMPLES::

            >>> descriptor = Descriptor({'a': 0})
            >>> descriptor["a"]
            0

        """
        if name in self._descriptor:
            value = self._descriptor[name]
            return Descriptor(value) if isinstance(value, dict) else value

        raise KeyError(f"Descriptor has no entry {name}. Did you mean one of {list(self._descriptor.keys())}?")

    def __repr__(self):
        r"""
        Return a printable representation of this descriptor.

        EXAMPLES::

            >>> Descriptor({})
            {}

        """
        return repr(self._descriptor)

    def create_yaml(self):
        import yaml
        return yaml.dump(self._descriptor)
