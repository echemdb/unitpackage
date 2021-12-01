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
        return list(key.replace(' ', '_') for key in self._descriptor.keys()) + object.__dir__(self)

    def __getattr__(self, name):
        r"""
        Return the attribute `name` of the descriptor.

        EXAMPLES::

            >>> descriptor = GenericDescriptor({'a': 0})
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

            >>> descriptor = GenericDescriptor({'a': 0})
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

            >>> GenericDescriptor({})
            {}

        """
        return repr(self._descriptor)

    @property
    def yaml(self):
        r'''Return a printable representation of this descriptor in yaml format.

        EXAMPLES::

            >>> descriptor = GenericDescriptor({'a': 0})
            >>> descriptor.yaml
            'a: 0\n'

        '''
        import yaml
        return yaml.dump(self._descriptor)

class UnitValueDescriptor(GenericDescriptor):
    r"""
    EXAMPLES::

        >>> from echemdb.data.cv.entry import Entry
        >>> entry = Entry.create_examples()[0]
        >>> temperature = entry.electrochemical_system.electrolyte.temperature
        >>> temperature
        298.15 K

        >>> temperature.markdown
        '25.0 °C'

    """
    @property
    def markdown(self):
        from echemdb.website.legacy.make_pages import render
        return render("unit_value.md", quantity=self.quantity)

    @property
    def quantity(self):
        from astropy import units

        return float(self.value) * units.Unit(self.unit)

    def __repr__(self):
        return str(self.quantity)

def Descriptor(descriptor):
    if set(descriptor.keys()) == {"unit", "value"}:
        return UnitValueDescriptor(descriptor)

    return GenericDescriptor(descriptor)
