class Entry:
    def __init__(self, package):
        self.package = package

    @property
    def identifier(self):
        return self.package.resources[0].name

    @property
    def _descriptor(self):
        return Descriptor(self.package.descriptor)

    def __dir__(self):
        return dir(self._descriptor) + object.__dir__(self)

    def __getattr__(self, name):
        name = name.replace('_', ' ')
        return getattr(Descriptor(self.package.descriptor), name)

    def __getitem__(self, name):
        return Descriptor(self.package.descriptor)[name]

    @property
    def df(self):
        import pandas
        return pandas.read_csv(self.package.resources[0].raw_iter(stream=False))

    def plot(self):
        from echemdb.data.cv.plot import Plot
        return Plot(self)

class Descriptor:
    def __init__(self, descriptor):
        self._descriptor = descriptor

    def __dir__(self):
        return list(key.replace(' ', '_') for key in self._descriptor.keys()) + object.__dir__(self)

    def __getattr__(self, name):
        name = name.replace('_', ' ')
        if name in self._descriptor:
            value = self._descriptor[name]
            return Descriptor(value) if isinstance(value, dict) else value

        raise AttributeError(f"Descriptor has no entry {name}. Did you mean one of {list(self._descriptor.keys())}?")

    def __getitem__(self, name):
        if name in self._descriptor:
            value = self._descriptor[name]
            return Descriptor(value) if isinstance(value, dict) else value

        raise KeyError(f"Descriptor has no entry {name}. Did you mean one of {list(self._descriptor.keys())}?")
