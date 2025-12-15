r"""
This module contains the :class: `ReferenceElectrode` which contains
reference data for reference electrodes and allows shifting potentials
between reference scales.

EXAMPLES::

    >>> from unitpackage.electrochemistry.reference_electrodes import ReferenceElectrodes
    >>> ReferenceElectrodes["Ag/AgCl-3M"]
    ReferenceElectrode(name='Ag/AgCl-3M', value_vs_she=0.21, unit='V', vs='SHE', source='Inzelt et al., Handbook of Reference Electrodes, Springer, 2013.', formula=None)

    >>> ReferenceElectrodes.convert(0.55, "Ag/AgCl-3M", "SHE")
    0.3400000000000001


"""

# ********************************************************************
#  This file is part of unitpackage.
#
#        Copyright (C) 2025 Johannes Hermann
#        Copyright (C) 2025 Albert Engstfeld
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

from dataclasses import dataclass

# reference_data.py
REFERENCE_ELECTRODE_DATA = {
    "SHE": {
        "value_vs_she": 0.000,
        "unit": "V",
        "vs": "SHE",
        "source": "Definition (zero point).",
    },
    "Ag/AgCl-sat": {
        "value_vs_she": 0.197,
        "unit": "V",
        "vs": "SHE",
        "source": "Inzelt et al., Handbook of Reference Electrodes, Springer, 2013.",
    },
    "Ag/AgCl-3M": {
        "value_vs_she": 0.210,
        "unit": "V",
        "vs": "SHE",
        "source": "Inzelt et al., Handbook of Reference Electrodes, Springer, 2013.",
    },
    "SCE-sat": {
        "value_vs_she": 0.241,
        "unit": "V",
        "vs": "SHE",
        "source": "Inzelt et al., Handbook of Reference Electrodes, Springer, 2013.",
    },
    "MSE-sat": {
        "value_vs_she": 0.640,
        "unit": "V",
        "vs": "SHE",
        "source": "Inzelt et al., Handbook of Reference Electrodes, Springer, 2013.",
    },
    "MSE-1M": {
        "value_vs_she": 0.000,
        "unit": "V",
        "vs": "MSE-1M",
        "source": "Chosen as internal zero for MSE family.",
    },
    "RHE": {
        "value_vs_she": 0.000,
        "unit": "V",
        "vs": "SHE",
        "formula": "E(RHE) = E(SHE) - 0.0591 × pH",
        "source": "Nernst equation, 25 °C.",
    },
}


@dataclass(frozen=True)
class ReferenceElectrode:
    """
    Represents a electrochemical reference electrode.

    Attributes
    ----------
    name : str
        Common name of the reference electrode (e.g., 'Ag/AgCl-3M', 'SHE').
    value_vs_she : float
        Potential of the electrode relative to the standard hydrogen electrode (SHE), in volts.
    unit : str
        Unit of the potential, typically 'V'.
    vs : str
        The reference scale against which the value is reported.
    source : str
        Bibliographic or textual source for the potential value.
    formula : str, optional
        Formula for cases where the potential depends on pH or temperature (e.g., RHE).

    Examples
    --------
    Accessing reference electrode data:

    >>> from unitpackage.electrochemistry.reference_electrodes import ReferenceElectrodes
    >>> ReferenceElectrodes["Ag/AgCl-3M"]
    ReferenceElectrode(name='Ag/AgCl-3M', value_vs_she=0.21, unit='V', vs='SHE', source='Inzelt et al., Handbook of Reference Electrodes, Springer, 2013.', formula=None)

    Converting between reference scales:

    >>> ReferenceElectrodes.convert(0.55, "Ag/AgCl-3M", "SHE")
    0.3400000000000001

    >>> ReferenceElectrodes.convert(ref_from="SHE", ref_to="RHE", ph=5)
    -0.2955
    """

    name: str
    value_vs_she: float
    unit: str = "V"
    vs: str = "SHE"
    source: str = ""
    formula: str | None = None


class ReferenceElectrodes:
    """Registry and converter for electrochemical reference electrodes."""

    _registry: dict[str, ReferenceElectrode] = {
        name: ReferenceElectrode(name=name, **params)
        for name, params in REFERENCE_ELECTRODE_DATA.items()
    }

    def __class_getitem__(cls, key: str) -> ReferenceElectrode:
        """Allow dictionary-style access, e.g. ReferenceElectrodes['SHE']"""
        if key not in cls._registry:
            raise KeyError(f"Unknown reference electrode: '{key}'")
        return cls._registry[key]

    def __repr__(self):
        """String representation of the ReferenceElectrodes registry.

        EXAMPLES

        >>> from unitpackage.electrochemistry.reference_electrodes import ReferenceElectrodes
        >>> ReferenceElectrodes()
        <ReferenceElectrodes: ['SHE', 'Ag/AgCl-sat', 'Ag/AgCl-3M', 'SCE-sat', 'MSE-sat', 'MSE-1M', 'RHE']>

        """
        return f"<ReferenceElectrodes: {list(self._registry.keys())}>"

    @classmethod
    def convert(
        cls,
        potential: float | None = None,
        ref_from: str = "SHE",
        ref_to: str = "SHE",
        ph: float | None = None,
    ):
        """
        Convert a potential between reference electrode scales or compute their shift.

        Parameters
        ----------
        potential : float, Quantity, or None
            Potential vs. `ref_from`. If None, returns only the shift.
        ref_from : str
            The reference scale of the input potential.
        ref_to : str
            The target reference scale.
        pH : float, optional
            Required if RHE is involved.

        Returns
        -------
        float or Quantity
            Converted potential (if `potential` provided) or shift (if not).

        Examples
        --------
        >>> ReferenceElectrodes.convert(ref_from="Ag/AgCl-3M", ref_to="SHE")
        -0.21

        >>> ReferenceElectrodes.convert(0.55, "Ag/AgCl-3M", "SHE")
        0.3400000000000001

        >>> ReferenceElectrodes.convert(ref_from="SHE", ref_to="RHE", ph=7)
        -0.4137
        """

        def get_value_vs_she(ref: str) -> float:
            if ref == "RHE":
                if ph is None:
                    raise ValueError("pH must be provided for RHE conversion.")
                return -0.0591 * ph
            return cls[ref].value_vs_she

        shift = get_value_vs_she(ref_to) - get_value_vs_she(ref_from)

        if potential is None:
            return shift

        return potential + shift
