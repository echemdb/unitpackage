r"""
A Data Package describing tabulated data for which the units of the
column names (`pandas <https://pandas.pydata.org/>`_)
or fields (`frictionless <https://framework.frictionlessdata.io/>`_) are known
and the resource has additional  metadata describing the underlying data.

A description of such datapackags can be found in the documentation
in :doc:`/usage/unitpackage`.

Datapackages are the individual elements of a :class:`~unitpackage.collection.Collection` and
are denoted as ``entry``.

EXAMPLES:

Metadata included in an entries resource is accessible as an attribute::

    >>> entry = Entry.create_examples()[0]
    >>> entry.source # doctest: +ELLIPSIS +NORMALIZE_WHITESPACE
    {'citation key': 'alves_2011_electrochemistry_6010',
    'url': 'https://doi.org/10.1039/C0CP01001D',
    'figure': '1a',
    'curve': 'solid',
    'bibdata': '@article{alves_2011_electrochemistry_6010,...}

The data of the resource can be called as a pandas dataframe::

    >>> entry = Entry.create_examples()[0]
    >>> entry.df
                  t         E         j
    0      0.000000 -0.103158 -0.998277
    1      0.020000 -0.102158 -0.981762
    ...

Data Packages containing published data,
also contain information on the source of the data.::

    >>> from unitpackage.collection import Collection
    >>> db = Collection.create_example()
    >>> entry = db['alves_2011_electrochemistry_6010_f1a_solid']
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
        ('abstract', 'We investigated ...')],
      persons=OrderedCaseInsensitiveDict([('author', [Person('Alves, Otavio B'), Person('Hoster, Harry E'), Person('Behm, Rolf J{\\"u}rgen')])]))

"""

# ********************************************************************
#  This file is part of unitpackage.
#
#        Copyright (C) 2021-2024 Albert Engstfeld
#        Copyright (C)      2021 Johannes Hermann
#        Copyright (C) 2021-2022 Julian Rüth
#        Copyright (C)      2021 Nicolas Hörmann
#
#  unitpackage is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  unitpackage is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with unitpackage. If not, see <https://www.gnu.org/licenses/>.
# ********************************************************************
import logging
import os.path

from unitpackage.descriptor import Descriptor

logger = logging.getLogger("unitpackage")


class Entry:
    r"""
    A `frictionless data package <https://github.com/frictionlessdata/framework>`_
    describing tabulated data.

    EXAMPLES:

    Entries can be directly created::

        >>> from unitpackage.local import collect_datapackage
        >>> from unitpackage.entry import Entry
        >>> entry = Entry(collect_datapackage('./examples/no_bibliography/no_bibliography.json'))
        >>> entry
        Entry('no_bibliography')

    or more simply::

        >>> from unitpackage.entry import Entry
        >>> entry = Entry.from_local('./examples/no_bibliography/no_bibliography.json')
        >>> entry
        Entry('no_bibliography')

    Entries can also be created by other means such as,
    a CSV ``Entry.from_csv`` or a pandas dataframe ``Entry.from_df``.

    Normally, entries are obtained by opening a :class:`~unitpackage.collection.Collection` of entries::

        >>> from unitpackage.collection import Collection
        >>> collection = Collection.create_example()
        >>> entry = next(iter(collection))

    """

    def __init__(self, package):
        self.package = package

    @property
    def identifier(self):
        r"""
        Return a unique identifier for this entry, i.e., its basename.

        EXAMPLES::

            >>> entry = Entry.create_examples()[0]
            >>> entry.identifier
            'alves_2011_electrochemistry_6010_f1a_solid'

        """
        return self.package.resources[0].name

    def __dir__(self):
        r"""
        Return the attributes of this entry.

        Implement to support tab-completion into the data package's descriptor.

        EXAMPLES::

            >>> entry = Entry.create_examples()[0]
            >>> dir(entry) # doctest: +ELLIPSIS +NORMALIZE_WHITESPACE
            [... 'bibliography', 'citation', 'create_examples', 'curation',
            'data_description', 'df', 'experimental', 'field_unit', 'figure_description',
            'from_csv', 'from_df', 'from_local', 'identifier', 'package',  'plot',
            'rename_fields', 'rescale', 'save', 'source', 'system', 'yaml']

        """
        return list(set(dir(self._descriptor) + object.__dir__(self)))

    def __getattr__(self, name):
        r"""
        Return a property of the data package's descriptor.

        EXAMPLES::

            >>> entry = Entry.create_examples()[0]
            >>> entry.source # doctest: +ELLIPSIS +NORMALIZE_WHITESPACE
            {'citation key': 'alves_2011_electrochemistry_6010',
            'url': 'https://doi.org/10.1039/C0CP01001D',
            'figure': '1a',
            'curve': 'solid',
            'bibdata': '@article{alves_2011_electrochemistry_6010,...}

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
            >>> entry["source"] # doctest: +NORMALIZE_WHITESPACE
            {'citation key': 'alves_2011_electrochemistry_6010',
            'url': 'https://doi.org/10.1039/C0CP01001D',
            'figure': '1a',
            'curve': 'solid',
            'bibdata': '@article{alves_2011_electrochemistry_6010,...}

        """
        return self._descriptor[name]

    @property
    def _descriptor(self):
        return Descriptor(self.package.resources[0].custom["metadata"]["echemdb"])

    @property
    def _metadata(self):
        r"""
        Returns the metadata named "echemdb" nested within a resource named "echemdb".

        EXAMPLES::

            >>> entry = Entry.create_examples()[0]
            >>> entry._metadata # doctest: +NORMALIZE_WHITESPACE
            {...'source': {'citation key': 'alves_2011_electrochemistry_6010',...}

        """
        return self.package.resources[0].custom["metadata"]["echemdb"]

    @property
    def bibliography(self):
        r"""
        Return a pybtex bibliography object.

        EXAMPLES::

            >>> entry = Entry.create_examples()[0]
            >>> entry.bibliography # doctest: +NORMALIZE_WHITESPACE
            Entry('article',
            fields=[
                ('title', ...
                ...

            >>> entry_no_bib = Entry.create_examples(name="no_bibliography")[0]
            >>> entry_no_bib.bibliography
            ''

        """
        metadata = self._metadata.setdefault("source", {})
        citation = metadata.setdefault("bibdata", "")

        if not citation:
            logger.warning(f"Entry with name {self.identifier} has no bibliography.")
            return citation

        from pybtex.database import parse_string

        bibliography = parse_string(citation, "bibtex")
        return bibliography.entries[self.source.citation_key]

    def citation(self, backend="text"):
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

        """
        from pybtex.style.formatting.unsrt import Style

        # TODO:: Remove `class EchemdbStyle` from citation and improve citation style. (see #104)
        class EchemdbStyle(Style):
            r"""
            A citation style for the echemdb website.
            """

            def format_names(self, role, as_sentence=True):
                from pybtex.style.template import node

                @node
                def names(_, context, role):
                    persons = context["entry"].persons[role]
                    style = context["style"]

                    names = [
                        style.format_name(person, style.abbreviate_names)
                        for person in persons
                    ]

                    if len(names) == 1:
                        return names[0].format_data(context)

                    from pybtex.style.template import tag, words

                    # pylint: disable=no-value-for-parameter
                    return words(sep=" ")[names[0], tag("i")["et al."]].format_data(
                        context
                    )

                # pylint: disable=no-value-for-parameter
                names = names(role)

                from pybtex.style.template import sentence

                return sentence[names] if as_sentence else names

            def format_title(self, e, which_field, as_sentence=True):
                from pybtex.style.template import field, sentence, tag

                # pylint: disable=no-value-for-parameter
                title = tag("i")[field(which_field)]
                return sentence[title] if as_sentence else title

        return (
            EchemdbStyle(abbreviate_names=True)
            .format_entry("unused", self.bibliography)
            .text.render_as(backend)
        )

    def field_unit(self, field_name):
        r"""
        Return the unit of the ``field_name`` of the ``echemdb`` resource.

        EXAMPLES::

            >>> entry = Entry.create_examples()[0]
            >>> entry.field_unit('E')
            'V'

        """
        return (
            self.package.get_resource("echemdb")
            .schema.get_field(field_name)
            .custom["unit"]
        )

    def rescale(self, units):
        r"""
        Returns a rescaled :class:`~unitpackage.entry.Entry` with axes in the specified ``units``.
        Provide a dict, where the key is the axis name and the value
        the new unit, such as `{'j': 'uA / cm2', 't': 'h'}`.

        EXAMPLES:

        The units without any rescaling::

            >>> entry = Entry.create_examples()[0]
            >>> entry.package.get_resource('echemdb').schema.fields
            [{'name': 't', 'type': 'number', 'unit': 's'},
            {'name': 'E', 'type': 'number', 'unit': 'V', 'reference': 'RHE'},
            {'name': 'j', 'type': 'number', 'unit': 'A / m2'}]

        A rescaled entry using different units::

            >>> rescaled_entry = entry.rescale({'j':'uA / cm2', 't':'h'})
            >>> rescaled_entry.package.get_resource('echemdb').schema.fields
            [{'name': 't', 'type': 'number', 'unit': 'h'},
            {'name': 'E', 'type': 'number', 'unit': 'V', 'reference': 'RHE'},
            {'name': 'j', 'type': 'number', 'unit': 'uA / cm2'}]

        The values in the data frame are scaled to match the new units::

            >>> rescaled_entry.df
                         t         E          j
            0     0.000000 -0.103158 -99.827664
            1     0.000006 -0.102158 -98.176205
            ...

        """
        from collections.abc import Mapping

        if not isinstance(units, Mapping):
            raise ValueError(
                "'units' must have the format {'dimension': 'new unit'}, e.g., `{'j': 'uA / cm2', 't': 'h'}`"
            )

        if not units:
            units = {}

        from astropy import units as u
        from frictionless import Package, Resource

        package = Package(self.package.to_dict())
        fields = self.package.get_resource("echemdb").schema.fields
        df = self.df.copy()

        for field in fields:
            if field.name in units:
                df[field.name] *= u.Unit(field.custom["unit"]).to(
                    u.Unit(units[field.name])
                )
                package.get_resource("echemdb").schema.update_field(
                    field.name, {"unit": units[field.name]}
                )

        # create a new dataframe resource
        df_resource = Resource(df)
        df_resource.infer()
        # update units in the schema of the df resource
        df_resource.schema = package.get_resource("echemdb").schema

        df_resource.name = "echemdb"

        # Remove the original echemdb resource and
        # add a new echemdb resource to the new entry
        package.remove_resource("echemdb")

        entry = type(self)(package=package)

        entry.package.add_resource(df_resource)

        return entry

    @property
    def df(self):
        r"""
        Return the data of this entry as a data frame.

        EXAMPLES::

            >>> entry = Entry.create_examples()[0]
            >>> entry.df
                          t         E         j
            0      0.000000 -0.103158 -0.998277
            1      0.020000 -0.102158 -0.981762
            ...

        The units and descriptions of the axes in the data frame can be recovered::

            >>> entry.package.get_resource('echemdb').schema.fields # doctest: +NORMALIZE_WHITESPACE
            [{'name': 't', 'type': 'number', 'unit': 's'},
            {'name': 'E', 'type': 'number', 'unit': 'V', 'reference': 'RHE'},
            {'name': 'j', 'type': 'number', 'unit': 'A / m2'}]

        """
        return self.package.get_resource("echemdb").data

    def __repr__(self):
        r"""
        Return a printable representation of this entry.

        EXAMPLES::

            >>> entry = Entry.create_examples()[0]
            >>> entry
            Entry('alves_2011_electrochemistry_6010_f1a_solid')

        """
        return f"Entry({repr(self.identifier)})"

    @classmethod
    def create_examples(cls, name=""):
        r"""
        Return some example entries for use in automated tests.

        The examples are created from datapackages in the unitpackage's examples directory.
        These are only available from the development environment.

        EXAMPLES::

            >>> Entry.create_examples()
            [Entry('alves_2011_electrochemistry_6010_f1a_solid'), Entry('engstfeld_2018_polycrystalline_17743_f4b_1'), Entry('no_bibliography')]

        An entry without associated BIB file.

            >>> Entry.create_examples(name="no_bibliography")
            [Entry('no_bibliography')]

        """
        example_dir = os.path.join(os.path.dirname(__file__), "..", "examples", name)

        if not os.path.exists(example_dir):
            raise ValueError(
                f"No subdirectory in examples/ for {name}, i.e., could not find {example_dir}."
            )

        from unitpackage.local import collect_datapackages

        packages = collect_datapackages(example_dir)

        if len(packages) == 0:
            from glob import glob

            raise ValueError(
                f"No literature data found for {name}. The directory for this data {example_dir} exists. But we could not find any datapackages in there. "
                f"There is probably some outdated data in {example_dir}. The contents of that directory are: { glob(os.path.join(example_dir,'**')) }"
            )

        return [cls(package=package) for package in packages]

    def plot(self, x_label=None, y_label=None, name=None):
        r"""
        Return a 2D plot of this entry.

        The default plot is constructed from the first two columns of the dataframne.

        EXAMPLES::

            >>> entry = Entry.create_examples()[0]
            >>> entry.plot()
            Figure(...)

        The 2D plot can also be returned with custom axis units available in the resource::

            >>> entry.plot(x_label='j', y_label='E')
            Figure(...)

        """
        import plotly.graph_objects

        x_label = x_label or self.df.columns[0]
        y_label = y_label or self.df.columns[1]

        fig = plotly.graph_objects.Figure()

        fig.add_trace(
            plotly.graph_objects.Scatter(
                x=self.df[x_label],
                y=self.df[y_label],
                mode="lines",
                name=name or self.identifier,
            )
        )

        fig.update_layout(
            template="simple_white",
            showlegend=True,
            autosize=True,
            width=600,
            height=400,
            margin={"l": 70, "r": 70, "b": 70, "t": 70, "pad": 7},
            xaxis_title=f"{x_label} [{self.field_unit(x_label)}]",
            yaxis_title=f"{y_label} [{self.field_unit(y_label)}]",
        )

        fig.update_xaxes(showline=True, mirror=True)
        fig.update_yaxes(showline=True, mirror=True)

        return fig

    @classmethod
    def from_csv(cls, csvname, metadata=None, fields=None):
        r"""
        Returns an entry constructed from a CSV with a single header line.

        EXAMPLES:

        Units describing the fields can be provided::

            >>> import os
            >>> fields = [{'name':'E', 'unit': 'mV'}, {'name':'I', 'unit': 'A'}]
            >>> entry = Entry.from_csv(csvname='examples/from_csv/from_csv.csv', fields=fields)
            >>> entry
            Entry('from_csv')

            >>> entry.package # doctest: +NORMALIZE_WHITESPACE
            {'resources': [{'name':
            ...

        Metadata can be appended::

            >>> import os
            >>> fields = [{'name':'E', 'unit': 'mV'}, {'name':'I', 'unit': 'A'}]
            >>> metadata = {'user':'Max Doe'}
            >>> entry = Entry.from_csv(csvname='examples/from_csv/from_csv.csv', metadata=metadata, fields=fields)
            >>> entry.user
            'Max Doe'

        """
        from frictionless import Schema

        from unitpackage.local import create_df_resource, create_unitpackage

        package = create_unitpackage(csvname=csvname, metadata=metadata, fields=fields)

        df_resource = create_df_resource(package)

        package.add_resource(df_resource)
        package.get_resource("echemdb").schema = Schema.from_descriptor(
            package.resources[0].schema.to_dict()
        )

        return cls(package=package)

    @classmethod
    def _modify_fields(cls, original, alternative, keep_original_name_as=None):
        r"""Updates in a list of fields (original) the field names with those
        provided in a dictionary. The original name of the fields is kept with
        the name `original` in the updated fields.

        EXAMPLES::

            >>> fields = [{'name': '<E>', 'unit':'mV'},{'name': 'I', 'unit':'mA'}]
            >>> alt_fields = {'<E>':'E'}
            >>> Entry._modify_fields(fields, alt_fields, keep_original_name_as='original')
            [{'name': 'E', 'unit': 'mV', 'original': '<E>'}, {'name': 'I', 'unit': 'mA'}]

        """
        for field in original:
            for key in alternative.keys():
                if field["name"] == key:
                    if keep_original_name_as:
                        field.setdefault(keep_original_name_as, key)
                    field["name"] = alternative[key]

        return original

    def rename_fields(self, field_names, keep_original_name_as=None):
        r"""Returns a :class:`~unitpackage.entry.Entry` with updated field names and dataframe
        column names. Provide a dict, where the key is the previous field name and the
        value the new name, such as ``{'t':'t_rel', 'E':'E_we'}``.
        The original field names can be kept in a new key.

        EXAMPLES::

            >>> from unitpackage.entry import Entry
            >>> entry = Entry.create_examples()[0]
            >>> renamed_entry = entry.rename_fields({'t': 't_rel'}, keep_original_name_as='originalName')
            >>> renamed_entry.df
                      t_rel         E         j
            0      0.000000 -0.103158 -0.998277
            1      0.020000 -0.102158 -0.981762
            ...

            >>> renamed_entry.package.get_resource('echemdb').schema.fields
            [{'name': 't_rel', 'type': 'number', 'unit': 's', 'originalName': 't'},
            {'name': 'E', 'type': 'number', 'unit': 'V', 'reference': 'RHE'},
            {'name': 'j', 'type': 'number', 'unit': 'A / m2'}]

        TESTS:

        Provide alternatives for non-existing fields::

            >>> renamed_entry = entry.rename_fields({'t': 't_rel', 'x':'y'}, keep_original_name_as='originalName')
            >>> renamed_entry.package.get_resource('echemdb').schema.fields
            [{'name': 't_rel', 'type': 'number', 'unit': 's', 'originalName': 't'},
            {'name': 'E', 'type': 'number', 'unit': 'V', 'reference': 'RHE'},
            {'name': 'j', 'type': 'number', 'unit': 'A / m2'}]

        """
        if not field_names:
            logger.warning(
                "No renaming pattern was provided, such as {'t': 't_rel', 'x':'y'}."
            )
            field_names = {}

        from frictionless import Package, Resource, Schema

        package = Package(self.package.to_dict())

        df = self.df.rename(columns=field_names).copy()

        new_fields = self._modify_fields(
            self.package.get_resource("echemdb").schema.to_dict()["fields"],
            alternative=field_names,
            keep_original_name_as=keep_original_name_as,
        )

        df_resource = Resource(df)
        df_resource.infer()
        df_resource.schema = Schema.from_descriptor(
            {"fields": new_fields}, allow_invalid=True
        )

        df_resource.name = "echemdb"

        package.remove_resource("echemdb")

        entry = type(self)(package=package)

        entry.package.add_resource(df_resource)
        return entry

    @classmethod
    def from_local(cls, filename):
        r"""
        Return an entry from a :param filename:

        EXAMPLES::

            >>> from unitpackage.entry import Entry
            >>> entry = Entry.from_local('./examples/no_bibliography/no_bibliography.json')
            >>> entry
            Entry('no_bibliography')

        """
        from unitpackage.local import collect_datapackage

        return cls(package=collect_datapackage(filename))

    @classmethod
    def from_df(cls, df, metadata=None, fields=None, outdir=None, *, basename):
        r"""
        Returns an entry constructed from a pandas dataframe.

        EXAMPLES::

            >>> import pandas as pd
            >>> from unitpackage.entry import Entry
            >>> df = pd.DataFrame({'x':[1,2,3], 'y':[2,3,4]})
            >>> entry = Entry.from_df(df=df, basename='test_df')
            >>> entry
            Entry('test_df')

        Metadata and field descriptions can be added::

            >>> import os
            >>> fields = [{'name':'x', 'unit': 'm'}, {'name':'P', 'unit': 'um'}, {'name':'E', 'unit': 'V'}]
            >>> metadata = {'user':'Max Doe'}
            >>> entry = Entry.from_df(df=df, basename='test_df', metadata=metadata, fields=fields)
            >>> entry.user
            'Max Doe'

        Save the entry::

            >>> entry.save(outdir='./test/generated/from_df')

        TESTS

        Verify that all fields are properly created even when they are not specified as fields::

            >>> import os
            >>> fields = [{'name':'x', 'unit': 'm'}, {'name':'P', 'unit': 'um'}, {'name':'E', 'unit': 'V'}]
            >>> metadata = {'user':'Max Doe'}
            >>> entry = Entry.from_df(df=df, basename='test_df', metadata=metadata, fields=fields)
            >>> entry.package.get_resource('echemdb').schema.fields
            [{'name': 'x', 'type': 'integer', 'unit': 'm'}, {'name': 'y', 'type': 'integer'}]

        """
        if outdir is None:
            import atexit
            import shutil
            import tempfile

            outdir = tempfile.mkdtemp()
            atexit.register(shutil.rmtree, outdir)

        csvname = basename + ".csv"

        df.to_csv(os.path.join(outdir, csvname), index=False)

        return cls.from_csv(
            os.path.join(outdir, csvname), metadata=metadata, fields=fields
        )

    def save(self, *, outdir, basename=None):
        r"""
        Create a unitpackage, i.e., a CSV file and a JSON file, in the directory ``outdir``.

        EXAMPLES:

        The output files are named ``identifier.csv`` and ``identifier.json`` using the identifier of the original resource::

            >>> import os
            >>> entry = Entry.create_examples()[0]
            >>> entry.save(outdir='./test/generated')
            >>> basename = entry.identifier
            >>> os.path.exists(f'test/generated/{basename}.json') and os.path.exists(f'test/generated/{basename}.csv')
            True

        When a ``basename`` is set, the files are named ``basename.csv`` and ``basename.json``.
        Note that for a valid frictionless package this base name
        MUST be lower-case and contain only alphanumeric
        characters along with ".", "_" or "-" characters'::

            >>> import os
            >>> entry = Entry.create_examples()[0]
            >>> basename = 'save_basename'
            >>> entry.save(basename=basename, outdir='./test/generated')
            >>> os.path.exists(f'test/generated/{basename}.json') and os.path.exists(f'test/generated/{basename}.csv')
            True

        TESTS:

        Save entry with metadata containing datetime format,
        which is not natively supported by JSON.

            >>> import os
            >>> from datetime import datetime
            >>> import pandas as pd
            >>> from unitpackage.entry import Entry
            >>> df = pd.DataFrame({'x':[1,2,3], 'y':[2,3,4]})
            >>> basename = 'save_datetime'
            >>> entry = Entry.from_df(df=df, basename=basename, metadata={'current time':datetime.now()})
            >>> entry.save(outdir='./test/generated')
            >>> os.path.exists(f'test/generated/{basename}.json') and os.path.exists(f'test/generated/{basename}.csv')
            True

        """
        if not os.path.isdir(outdir):
            os.makedirs(outdir)

        basename = basename or self.identifier
        csv_name = os.path.join(outdir, basename + ".csv")
        json_name = os.path.join(outdir, basename + ".json")

        metadata = self.package.to_copy()

        # update the fields from the main resource with those from the echemdb resource
        metadata.get_resource(self.identifier).schema.fields = metadata.get_resource(
            "echemdb"
        ).schema.fields
        metadata.remove_resource("echemdb")

        # update the identifier and filepath of the resource
        if basename:
            metadata.get_resource(self.identifier).path = basename + ".csv"
            metadata.get_resource(self.identifier).name = basename

        self.df.to_csv(csv_name, index=False)

        with open(json_name, mode="w", encoding="utf-8") as json:
            from unitpackage.local import write_metadata

            write_metadata(json, metadata.to_dict())
