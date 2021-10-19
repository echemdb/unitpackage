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

    @property
    def df_original(self): #, reference, xunit, yunit
        from astropy import units as u
        df = self.df
        current = u.Unit(self.figure_description.current.unit)
    
        if 'j' in df.columns:
            factor = (u.A / u.m**2).to(current)
            df['j'] *= factor
        if 'I' in df.columns:
            factor = (u.A).to(current)
            df['I'] *= factor
        # same for Voltage axis
        return df

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
