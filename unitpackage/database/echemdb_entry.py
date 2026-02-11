r"""
A Data Package describing an entry in the echemdb database.
It provides additional functionalities compared to the class :class:`~unitpackage.entry.Entry`.

These are the individual elements of a :class:`~unitpackage.database.echemdb.Echemdb`.

EXAMPLES:

We can directly access the material of an electrode used in the experiment,
such as the working electrode (WE), counter electrode (CE) or reference electrode (REF)::

    >>> from unitpackage.database.echemdb import Echemdb
    >>> db = Echemdb.create_example()
    >>> entry = db['alves_2011_electrochemistry_6010_f1a_solid']
    >>> entry.get_electrode('WE').material
    'Ru'

The :meth:`~unitpackage.database.echemdb_entry.EchemdbEntry.plot` creates a typical representation of a CV,
where ``I`` or. ``j`` is plotted vs. ``U`` or. ``E``::

    >>> entry.plot()
    Figure(...)

    Data Entries containing published data,
    also contain information on the source of the data.::

    >>> from unitpackage.database.echemdb import Echemdb
    >>> db = Echemdb.create_example()
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
      persons={'author': [Person('Alves, Otavio B'), Person('Hoster, Harry E'), Person('Behm, Rolf J{\\"u}rgen')]})


"""

# ********************************************************************
#  This file is part of unitpackage.
#
#        Copyright (C) 2021-2026 Albert Engstfeld
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

from unitpackage.entry import Entry

logger = logging.getLogger("unitpackage")


class EchemdbEntry(Entry):
    r"""
    A `frictionless Data Package <https://github.com/frictionlessdata/framework>`_ describing a CV.

    EXAMPLES:

    Entries are normally obtained by opening a :class:`~unitpackage.database.echemdb.Echemdb` of entries::

        >>> from unitpackage.database.echemdb import Echemdb
        >>> collection = Echemdb.create_example()
        >>> entry = next(iter(collection))


    """

    default_metadata_key = "echemdb"
    """Use 'echemdb' key to access descriptor metadata."""

    def __repr__(self):
        r"""
        Return a printable representation of this entry.

        EXAMPLES::

            >>> entry = EchemdbEntry.create_examples()[0]
            >>> entry
            Echemdb('alves_2011_electrochemistry_6010_f1a_solid')

        """
        return f"Echemdb({self.identifier!r})"

    @property
    def bibliography(self):
        r"""
        Return a pybtex bibliography object associated with this entry.

        EXAMPLES::

            >>> entry = EchemdbEntry.create_examples()[0]
            >>> entry.bibliography # doctest: +NORMALIZE_WHITESPACE
            Entry('article',
            fields=[
                ('title', ...
                ...

            >>> entry_no_bib = EchemdbEntry.create_examples(name="no_bibliography")[0]
            >>> entry_no_bib.bibliography
            ''

        """
        metadata = self._default_metadata.setdefault("source", {})
        citation = metadata.setdefault("bibdata", "")

        if not citation:
            logger.warning(f"Entry with name {self.identifier} has no bibliography.")
            return citation

        from pybtex.database import parse_string

        bibliography = parse_string(citation, "bibtex")
        return bibliography.entries[self.source.citationKey]

    def citation(self, backend="text"):
        r"""
        Return a formatted reference for the entry's bibliography such as:

        J. Doe, et al., Journal Name, volume (YEAR) page, "Title"

        Rendering default is plain text 'text', but can be changed to any format
        supported by pybtex, such as markdown 'md', 'latex' or 'html'.

        EXAMPLES::

            >>> entry = EchemdbEntry.create_examples()[0]
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

    def get_electrode(self, name):
        r"""
        Returns an electrode with the specified name.

        EXAMPLES::

            >>> entry = EchemdbEntry.create_examples()[0]
            >>> entry.get_electrode('WE') # doctest: +NORMALIZE_WHITESPACE
            {'name': 'WE', 'function': 'workingElectrode', 'type': 'single crystal',
            'crystallographicOrientation': '0001', 'material': 'Ru',
            'preparationProcedure': 'Sputtering and flash annealing under UHV
            conditions with repeated cycles of oxygen adsorption and desorption.',
            'shape': {'height': {'unit': 'mm', 'value': 2}, 'type': 'hat shaped'},
            'source': {'supplier': 'Mateck'}}

        TESTS::

            >>> entry.get_electrode('foo') # doctest: +NORMALIZE_WHITESPACE
            Traceback (most recent call last):
            ...
            KeyError: "Electrode with name 'foo' does not exist"

        """
        for electrode in self.system.electrodes:
            if electrode["name"] == name:
                return electrode

        raise KeyError(f"Electrode with name '{name}' does not exist")

    def rescale(self, units):
        r"""
        Return a rescaled :class:`~unitpackage.database.echemdb_entry.EchemdbEntry` with axes in the specified ``units``.

        Usage is essentially the same as for :meth:`~unitpackage.entry.Entry.rescale`, i.e.,
        new units are expected as dict, where the key is the axis name and the value
        the new unit, such as ``{'j': 'uA / cm2', 't': 'h'}``.

        Additionally, the entry can be rescaled to the axes' units of the original data.
        These units must be defined in the metadata of the resource,
        within the key ``figureDescription.fields``::

            >>> entry = EchemdbEntry.create_examples()[0]
            >>> rescaled_entry = entry.rescale(units='original')
            >>> rescaled_entry.mutable_resource.schema.fields # doctest: +NORMALIZE_WHITESPACE
            [{'name': 't', 'type': 'number', 'unit': 's'},
            {'name': 'E', 'type': 'number', 'unit': 'V', 'reference': 'RHE'},
            {'name': 'j', 'type': 'number', 'unit': 'mA / cm2'}]

        """
        if units == "original":
            units = {
                field["name"]: field["unit"] for field in self.figureDescription.fields
            }

        return super().rescale(units)

    def _normalize_field_name(self, field_name):
        r"""
        Return the name of a field name of the `unitpackage` resource.

        If 'j' is requested but is not present in the resource,
        'I' is returned instead.

        EXAMPLES::

            >>> entry = EchemdbEntry.create_examples()[0]
            >>> entry._normalize_field_name('j')
            'j'
            >>> entry._normalize_field_name('x')
            Traceback (most recent call last):
            ...
            ValueError: No axis with name 'x' found.

        """
        if field_name in self.mutable_resource.schema.field_names:
            return field_name
        if field_name == "j":
            return self._normalize_field_name("I")
        raise ValueError(f"No axis with name '{field_name}' found.")

    def thumbnail(self, width=96, height=72, dpi=72, **kwds):
        r"""
        Return a thumbnail of the entry's curve as a PNG byte stream.

        EXAMPLES::

            >>> entry = EchemdbEntry.create_examples()[0]
            >>> thumb = entry.thumbnail()
            >>> thumb.startswith(b'\x89PNG')
            True

        The PNG's ``width`` and ``height`` can be specified in pixels.
        Additional keyword arguments are passed to the data frame plotting
        method::

            >>> thumb = entry.thumbnail(width=4, height=2, color='red', linewidth=2) # doctest: +ELLIPSIS +NORMALIZE_WHITESPACE
            >>> thumb.startswith(b'\x89PNG')
            True

        """
        kwds.setdefault("color", "b")
        kwds.setdefault("linewidth", 1)
        kwds.setdefault("legend", False)

        import matplotlib.pyplot

        # A reasonable DPI setting that should work for most screens is the default value of 72.
        fig, axis = matplotlib.pyplot.subplots(
            1, 1, figsize=[width / dpi, height / dpi], dpi=dpi
        )
        self.df.plot(
            "E",
            self._normalize_field_name("j"),
            ax=axis,
            **kwds,
        )

        matplotlib.pyplot.axis("off")
        matplotlib.pyplot.close(fig)

        import io

        buffer = io.BytesIO()
        fig.savefig(buffer, format="png", transparent=True, dpi=dpi)

        buffer.seek(0)
        return buffer.read()

    def plot(self, x_label="E", y_label="j", name=None):
        r"""
        Return a plot of this entry.
        The default plot is a Cyclic Voltammogram ('j vs E').
        When `j` is not present in the data, `I` is used instead.

        EXAMPLES::

            >>> entry = EchemdbEntry.create_examples()[0]
            >>> entry.plot()
            Figure(...)

        The plot can also be returned with custom axis dimensions (field names) available in the resource::

            >>> entry.plot(x_label='t', y_label='E')
            Figure(...)

        A plot resembling the original figure can be obtained by first rescaling::

            >>> rescaled_entry = entry.rescale('original')
            >>> rescaled_entry.plot()
            Figure(...)

        """
        x_label = self._normalize_field_name(x_label)
        y_label = self._normalize_field_name(y_label)

        def figure_name():
            if (
                hasattr(self.resource, "source")
                and hasattr(self.resource.source, "figure")
                and hasattr(self.resource.source, "curve")
            ):
                return f"Fig. {self.source.figure}: {self.source.curve}"

            return self.identifier

        fig = super().plot(x_label=x_label, y_label=y_label, name=name or figure_name())

        def reference(label):
            if not label == "E":
                return ""
            field = self.mutable_resource.schema.get_field(label).to_dict()
            if "reference" not in field:
                return ""
            return f" vs. {field['reference']}"

        def axis_label(label):
            return f"{label} [{self.field_unit(label)}{reference(label)}]"

        fig.update_layout(
            xaxis_title=axis_label(x_label),
            yaxis_title=axis_label(y_label),
        )

        return fig

    def rescale_reference(self, new_reference=None, field_name=None, ph=None):
        r"""
        Return a rescaled :class:`~unitpackage.database.echemdb_entry.EchemdbEntry` with potentials
        referenced to ``new_reference`` scale.

        ::Warning:: This is an experimental feature working for standard aqueous reference electrodes and electrolytes.
        We do not include temperature effects or other non-idealities at this point.

        If a reference is not available, the axis can still be rescaled by adding an offset using the
        :meth:`~unitpackage.entry.Entry.add_offset`.

        EXAMPLES::

            >>> entry = EchemdbEntry.create_examples()[0]
            >>> entry.mutable_resource.schema.get_field('E') # doctest: +NORMALIZE_WHITESPACE
            {'name': 'E', 'type': 'number', 'unit': 'V', 'reference': 'RHE'}

            >>> entry.df.head() # doctest: +NORMALIZE_WHITESPACE
                  t         E         j
            0  0.00 -0.103158 -0.998277
            1  0.02 -0.102158 -0.981762
            ...

            >>> rescaled_entry = entry.rescale_reference(new_reference='Ag/AgCl-sat')
            >>> rescaled_entry.mutable_resource.schema.get_field('E') # doctest: +NORMALIZE_WHITESPACE
            {'name': 'E', 'type': 'number', 'unit': 'V', 'reference': 'Ag/AgCl-sat'}

            >>> rescaled_entry.df.head() # doctest: +NORMALIZE_WHITESPACE
                  t         E         j
            0  0.00  0.152942 -0.998277
            1  0.02  0.153942 -0.981762
            ...


        """
        field_name = field_name or "E"

        from frictionless import Resource

        resource = Resource(self.resource.to_dict())

        field = self.mutable_resource.schema.get_field(field_name)

        if "reference" not in field.to_dict():
            raise ValueError(f"No Reference is associated with field '{field_name}'.")

        old_reference = field.to_dict()["reference"]

        if old_reference == new_reference:
            return self

        import astropy.units as u

        ph = (
            ph or self.system.electrolyte.ph
            if hasattr(self.system, "electrolyte")
            and hasattr(self.system.electrolyte, "ph")
            else None
        )

        # TODO:: The class should be implemented in an external EC tools module.
        # For now, we need a simple approach for reference scale conversion.
        from unitpackage.electrochemistry.reference_electrode import ReferenceElectrode

        # The potential difference is returned in V
        potential_difference_value = ReferenceElectrode(old_reference).shift(
            to=new_reference, ph=ph.value
        )

        # create an astropy quantity
        potential_difference = potential_difference_value * u.Unit(field.custom["unit"])

        df = self.df.copy()
        df[field_name] += potential_difference.value

        reference_unit = potential_difference.unit.to_string()

        # generate new resource
        df_resource = Resource(df)
        df_resource.infer()
        df_resource.schema = resource.schema
        df_resource.schema.update_field(
            field.name, {"reference": new_reference, "unit": reference_unit}
        )

        resource.custom["MutableResource"] = df_resource

        return type(self)(resource=resource)
