r"""
This module contains the :class: `ReferenceElectrode` which contains
reference data for reference electrodes and allows shifting potentials
between reference scales.

EXAMPLES::

    >>> from unitpackage.electrochemistry.reference_electrodes import ReferenceElectrodes
    >>> ReferenceElectrodes["Ag/AgCl-3M"]
    ReferenceElectrode(name='Ag/AgCl-3M', value=0.21, unit='V', vs='SHE', source='Inzelt et al., Handbook of Reference Electrodes, Springer, 2013.', formula=None)

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

# A n overview an particularities of reference electrodes can be inferred from
# Inzelt et al., Handbook of Reference Electrodes, Springer, 2013.
# https://doi.org/10.1007/978-3-642-36188-3"
# Many values below were found in that book, but the original DOI is given instead.
REFERENCE_ELECTRODE_DATA = {
    "SHE": {
        "value": 0.000,
        "unit": "V",
        "vs": "SHE",
        "source": "Definition (zero point).",
    },
    "Ag/AgCl-sat": {
        "value": 0.197,
        "unit": "V",
        "vs": "SHE",
        "source": {
            "doi": "https://doi.org/10.1007/978-3-642-36188-3",
            "title": "Handbook of Reference Electrodes",
        },
    },
    "Ag/AgCl-3M": {
        "value": 0.210,
        "unit": "V",
        "vs": "SHE",
        "source": {
            "doi": "https://doi.org/10.1007/978-3-642-36188-3",
            "title": "Handbook of Reference Electrodes",
        },
    },
    "CE-sat": {
        "fullName": "Saturated calomel electrode",
        "alias": "SCE",
        "value": 0.26796,
        "choice": "Recommended value in Handbook of Reference Electrodes (DOI: https://doi.org/10.1007/978-3-642-36188-3).",
        "unit": "V",
        "vs": "SHE",
        "source": {
            "doi": "https://doi.org/10.1007/978-3-642-36188-3",
            "title": "Handbook of Reference Electrodes",
        },
    },
    "CE-1M": {
        "fullName": "1 molar calomel electrode",
        "value": 0.2801,
        "choice": "Recommended value in Handbook of Reference Electrodes (DOI: https://doi.org/10.1007/978-3-642-36188-3).",
        "unit": "V",
        "vs": "SHE",
        "source": {"doi": "https://doi.org/10.1051/jcp/1954510590"},
        "alternativeValues": [
            {"value": 0.2801, "doi": "https://doi.org/10.1051/jcp/1954510590"},
            {"value": 0.2801, "isbn": "9780123768568"},
        ],
    },
    "CE-0.1M": {
        "fullName": "0.1 molar calomel electrode",
        "value": 0.3337,
        "choice": "Recommended value in Handbook of Reference Electrodes (DOI: https://doi.org/10.1007/978-3-642-36188-3).",
        "unit": "V",
        "vs": "SHE",
        "source": {"doi": "https://doi.org/10.1051/jcp/1954510590"},
        "alternativeValues": [
            {"value": 0.3337, "isbn": "978-1-118-31280-3"},
            {"value": 0.3337, "doi": "https://doi.org/10.1051/jcp/1954510590"},
        ],
    },
    "MSE": {
        "fullName": "Mercury/mercurous sulfate electrode",
        "value": 0.61236,
        "choice": "Recommended value in Handbook of Reference Electrodes (DOI: https://doi.org/10.1007/978-3-642-36188-3).",
        "unit": "V",
        "vs": "SHE",
        "temperatureDependence": {
            "formula": "E = 0.63495 - 781.44E-6 * T - 426,89E-9 * T**2",
            "comment": "E is in V and T in °C. Equation is valid in the range of 0°C to 60°C",
            "doi": "https://doi.org/10.1021/ja01304a009",
        },
        "source": {"doi": "https://doi.org/10.1039/FT9949001875"},
        "alternativeValues": [
            {"value": 0.61587, "source": "https://doi.org/10.1039/TF9605601172"},
            {"value": 0.61515, "source": "https://doi.org/10.1021/ja01304a009"},
            {"value": 0.6125, "source": "https://doi.org/10.1039/TF9656102050"},
            {"value": 0.61236, "source": "https://doi.org/10.1039/FT9949001875"},
            {"value": 0.61544, "source": "https://doi.org/10.1007/BF00973518"},
        ],
    },
    "MSE-0.5M": {
        "fullName": "Mercury sulfate electrode",
        "value": 0.640,
        "unit": "V",
        "vs": "SHE",
        "temperatureDependence": {
            "formula": "E(V) = 0.63495 - 781.44E-6 * T - 426,89E-9 * T**2",
            "comment": "valid in the range of 0°C to 60°C",
            "doi": "https://doi.org/10.1021/ja01304a009",
        },
        "source": {
            "doi": "https://doi.org/10.1007/978-3-642-36188-3",
            "title": "Handbook of Reference Electrodes",
        },
    },
    "MSE-sat": {
        "value": 654,
        "unit": "V",
        "vs": "SHE",
        "source": "Chosen as internal zero for MSE family.",
    },
    "RHE": {
        "value": 0.000,
        "unit": "V",
        "vs": "SHE",
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
    value : float
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
    ReferenceElectrode(name='Ag/AgCl-3M', value=0.21, unit='V', vs='SHE', source='Inzelt et al., Handbook of Reference Electrodes, Springer, 2013.', formula=None)

    Converting between reference scales:

    >>> ReferenceElectrodes.convert(0.55, "Ag/AgCl-3M", "SHE")
    0.3400000000000001

    >>> ReferenceElectrodes.convert(ref_from="SHE", ref_to="RHE", ph=5)
    -0.2955
    """

    name: str
    value: float
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
            return cls[ref].value

        shift = get_value_vs_she(ref_to) - get_value_vs_she(ref_from)

        if potential is None:
            return shift

        return potential + shift
