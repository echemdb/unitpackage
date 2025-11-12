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

"""

# ********************************************************************
#  This file is part of unitpackage.
#
#        Copyright (C) 2021-2025 Albert Engstfeld
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

    def __repr__(self):
        r"""
        Return a printable representation of this entry.

        EXAMPLES::

            >>> entry = EchemdbEntry.create_examples()[0]
            >>> entry
            Echemdb('alves_2011_electrochemistry_6010_f1a_solid')

        """
        return f"Echemdb({self.identifier!r})"

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
