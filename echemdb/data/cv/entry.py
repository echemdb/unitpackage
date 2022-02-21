r"""
A Data Package decribing a Cyclic Voltammogram.

These are the individual elements of a :class:`Database`.

EXAMPLES:

Data Packages containing published data, 
also contain information on the source of the data.::

    >>> from echemdb.data.cv.database import Database
    >>> db = Database()
    >>> entry = db['alves_2011_electrochemistry_6010_p2_f2a_solid']
    >>> entry.bibliography  # doctest: +NORMALIZE_WHITESPACE +REMOTE_DATA
    Entry('article',
      fields=[
        ('title', 'Electrochemistry at Ru(0001) in a flowing CO-saturated electrolyte—reactive and inert adlayer phases'), 
        ('journal', 'Physical Chemistry Chemical Physics'), 
        ('volume', '13'), 
        ('number', '13'), 
        ('pages', '6010--6021'), 
        ('year', '2011'), 
        ('publisher', 'Royal Society of Chemistry'), 
        ('abstract', 'We investigated the electrochemical oxidation and reduction processes on ultrahigh vacuum prepared, smooth and structurally well-characterized Ru(0001) electrodes in a CO-saturated and, for comparison, in a CO-free flowing HClO4 electrolyte by electrochemical methods and by comparison with previous structural data. Structure and reactivity of the adsorbed layers are largely governed by a critical potential of E = 0.57 V, which determines the onset of Oad formation on the COad saturated surface in the positive-going scan and of Oadreduction in the negative-going scan. Oad formation proceeds via nucleation and 2D growth of high-coverage Oad islands in a surrounding COad phase, and it is connected with COadoxidation at the interface between the two phases. In the negative-going scan, mixed (COad + Oad) phases, most likely a (2 $\\times$ 2)-(CO + 2O) and a (2$\\times$2)-(2CO + O), are proposed to form at E $<$ 0.57 V by reduction of the Oad-rich islands and CO adsorption into the resulting lower-density Oad structures. CO bulk oxidation rates in the potential range E $>$ 0.57 V are low, but significantly higher than those observed during oxidation of pre-adsorbed CO in the CO-free electrolyte. We relate this to high local COad coverages due to CO adsorption in the CO-saturated electrolyte, which lowers the CO adsorption energy and thus the barrier for COadoxidation during CO bulk oxidation.')],
      persons=OrderedCaseInsensitiveDict([('author', [Person('Alves, Otavio B'), Person('Hoster, Harry E'), Person('Behm, Rolf J{\\"u}rgen')])]))

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
            'alves_2011_electrochemistry_6010_p2_f2a_solid'

        """
        return self.package.resources[0].name

    def __dir__(self):
        r"""
        Return the attributes of this entry.

        Implement to support tab-completion into the data package's descriptor.

        EXAMPLES::

            >>> entry = Entry.create_examples()[0]
            >>> dir(entry)
            ['__class__', '__delattr__', '__dict__', '__dir__', '__doc__', '__eq__', '__format__', '__ge__', '__getattr__', '__getattribute__', '__getitem__', '__gt__', '__hash__', '__init__', '__init_subclass__', '__le__', '__lt__', '__module__', '__ne__', '__new__', '__reduce__', '__reduce_ex__', '__repr__', '__setattr__', '__sizeof__', '__str__', '__subclasshook__', '__weakref__', '_descriptor', 'bibliography', 'citation', 'create_examples', 'curation', 'data_description', 'df', 'experimental', 'figure_description', 'identifier', 'package', 'plot', 'profile', 'resources', 'source', 'system', 'version', 'x', 'x_unit', 'y', 'y_unit', 'yaml']

        """
        return list(set(dir(self._descriptor) + object.__dir__(self)))

    def __getattr__(self, name):
        r"""
        Return a property of the data package's descriptor.

        EXAMPLES::

            >>> entry = Entry.create_examples()[0]
            >>> entry.source
            {'citation key': 'alves_2011_electrochemistry_6010', 'curve': 'solid', 'url': 'https://doi.org/10.1039/C0CP01001D', 'figure': '2a', 'version': 1}

        The returned descriptor can again be accessed in the same way::

            >>> entry.system.electrolyte.components[0].name
            'H2O'

        """
        return getattr(self._descriptor, name)

    def __getitem__(self, name):
        r"""
        Return a property of the data package's descriptor.

        EXAMPLES::

            >>> entry = Entry.create_examples()[0]
            >>> entry["source"]
            {'citation key': 'alves_2011_electrochemistry_6010', 'curve': 'solid', 'url': 'https://doi.org/10.1039/C0CP01001D', 'figure': '2a', 'version': 1}

        """
        return self._descriptor[name]

    @property
    def _descriptor(self):
        return Descriptor(self.package.descriptor)

    def citation(self, backend='text'):
        r"""
        Return a formatted reference for the entry's bibliography such as:

        J. Doe, et al., Journal Name, volume (YEAR) page, "Title"

        Rendering default is plain text 'text', but can be changed to any format
        supported by pybtex, such as markdown 'md', 'latex' or 'html'.

        EXAMPLES::

            >>> entry = Entry.create_examples()[0]
            >>> entry.citation(backend='text')
            'O. B. Alves et al. Electrochemistry at Ru(0001) in a flowing CO-saturated electrolyte—reactive and inert adlayer phases. Physical Chemistry Chemical Physics, 13(13):6010–6021, 2011.'
            >>> print(entry.citation(backend='md'))
            O\. B\. Alves *et al\.*
            *Electrochemistry at Ru\(0001\) in a flowing CO\-saturated electrolyte—reactive and inert adlayer phases*\.
            *Physical Chemistry Chemical Physics*, 13\(13\):6010–6021, 2011\.

            >>> entry = Entry.create_examples(name="gomez-marin_2012_surface_558")[0]
            >>> entry.citation(backend='text')
            'A. M. Gómez-Marín et al. Pt(111) surface disorder kinetics in perchloric acid solutions and the influence of specific anion adsorption. Electrochimica acta, 82:558–569, 2012.'

            >>> print(entry.citation(backend='md'))
            A\. M\. Gómez\-Marín *et al\.*
            *Pt\(111\) surface disorder kinetics in perchloric acid solutions and the influence of specific anion adsorption*\.
            *Electrochimica acta*, 82:558–569, 2012\.

        """
        from pybtex.style.formatting.unsrt import Style

        # TODO:: Remove `class EchemdbStyle` from citation and improve citation style. (see #104)
        class EchemdbStyle(Style):
            def format_names(self, role, as_sentence=True):
                from pybtex.style.template import node

                @node
                def names(_, context, role):
                    persons = context["entry"].persons[role]
                    style = context["style"]

                    names = [style.format_name(person, style.abbreviate_names) for person in persons]

                    if len(names) == 1:
                        return names[0].format_data(context)
                    else:
                        from pybtex.style.template import words, tag
                        return words(sep=' ')[names[0], tag('i')['et al.']].format_data(context)

                names = names(role)

                from pybtex.style.template import sentence
                return sentence[names] if as_sentence else names

            def format_title(self, e, which_field, as_sentence=True):
                from pybtex.style.template import field, tag, sentence
                title = tag('i')[field(which_field)]
                return sentence[title] if as_sentence else title

        return EchemdbStyle(abbreviate_names=True).format_entry("unused", self.bibliography).text.render_as(backend)

    def x(self):
        r"""
        Return the name of the variable on the x-axis, i.e., ``"E"``.

        EXAMPLES::

            >>> entry = Entry.create_examples()[0]
            >>> entry.x()
            'E'

        """
        from astropy import units as u

        axis = getattr(self.data_description, 'axes', {})['E']

        if not u.Unit(axis.unit).is_equivalent('V'):
            raise ValueError("The variable on the x-axis denoted as 'E', is not convertible to 'V'.")
        
        return 'E'

    def y(self):
        r"""
        Return the name of the variable on the y-axis, i.e., ``"j"`` or ``"I"``.

        EXAMPLES::

            >>> entry = Entry.create_examples()[0]
            >>> entry.y()
            'j'

        """
        from astropy import units as u

        axes = getattr(self.data_description, 'axes', {})

        variables = [variable for variable in dir(axes) if variable in ['I', 'j']]

        if len(variables) != 1:
            raise KeyError("Exactly one of the axes must have variable 'I' or 'j'.")

        variable = variables[0]

        if variable == 'I':
            if not u.Unit(axes[variable].unit).is_equivalent('A'):
                raise Exception("Unit on I axis must be convertible to A.")

        if variable == 'j':
            if not u.Unit(axes[variable].unit).is_equivalent('A / m2'):
                raise Exception("Unit on j axis must be convertible to A / m².")

        return variable

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
            xunit = self.figure_description.axes.E.unit

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
            yunit = self.figure_description.axes.j.unit or self.figure_description.axes.I.unit

        return u.Unit(yunit)

    def rescale_original(self):
        # self.rescale(parse original axes units)
        pass

    def rescale(self, new_units={}):
        r"""
        Returns an Entry with rescaled axes with the specified units. 
        Provide a dict, where the key is the axis name and the value 
        the new unit, such as `{'j':'uA / cm2', 't':'h'}.
            
        EXAMPLES:

        The axes units of the original entry.::

            >>> entry = Entry.create_examples()[0]
            >>> entry.data_description.fields # doctest: +NORMALIZE_WHITESPACE
            [{'name': 't', 'unit': 's', 'type': 'number', 'format': 'default'},
            {'name': 'E', 'unit': 'V', 'reference': 'RHE', 'type': 'number', 'format': 'default'},
            {'name': 'j', 'unit': 'A / m2', 'type': 'number', 'format': 'default'}]

        A rescaled entry with updated axes units::

            >>> rescaled_entry = entry.rescale({'j':'uA / cm2', 't':'h'})
            >>> rescaled_entry.data_description.fields # doctest: +NORMALIZE_WHITESPACE
            [{'name': 't', 'unit': 'h', 'type': 'number', 'format': 'default'},
            {'name': 'E', 'unit': 'V', 'reference': 'RHE', 'type': 'number', 'format': 'default'},
            {'name': 'j', 'unit': 'uA / cm2', 'type': 'number', 'format': 'default'}]

        """
        from copy import deepcopy

        package = deepcopy(self.package)
        fields = package.descriptor['resources'][0]['schema']['fields']

        for idx, field in enumerate(fields):
            if field['name'] in new_units.keys():
                    package.descriptor['resources'][0]['schema']['fields'][idx]['unit'] = new_units[field['name']]
                    package.descriptor['data description']['fields'][idx]['unit'] = new_units[field['name']]

        # print(self.package.descriptor['resources'][0]['schema']['fields'])
        # print(package.descriptor['resources'][0]['schema']['fields'])

        from datapackage import Package
        
        return Entry(package=Package(package.to_dict()), bibliography=self.bibliography)
    
    @property
    def df(self):
        r"""
        Return the CSV resource attached to this entry as a data frame,
        based on the units given in `entry.data_description.fields`.

        EXAMPLES:
        
        A data frame of the CSV resource::

            >>> entry = Entry.create_examples()[0]
            >>> entry.df
                         t         E         j
            0     0.000000 -0.103158 -0.998277
            1     0.100000 -0.098158 -0.916644
            ...

        The axes units and description can be found in ``entry.data_description.fields``::

            >>> entry.data_description.fields # doctest: +NORMALIZE_WHITESPACE
            [{'name': 't', 'unit': 's', 'type': 'number', 'format': 'default'},
            {'name': 'E', 'unit': 'V', 'reference': 'RHE', 'type': 'number', 'format': 'default'},
            {'name': 'j', 'unit': 'A / m2', 'type': 'number', 'format': 'default'}]

        """
        
        # A data frame in the original units of the figure::

        #     >>> entry.df(xunit='original', yunit='original')
        #                  t         E         j
        #     0     0.000000 -0.103158 -0.099828
        #     1     0.100000 -0.098158 -0.091664
        #     ...

        # A data frame with custom units::

        #     >>> from astropy import units as u
        #     >>> entry.df(xunit='mV', yunit=u.uA / u.cm**2)
        #                  t           E          j
        #     0     0.000000 -103.158422 -99.827664
        #     1     0.100000  -98.158422 -91.664367
        #     ...

        import pandas as pd

        # if xunit or yunit:
        #     df[self.x()] *= self.x_unit().to(self.x_unit(xunit))
        #     df[self.y()] *= self.y_unit().to(self.y_unit(yunit))
        
        return pd.read_csv(self.package.resources[0].raw_iter(stream=False))

    def __repr__(self):
        r"""
        Return a printable representation of this entry.

        EXAMPLES::

            >>> entry = Entry.create_examples()[0]
            >>> entry
            Entry('alves_2011_electrochemistry_6010_p2_f2a_solid')

        """
        return f"Entry({repr(self.identifier)})"

    def plot(self, xunit=None, yunit=None):
        r"""
        Return a plot of the data in this data package in SI units.

        EXAMPLES::

            >>> entry = Entry.create_examples()[0]
            >>> entry.plot()
            Figure(...)

        The plot can also be returned with the axis units of the original figure::

            >>> entry = Entry.create_examples()[0]
            >>> entry.plot(xunit='original', yunit='original')
            Figure(...)

        The plot can also be returned with custom axis units, where 
        `xunit` should be convertible to `V` and 
        `yunit` convertible to `A` or `A / m2`.::

            >>> entry = Entry.create_examples()[0]
            >>> entry.plot(xunit='mV', yunit='uA / cm2')
            Figure(...)

        """
        import plotly.graph_objects

        xunit = self.x_unit(xunit)
        yunit = self.y_unit(yunit)

        df = self.df(xunit=xunit, yunit=yunit)

        fig = plotly.graph_objects.Figure()

        fig.add_trace(plotly.graph_objects.Scatter(x=df[self.x()], y=df[self.y()], mode='lines', name=f'Fig. {self.source.figure}: {self.source.curve}'))

        reference = f' vs {self.data_description.axes.E.reference}' if self.data_description.axes.E.reference else ''

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
            [Entry('alves_2011_electrochemistry_6010_p2_f2a_solid')]

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
                    invoke(digitize_cv, "--sampling-interval", ".005", "--package", "--metadata", yaml, svg, "--outdir", outdir)

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
