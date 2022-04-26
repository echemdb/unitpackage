r"""
Wrappers for a Data Package's metadata stored in the descriptor property.

These wrappers are automatically applied to all metadata of each :class:`Entry`
in our :class:`Database`.

Metadata in data packages is stored as a JSON object. In Python, such a nested
JSON object gets turned into a hierarchy of dictionaries and lists. Such raw
data structures can be a bit tedious to work with, so the descriptors in this
module provide some convenience wrappers for it, e.g., better tab-completion
when working in an interactive session.

EXAMPLES:

To add convenience methods to a data package's descriptor, run it through the
:func:`Descriptor` factory function::

    >>> descriptor = {'some': {'nested': 'metadata'}}
    >>> descriptor = Descriptor(descriptor)

Such a descriptor has some added convenience methods that make it more
convenient to work with.

For example, it can be easily dumped to YAML::

    >>> print(descriptor.yaml)
    some:
        nested: metadata

It can be explored with attributes that are more tab-completion friendly::

    >>> descriptor.some.nested
    'metadata'

Extra methods are added if the descriptor satisfies a certain interface::

    >>> descriptor = {'some': {'nested': {'value': 13.37, 'unit': 'parsec'}}}
    >>> descriptor = Descriptor(descriptor)
    >>> descriptor.some.nested.quantity.to('km')
    <Quantity 4.12555093e+14 km>

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


class GenericDescriptor:
    r"""
    Wrapper for a data package's descriptor to make searching in metadata easier.

    EXAMPLES::

        >>> GenericDescriptor({'a': 0})
        {'a': 0}

    """

    def __init__(self, descriptor):
        self._descriptor = descriptor

    def __dir__(self):
        r"""
        Return the attributes of this descriptor.

        Implemented to allow tab-completion in a package's descriptor.

        EXAMPLES::

            >>> descriptor = GenericDescriptor({'a': 0})
            >>> 'a' in dir(descriptor)
            True

        """
        return list(
            key.replace(" ", "_") for key in self._descriptor.keys()
        ) + object.__dir__(self)

    def __getattr__(self, name):
        r"""
        Return the attribute `name` of the descriptor.

        EXAMPLES::

            >>> descriptor = GenericDescriptor({'a': 0})
            >>> descriptor.a
            0

        """
        name = name.replace("_", " ")

        if name in self._descriptor:
            return Descriptor(self._descriptor[name])

        raise AttributeError(
            f"Descriptor has no entry {name}. Did you mean one of {[key.replace(' ', '_') for key in self._descriptor.keys()]}?"
        )

    def __getitem__(self, name):
        r"""
        Return the attribute `name` of the descriptor.

        EXAMPLES::

            >>> descriptor = GenericDescriptor({'a': 0})
            >>> descriptor["a"]
            0

        """
        if name in self._descriptor:
            return Descriptor(self._descriptor[name])

        raise KeyError(
            f"Descriptor has no entry {name}. Did you mean one of {list(self._descriptor.keys())}?"
        )

    def __repr__(self):
        r"""
        Return a printable representation of this descriptor.

        EXAMPLES::

            >>> GenericDescriptor({})
            {}

        """
        return repr(self._descriptor)

    @property
    def yaml(self):
        r"""Return a printable representation of this descriptor in yaml format.

        EXAMPLES::

            >>> descriptor = GenericDescriptor({'a': 0})
            >>> descriptor.yaml
            'a: 0\n'

        """
        import yaml

        return yaml.dump(self._descriptor)


class QuantityDescriptor(GenericDescriptor):
    r"""
    Extends a descriptor with convenience methods when it is encoding a
    quantity, i.e., unit and value.

    EXAMPLES::

        >>> from echemdb.data.cv.entry import Entry
        >>> entry = Entry.create_examples()[0]
        >>> temperature = entry.system.electrolyte.temperature
        >>> temperature
        298.15 K

    """
    markdown_template = "components/quantity.md"

    @property
    def quantity(self):
        r"""
        This quantity as an astropy quantity.

        EXAMPLES::

            >>> from echemdb.data.cv.entry import Entry
            >>> entry = Entry.create_examples()[0]
            >>> temperature = entry.system.electrolyte.temperature
            >>> temperature.quantity
            <Quantity 298.15 K>

        """
        from astropy import units

        return float(self.value) * units.Unit(self.unit)

    def __repr__(self):
        r"""
        Return a printable representation of this quantity.

        EXAMPLES::

            >>> from echemdb.data.cv.entry import Entry
            >>> entry = Entry.create_examples()[0]
            >>> temperature = entry.system.electrolyte.temperature
            >>> temperature
            298.15 K

        """
        return str(self.quantity)


def Descriptor(descriptor):
    r"""
    Return `descriptor` augmented with additional convenience methods.

    EXAMPLES:

    Primitive types are returned unchanged::

        >>> Descriptor("string")
        'string'

    Dictionaries are augmented with attribute access::

        >>> descriptor = Descriptor({"an attribute": 13.37})
        >>> descriptor.an_attribute
        13.37

    Lists are recursively augmented::

        >>> descriptor = Descriptor([{"an attribute": 13.37}, {}])
        >>> descriptor[0].an_attribute
        13.37

    Dictionaries encoding a unit and value are augmented with astropy
    convenience methods::

        >>> descriptor = Descriptor({"value": 1, "unit": "liter"})
        >>> descriptor.quantity.to("m^3")
        <Quantity 0.001 m3>

    """

    if isinstance(descriptor, GenericDescriptor):
        return descriptor

    if isinstance(descriptor, dict):
        if set(descriptor.keys()) == {"unit", "value"}:
            return QuantityDescriptor(descriptor)

        return GenericDescriptor(descriptor)

    if isinstance(descriptor, list):
        return [Descriptor(item) for item in descriptor]

    return descriptor
