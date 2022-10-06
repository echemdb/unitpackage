r"""
A Data Package describing a Cyclic Voltammogram.

These are the individual elements of a :class:`CVdatabase`.

EXAMPLES:

Data Packages containing published data,
also contain information on the source of the data.::

    >>> from echemdb.cv.cvdatabase import CVdatabase
    >>> db = CVdatabase.create_example()
    >>> entry = db['alves_2011_electrochemistry_6010_f1a_solid']
    >>> entry.bibliography  # doctest: +NORMALIZE_WHITESPACE +REMOTE_DATA
    CVentry('article',
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
#  This file is part of echemdb.
#
#        Copyright (C) 2021-2022 Albert Engstfeld
#        Copyright (C)      2021 Johannes Hermann
#        Copyright (C) 2021-2022 Julian Rüth
#        Copyright (C)      2021 Nicolas Hörmann
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
import logging

from echemdb.entry import Entry

logger = logging.getLogger("echemdb")


class CVentry(Entry):
    r"""
    A [data packages](https://github.com/frictionlessdata/datapackage-py)
    describing a Cyclic Voltammogram.

    EXAMPLES:

    An entry can be created directly from a datapackage that has been created
    with svgdigitizer's `cv` command. However, the entry normally obtained by
    opening a :class:`CVdatabase` of entries::

        >>> from echemdb.cv.cvdatabase import CVdatabase
        >>> database = CVdatabase.create_example()
        >>> entry = next(iter(database))

    """

    def __repr__(self):
        r"""
        Return a printable representation of this entry.

        EXAMPLES::

            >>> entry = CVentry.create_examples()[0]
            >>> entry
            CVentry('alves_2011_electrochemistry_6010_f1a_solid')

        """
        return f"CVentry({repr(self.identifier)})"

    def rescale(self, units):
        if units == "original":
            units = {
                field["name"]: field["unit"] for field in self.figure_description.fields
            }

        return super().rescale(units)

    def _normalize_field_name(self, field_name):
        r"""
        Return a field name when it exists in the `echemdb` resource's field names.

        If 'j' is requested and does not exists in the resource's field names,
        'I' will be returned instead.

        EXAMPLES::

            >>> entry = CVentry.create_examples()[0]
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

            >>> entry = CVentry.create_examples()[0]
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

    def plot(self, x_label="E", y_label="j"):
        r"""
        Return a plot of this entry.
        The default plot is a cyclic voltammogram ('j vs E').
        When `j` is not defined `I` is used instead.

        EXAMPLES::

            >>> entry = CVentry.create_examples()[0]
            >>> entry.plot()
            Figure(...)

        The plot can also be returned with custom axis units available in the resource::

            >>> entry.plot(x_label='t', y_label='E')
            Figure(...)

        The plot with axis units of the original figure can be obtained by first rescaling the entry::

            >>> rescaled_entry = entry.rescale('original')
            >>> rescaled_entry.plot()
            Figure(...)

        """
        import plotly.graph_objects

        x_label = self._normalize_field_name(x_label)
        y_label = self._normalize_field_name(y_label)

        fig = plotly.graph_objects.Figure()

        def figure_name():
            try:
                self.source.figure
            except AttributeError:
                try:
                    self.source.curve
                except AttributeError:
                    return self.identifier
            return f"Fig. {self.source.figure}: {self.source.curve}"

        fig.add_trace(
            plotly.graph_objects.Scatter(
                x=self.df[x_label],
                y=self.df[y_label],
                mode="lines",
                name=f"{figure_name()}",
            )
        )

        def reference(label):
            if label == "E":
                try:
                    self.package.get_resource("echemdb").schema.get_field(label)[
                        "reference"
                    ]
                except KeyError:
                    return ""
                return f" vs. {self.package.get_resource('echemdb').schema.get_field(label)['reference']}"

            return ""

        def axis_label(label):
            return f"{label} [{self.field_unit(label)}{reference(label)}]"

        fig.update_layout(
            template="simple_white",
            showlegend=True,
            autosize=True,
            width=600,
            height=400,
            margin=dict(l=70, r=70, b=70, t=70, pad=7),
            xaxis_title=axis_label(x_label),
            yaxis_title=axis_label(y_label),
        )

        fig.update_xaxes(showline=True, mirror=True)
        fig.update_yaxes(showline=True, mirror=True)

        return fig
