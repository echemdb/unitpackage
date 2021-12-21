r"""
Implements a `render` macro that renders a template with the Jinja engine.

EXAMPLES::

The `render` macro renders an element using a specific template::

    >>> from io import StringIO
    >>> from astropy.units import Unit

    >>> snippet = StringIO("{{ render('components/quantity.md', value=value) }}")
    >>> render(snippet, value={ 'quantity': 1 * Unit("mol / l") })
    '1.0 M'

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


def render(template, **kwargs):
    r"""
    Render `template` as a jinja template in a new context.

    TESTS:

    The outer context does not leak into a nested context::

        >>> from io import StringIO
        >>> from astropy.units import Unit

        >>> snippet = StringIO("{{ render('components/quantity.md') }}")
        >>> render(snippet, value={ 'quantity': 1 * Unit("mol / l") })
        Traceback (most recent call last):
        ...
        jinja2.exceptions.UndefinedError: 'value' is undefined

    """
    import os.path
    from jinja2 import Environment, FileSystemLoader, select_autoescape
    env = Environment(
        loader=FileSystemLoader(os.path.join(os.path.dirname(__file__), "..", "..", "..", "templates")),
        autoescape=select_autoescape(),
        trim_blocks=True,
        lstrip_blocks=True,
    )

    # Load macros like mkdocs-macros does, see
    # https://github.com/fralau/mkdocs_macros_plugin/blob/master/mkdocs_macros/plugin.py#L157
    def macro(f, name=''):
        env.globals[name or f.__name__] = f
    env.macro = macro
    from echemdb.website.macros import enable_macros
    enable_macros(env)
    del env.macro

    from echemdb.website.filters import enable_filters
    enable_filters(env)

    from io import TextIOBase
    if isinstance(template, TextIOBase):
        template = env.from_string(template.read())
    else:
        template = env.get_template(template)

    return template.render(**kwargs)
