r"""
This module contains the :class: `ReferenceElectrode` which contains
reference data for reference electrodes and allows shifting potentials
between reference scales.

EXAMPLES::

    >>> from unitpackage.electrochemistry.reference_electrodes import ReferenceElectrodes
    >>> ReferenceElectrodes["Ag/AgCl-sat"] # doctest: +NORMALIZE_WHITESPACE
    ReferenceElectrode(name='Ag/AgCl-sat', fullName='KCl Saturated silver / silver chloride electrode',
    entries=[{'value': 0.197, 'preferred': True, 'type': 'experimental', 'unit': 'V', 'vs': 'SHE',
    'source': {'isbn': '978-1119334064'}}], alias=None, temperatureDependence=None)

    >>> ReferenceElectrodes.convert(0.55, "Ag/AgCl-sat", "SHE")
    0.35300000000000004

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


import logging
from dataclasses import dataclass

logger = logging.getLogger("unitpackage")

# An overview and particularities of reference electrodes can be inferred from
# Inzelt et al., Handbook of Reference Electrodes, Springer, 2013.
# https://doi.org/10.1007/978-3-642-36188-3"
# Many values below can found in that source. Nevertheless, the DOIs to the original works are given.
REFERENCE_ELECTRODE_DATA = {
    "SHE": {
        "fullName": "Standard hydrogen electrode",
        "entries": [
            {
                "value": 0.000,
                "preferred": True,
                "type": "theoretical",
                "unit": "V",
                "vs": "SHE",
                "source": "Definition (zero point).",
            }
        ],
    },
    "Ag/AgCl": {
        "fullName": "Silver / Silver Chloride reference electrode for which the concentration is not specified.",
        "entries": [
            {
                "value": 0.210,
                "preferred": True,
                "type": "generic",
                "unit": "V",
                "vs": "SHE",
                "choice": "Reference value for a generic Ag/AgCl electrode",
            }
        ],
    },
    "Ag/AgCl-sat": {
        "fullName": "KCl Saturated silver / silver chloride electrode",
        "entries": [
            {
                "value": 0.197,
                "preferred": True,
                "type": "experimental",
                "unit": "V",
                "vs": "SHE",
                "source": {"isbn": "978-1119334064"},
            }
        ],
    },
    "Ag/AgCl-1M": {
        "fullName": "1 M KCL silver / silver chloride electrode",
        "entries": [
            {"value": 0.22246, "source": "https://doi.org/10.1021/ja01333a001"},
            {"value": 0.22234, "source": "https://doi.org/10.6028/jres.053.037"},
            {
                "value": 0.22239,
                "preferred": True,
                "source": "https://doi.org/10.1021/j150506a011",
            },
        ],
    },
    "CE-sat": {
        "fullName": "Saturated calomel electrode",
        "alias": "SCE",
        "entries": [
            {
                "value": 0.26796,
                "preferred": True,
                "type": "experimental",
                "choice": "Recommended value in Handbook of Reference Electrodes (DOI: https://doi.org/10.1007/978-3-642-36188-3).",
                "unit": "V",
                "vs": "SHE",
                "source": {
                    "doi": "https://doi.org/10.1007/978-3-642-36188-3",
                    "title": "Handbook of Reference Electrodes",
                },
            }
        ],
    },
    "CE-1M": {
        "fullName": "1 molar calomel electrode",
        "entries": [
            {"value": 0.2801, "doi": "https://doi.org/10.1051/jcp/1954510590"},
            {"value": 0.2801, "isbn": "9780123768568"},
            {
                "value": 0.2801,
                "preferred": True,
                "type": "experimental",
                "choice": "Recommended value in Handbook of Reference Electrodes (DOI: https://doi.org/10.1007/978-3-642-36188-3).",
                "unit": "V",
                "vs": "SHE",
                "source": {"doi": "https://doi.org/10.1051/jcp/1954510590"},
            },
        ],
    },
    "CE-0.1M": {
        "fullName": "0.1 M calomel electrode",
        "entries": [
            {"value": 0.3337, "isbn": "978-1-118-31280-3"},
            {"value": 0.3337, "doi": "https://doi.org/10.1051/jcp/1954510590"},
            {
                "value": 0.3337,
                "preferred": True,
                "type": "experimental",
                "choice": "Recommended value in Handbook of Reference Electrodes (DOI: https://doi.org/10.1007/978-3-642-36188-3).",
                "unit": "V",
                "vs": "SHE",
                "source": {"doi": "https://doi.org/10.1051/jcp/1954510590"},
            },
        ],
    },
    "Hg/HgO-0.1M-NaOH": {
        "fullName": "Mercury mercury oxide electrode with internal 0.1 M NaOH solution",
        "entries": [
            {
                "value": 0.1487,
                "source": "https://doi.org/10.1021/acscatal.2c05655",
                "uncertainty": 0.0015,
                "type": "experimental",
            },
            {
                "value": 0.1637,
                "source": "https://doi.org/10.1021/acscatal.2c05655",
                "type": "calculated",
            },
            {
                "value": 0.1690,
                "source": "https://doi.org/10.1039/CT9119900845",
                "type": "experimental",
            },
            {
                "value": 0.1485,
                "preferred": True,
                "type": "experimental",
                "uncertainty": 0.0018,
                "choice": "First value in Kawashima et al. (DOI: https://doi.org/10.1021/acscatal.2c05655), which is similar to a second reported value.",
                "unit": "V",
                "vs": "SHE",
                "source": {"doi": "https://doi.org/10.1021/acscatal.2c05655"},
            },
        ],
    },
    "Hg/HgO-0.5M-NaOH": {
        "fullName": "Mercury mercury oxide electrode with internal 0.5 M NaOH solution",
        "entries": [
            {
                "value": 0.1270,
                "source": "https://doi.org/10.1021/acscatal.2c05655",
                "uncertainty": 0.0014,
                "type": "experimental",
            },
            {
                "value": 0.1254,
                "source": "https://doi.org/10.1021/acscatal.2c05655",
                "type": "calculated",
            },
            {
                "value": 0.1280,
                "preferred": True,
                "type": "experimental",
                "uncertainty": 0.0017,
                "choice": "First value in Kawashima et al. (DOI: https://doi.org/10.1021/acscatal.2c05655), which is similar to a second reported value.",
                "unit": "V",
                "vs": "SHE",
                "source": {"doi": "https://doi.org/10.1021/acscatal.2c05655"},
            },
        ],
    },
    "Hg/HgO-1M-NaOH": {
        "fullName": "Mercury mercury oxide electrode with internal 1 M NaOH solution",
        "entries": [
            {
                "value": 0.1078,
                "source": "https://doi.org/10.1021/acscatal.2c05655",
                "uncertainty": 0.0006,
                "type": "experimental",
            },
            {
                "value": 0.1079,
                "source": "https://doi.org/10.1021/acscatal.2c05655",
                "type": "calculated",
            },
            {
                "value": 0.1135,
                "source": "https://doi.org/10.1039/CT9119900845",
                "type": "experimental",
            },
            {
                "value": 0.1089,
                "preferred": True,
                "type": "experimental",
                "uncertainty": 0.0012,
                "choice": "First value in Kawashima et al. (DOI: https://doi.org/10.1021/acscatal.2c05655), which is similar to a second reported value.",
                "unit": "V",
                "vs": "SHE",
                "source": {"doi": "https://doi.org/10.1021/acscatal.2c05655"},
            },
        ],
    },
    "Hg/HgO-0.1M-KOH": {
        "fullName": "Mercury mercury oxide electrode with internal 0.1 M KOH solution",
        "entries": [
            {
                "value": 0.1414,
                "source": "https://doi.org/10.1021/acscatal.2c05655",
                "uncertainty": 0.0027,
                "type": "experimental",
            },
            {
                "value": 0.1635,
                "source": "https://doi.org/10.1021/acscatal.2c05655",
                "type": "calculated",
            },
            {
                "value": 0.1415,
                "preferred": True,
                "type": "experimental",
                "uncertainty": 0.0012,
                "choice": "First value in Kawashima et al. (DOI: https://doi.org/10.1021/acscatal.2c05655), which is similar to a second reported value.",
                "unit": "V",
                "vs": "SHE",
                "source": {"doi": "https://doi.org/10.1021/acscatal.2c05655"},
            },
        ],
    },
    "Hg/HgO-0.5M-KOH": {
        "fullName": "Mercury mercury oxide electrode with internal 0.5 M KOH solution",
        "entries": [
            {
                "value": 0.1256,
                "source": "https://doi.org/10.1021/acscatal.2c05655",
                "uncertainty": 0.0017,
                "type": "experimental",
            },
            {
                "value": 0.1241,
                "source": "https://doi.org/10.1021/acscatal.2c05655",
                "type": "calculated",
            },
            {
                "value": 0.1100,
                "source": "https://doi.org/10.1039/CT9119900845",
                "type": "experimental",
            },
            {
                "value": 0.1267,
                "preferred": True,
                "type": "experimental",
                "uncertainty": 0.0017,
                "choice": "First value in Kawashima et al. (DOI: https://doi.org/10.1021/acscatal.2c05655), which is similar to a second reported value.",
                "unit": "V",
                "vs": "SHE",
                "source": {"doi": "https://doi.org/10.1021/acscatal.2c05655"},
            },
        ],
    },
    "Hg/HgO-1M-KOH": {
        "fullName": "Mercury mercury oxide electrode with internal 0.5 M NaOH solution",
        "entries": [
            {
                "value": 0.1027,
                "source": "https://doi.org/10.1021/acscatal.2c05655",
                "uncertainty": 0.0026,
                "type": "experimental",
            },
            {
                "value": 0.1053,
                "source": "https://doi.org/10.1021/acscatal.2c05655",
                "type": "calculated",
            },
            {
                "value": 0.1034,
                "preferred": True,
                "type": "experimental",
                "uncertainty": 0.0023,
                "choice": "First value in Kawashima et al. (DOI: https://doi.org/10.1021/acscatal.2c05655), which is similar to a second reported value.",
                "unit": "V",
                "vs": "SHE",
                "source": {"doi": "https://doi.org/10.1021/acscatal.2c05655"},
            },
        ],
    },
    "MSE-sat": {
        "fullName": "Saturated mercury / mercurous sulfate electrode",
        "entries": [
            {
                "value": 0.654,
                "preferred": True,
                "type": "generic",
                "unit": "V",
                "vs": "SHE",
                "source": "Internally used reference value at the Institute of Electrochemistry (Ulm University).",
            }
        ],
    },
    "MSE-0.5M": {
        "fullName": "0.5 M mercury / mercurous sulfate electrode",
        "temperatureDependence": [
            {
                "formula": "E = 0.63495 - 781.44E-6 * T - 426,89E-9 * T**2",
                "comment": "E is in V and T in °C. Equation is valid in the range of 0°C to 60°C",
                "doi": "https://doi.org/10.1021/ja01304a009",
            }
        ],
        "entries": [
            {"value": 0.61587, "source": "https://doi.org/10.1039/TF9605601172"},
            {"value": 0.61515, "source": "https://doi.org/10.1021/ja01304a009"},
            {"value": 0.6125, "source": "https://doi.org/10.1039/TF9656102050"},
            {"value": 0.61236, "source": "https://doi.org/10.1039/FT9949001875"},
            {"value": 0.61544, "source": "https://doi.org/10.1007/BF00973518"},
            {
                "value": 0.61236,
                "preferred": True,
                "type": "experimental",
                "choice": "Recommended value in Handbook of Reference Electrodes (DOI: https://doi.org/10.1007/978-3-642-36188-3).",
                "unit": "V",
                "vs": "SHE",
                "source": {"doi": "https://doi.org/10.1039/FT9949001875"},
            },
        ],
    },
    "RHE": {
        "fullName": "Reversible hydrogen electrode",
        "entries": [
            {
                "type": "theoretical",
                "value": 0.000,
                "preferred": True,
                "unit": "V",
                "vs": "SHE",
                "source": "Nernst equation, 25 °C.",
            }
        ],
    },
}


@dataclass(frozen=True)
class ReferenceElectrode:  # pylint: disable=too-many-instance-attributes
    """
    Represents an electrochemical reference electrode.

    Attributes
    ----------
    name : str
        Common name of the reference electrode (e.g., 'Ag/AgCl-sat', 'SHE').
    fullName: str
         Spelled out name.
    reported : list
        A list of reported values including references for these values.
    temperatureDependence : dict
        A list of formulas or data, providing information about the temperature dependence of the reference electrode.

    Examples
    --------
    Accessing reference electrode data:

    >>> from unitpackage.electrochemistry.reference_electrodes import ReferenceElectrodes
    >>> ReferenceElectrodes["Ag/AgCl-sat"] # doctest: +NORMALIZE_WHITESPACE
    ReferenceElectrode(name='Ag/AgCl-sat', fullName='KCl Saturated silver / silver chloride electrode',
    entries=[{'value': 0.197, 'preferred': True, 'type': 'experimental', 'unit': 'V', 'vs': 'SHE',
    'source': {'isbn': '978-1119334064'}}], alias=None, temperatureDependence=None)

    Converting between reference scales:

    >>> ReferenceElectrodes.convert(0.55, "Ag/AgCl-sat", "SHE")
    0.35300000000000004

    >>> ReferenceElectrodes.convert(ref_from="SHE", ref_to="RHE", ph=5)
    -0.2955
    """

    name: str
    fullName: str  # pylint: disable=invalid-name
    entries: list  # pylint: disable=invalid-name
    alias: str | None = None
    temperatureDependence: dict | None = None  # pylint: disable=invalid-name

    @property
    def value(self):
        """
        Value of the preferred reference electrode.

        EXAMPLES::

            >>> from unitpackage.electrochemistry.reference_electrodes import ReferenceElectrodes
            >>> ReferenceElectrodes["Ag/AgCl-sat"].value
            0.197

        """
        return self.preferred["value"]

    @property
    def preferred(self):
        """
        The preferred reference electrode from the reference electrodes' entries.

        EXAMPLES::

            >>> from unitpackage.electrochemistry.reference_electrodes import ReferenceElectrodes
            >>> ReferenceElectrodes["Ag/AgCl-sat"].preferred # doctest: +NORMALIZE_WHITESPACE
            {'value': 0.197, 'preferred': True, 'type': 'experimental', 'unit': 'V',
            'vs': 'SHE', 'source': {'isbn': '978-1119334064'}}

        """
        entries = [entry for entry in self.entries if "preferred" in entry.keys()]

        if not entries:
            raise KeyError(f"No preferred value found in the {self}.")

        if len(entries) > 1:
            raise KeyError(f"Multiple entries with preferred values found in {self}.")

        return entries[0]


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
        >>> ReferenceElectrodes() # doctest: +NORMALIZE_WHITESPACE
        <ReferenceElectrodes: ['SHE', 'Ag/AgCl', 'Ag/AgCl-sat', 'Ag/AgCl-1M', 'CE-sat', 'CE-1M',
        'CE-0.1M', 'Hg/HgO-0.1M-NaOH', 'Hg/HgO-0.5M-NaOH', 'Hg/HgO-1M-NaOH', 'Hg/HgO-0.1M-KOH',
        'Hg/HgO-0.5M-KOH', 'Hg/HgO-1M-KOH', 'MSE-sat', 'MSE-0.5M', 'RHE']>

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
        >>> ReferenceElectrodes.convert(ref_from="Ag/AgCl-sat", ref_to="SHE")
        -0.197

        >>> ReferenceElectrodes.convert(0.55, "Ag/AgCl-sat", "SHE")
        0.35300000000000004

        >>> ReferenceElectrodes.convert(ref_from="SHE", ref_to="RHE", ph=7)
        -0.4137
        """

        for ref in [ref_from, ref_to]:
            if cls[ref].preferred["type"] == "generic":
                logger.warning(
                    f"""Reference {ref} is of type "generic", i.e., the value is not based on experimental or theoretical values. Consult the details for {ref} with `ReferenceElectrodes()[{ref}]."""
                )

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
