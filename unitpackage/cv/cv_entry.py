r"""
A Data Package describing a Cyclic Voltammogram found in the field of electrochemistry.
It provides additional functionalities compared to the class :class:`Entry`.

These are the individual elements of a :class:`CVCollection`.

EXAMPLES:

We can directly access the material of an electrode used in the experiment,
such as WE, CE or REF::

    >>> from unitpackage.cv.cv_collection import CVCollection
    >>> db = CVCollection.create_example()
    >>> entry = db['alves_2011_electrochemistry_6010_f1a_solid']
    >>> entry.get_electrode('WE').material
    'Ru'

The :meth:`plot` creates a typical representation of a Cyclic Voltammogram,
where ``I`` or. ``j`` is plotted vs. ``U`` or. ``E``::

    >>> entry.plot()
    Figure(...)

"""
# ********************************************************************
#  This file is part of unitpackage.
#
#        Copyright (C) 2021-2023 Albert Engstfeld
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


class CVEntry(Entry):
    r"""
    A `frictionless data packages <https://github.com/frictionlessdata/framework>`_
    describing a Cyclic Voltammogram.

    EXAMPLES:

    An entry can be created directly from a datapackage that has been created
    with `svgdigitizer's <https://echemdb.github.io/svgdigitizer/>`_ `cv` command.
    However, entries are normally obtained by opening a :class:`CVCollection` of entries::

        >>> from unitpackage.cv.cv_collection import CVCollection
        >>> collection = CVCollection.create_example()
        >>> entry = next(iter(collection))

    """

    def __repr__(self):
        r"""
        Return a printable representation of this entry.

        EXAMPLES::

            >>> entry = CVEntry.create_examples()[0]
            >>> entry
            CVEntry('alves_2011_electrochemistry_6010_f1a_solid')

        """
        return f"CVEntry({self.identifier!r})"

    def get_electrode(self, name):
        r"""
        Returns an electrode with the specified name.

        EXAMPLES::

            >>> entry = CVEntry.create_examples()[0]
            >>> entry.get_electrode('WE') # doctest: +NORMALIZE_WHITESPACE
            {'name': 'WE', 'function': 'working electrode', 'type': 'single crystal',
            'crystallographic orientation': '0001', 'material': 'Ru',
            'preparation procedure': 'Sputtering and flash annealing under UHV
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
        Return a rescaled :class:`CVEntry` with axes in the specified ``units``.

        Usage is essentially the same as for :meth:`unitpackage.entry.Entry.rescale`, i.e.,
        new units are expected as dict, where the key is the axis name and the value
        the new unit, such as ``{'j': 'uA / cm2', 't': 'h'}``.

        Additionally, the entry can be rescaled to the axes' units of the original data.
        These units must be defined in the metadata of the resource,
        within the key ``figure_description.fields``::

            >>> entry = CVEntry.create_examples()[0]
            >>> rescaled_entry = entry.rescale(units='original')
            >>> rescaled_entry.package.get_resource('echemdb').schema.fields # doctest: +NORMALIZE_WHITESPACE
            [{'name': 't', 'type': 'number', 'unit': 's'},
            {'name': 'E', 'type': 'number', 'unit': 'V', 'reference': 'RHE'},
            {'name': 'j', 'type': 'number', 'unit': 'mA / cm2'}]

        """
        if units == "original":
            units = {
                field["name"]: field["unit"] for field in self.figure_description.fields
            }

        return super().rescale(units)

    def _normalize_field_name(self, field_name):
        r"""
        Return the name of a field name of the `unitpackage` resource.

        If 'j' is requested but is not present in the resource,
        'I' is returned instead.

        EXAMPLES::

            >>> entry = CVEntry.create_examples()[0]
            >>> entry._normalize_field_name('j')
            'j'
            >>> entry._normalize_field_name('x')
            Traceback (most recent call last):
            ...
            ValueError: No axis with name 'x' found.

        """
        if field_name in self.package.get_resource("echemdb").schema.field_names:
            return field_name
        if field_name == "j":
            return self._normalize_field_name("I")
        raise ValueError(f"No axis with name '{field_name}' found.")

    def thumbnail(self, width=96, height=72, dpi=72, **kwds):
        r"""
        Return a thumbnail of the entry's curve as a PNG byte stream.

        EXAMPLES::

            >>> entry = CVEntry.create_examples()[0]
            >>> entry.thumbnail()
            b'\x89PNG...'

        The PNG's ``width`` and ``height`` can be specified in pixels.
        Additional keyword arguments are passed to the data frame plotting
        method::

            >>> entry.thumbnail(width=4, height=2, color='red', linewidth=2)
            b"\x89PNG..."

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

            >>> entry = CVEntry.create_examples()[0]
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
                hasattr(self.package, "source")
                and hasattr(self.package.source, "figure")
                and hasattr(self.package.source, "curve")
            ):
                return f"Fig. {self.source.figure}: {self.source.curve}"

            return self.identifier

        fig = super().plot(x_label=x_label, y_label=y_label, name=name or figure_name())

        def reference(label):
            if not label == "E":
                return ""
            field = (
                self.package.get_resource("echemdb").schema.get_field(label).to_dict()
            )
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
