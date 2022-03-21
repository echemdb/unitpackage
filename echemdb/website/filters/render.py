r"""
Implements a `render` filter that renders an object as MarkDown.

EXAMPLES:

The `render` filter renders an element using a specific template::

    >>> from echemdb.website.macros.render import render
    >>> from io import StringIO
    >>> from astropy.units import Unit

    >>> snippet = StringIO("{{ value | render(template='components/quantity.md') }}")
    >>> render(snippet, value={ 'quantity': 1 * Unit("mol / l") })
    '1 M'

When no template is given, the filter returns the `markdown` property if
present::

    >>> snippet = StringIO("{{ value | render }}")

    >>> class Value:
    ...     @property
    ...     def markdown(self): return "MarkDown"

    >>> render(snippet, value=Value())
    'MarkDown'

When no template is given, the filter renders the value with the
`markdown_template` if present::

    >>> snippet = StringIO("{{ value | render }}")

    >>> class Value(dict):
    ...     markdown_template = 'components/quantity.md'

    >>> render(snippet, value=Value({ 'quantity': 1 * Unit("mol / l") }))
    '1 M'

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


def render(value, template=None):
    r"""
    Return `value` as a MarkDown string.

    Note that this filter might not interact correctly with autoescaping. If
    there are problems, we should revisit the autoescaping advice at
    https://jinja.palletsprojects.com/en/3.0.x/api/#custom-filters.

    EXAMPLES::

        >>> from echemdb.website.macros.render import render
        >>> from io import StringIO
        >>> from astropy.units import Unit

        >>> snippet = StringIO("{{ value | render(template='components/quantity.md') }}")
        >>> render(snippet, value={ 'quantity': 1 * Unit("A / m^2") })
        '1.0 $\\mathrm{A\\,m^{-2}}$'

    """
    if template is None:
        if hasattr(value, "markdown"):
            return value.markdown
        if hasattr(value, "markdown_template"):
            template = value.markdown_template
        else:
            raise ValueError(
                "No template specified but value does neither provide a markdown property nor a markdown_template property."
            )

    from echemdb.website.macros.render import render

    return render(template, value=value)
