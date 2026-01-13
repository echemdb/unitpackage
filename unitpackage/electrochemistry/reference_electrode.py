"""
This module contains the :class: `_ReferenceElectrode` to explore data for tabulated reference electrodes
and determine the shift between different potential scales.

TODO:: Add description of certain sources, etc

# An overview and particularities of reference electrodes can be inferred from
# Inzelt et al., Handbook of Reference Electrodes, Springer, 2013.
# https://doi.org/10.1007/978-3-642-36188-3"
# Many values below can found in that source. Nevertheless, the DOIs to the original works are given.


EXAMPLES::

    >>> from unitpackage.electrochemistry.reference_electrode import ReferenceElectrode
    >>> ref = ReferenceElectrode("Ag/AgCl-sat")#
    >>> ref # doctest: +NORMALIZE_WHITESPACE
    {'fullName': 'KCl Saturated silver / silver chloride electrode',
    'entries': [{'value': 0.197, 'standard': 'ECHEMDB-2026', 'approach': 'experimental',
    'unit': 'V', 'vs': 'SHE', 'source': {'isbn': '978-1119334064'}}]}

    >>> ref.shift(to="SHE", potential=0.55)
    0.35300000000000004

"""

# ********************************************************************
#  This file is part of unitpackage.
#
#        Copyright (C) 2025 Johannes Hermann
#        Copyright (C) 2025 Albert Engstfeld
#        Copyright (C) 2025 Julian Rüth
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


# pylint: disable=too-many-instance-attributes,too-few-public-methods
class _ReferenceElectrodeEntry:
    def __init__(
        self,
        value,
        unit,
        vs,
        approach,
        standard=None,
        source=None,
        choice=None,
        uncertainty=None,
    ):
        self.value = value
        self.standard = standard
        self.approach = approach
        self.unit = unit
        self.vs = vs
        self.source = source
        self.choice = choice
        self.uncertainty = uncertainty


class _ReferenceElectrode:
    """
    Represents an electrochemical reference electrode.

    EXAMPLES

    Accessing reference electrode data::

        >>> from unitpackage.electrochemistry.reference_electrode import ReferenceElectrode
        >>> ref = ReferenceElectrode("Ag/AgCl-sat") # doctest: +NORMALIZE_WHITESPACE

    Determine the shift between reference scales::

        >>> ref.shift("SHE", potential=0.42)
        0.22299999999999998

    Conversion to and from RHE requires pH::

        >>> ref.shift(to="RHE", ph=5)
        -0.4925

    """

    def __init__(
        self,
        name,
        full_name,
        alias=None,
        entries=None,
        temperature_dependence=None,
    ):
        self.name = name
        self.full_name = full_name
        self.alias = alias
        self.entries = entries if entries is not None else []
        self.temperature_dependence = (
            temperature_dependence if temperature_dependence is not None else []
        )

    def __repr__(self):
        """String representation of the ReferenceElectrode.

        EXAMPLES

        >>> from unitpackage.electrochemistry.reference_electrode import ReferenceElectrode
        >>> ref = ReferenceElectrode("Ag/AgCl-sat") # doctest: +NORMALIZE_WHITESPACE

        """
        return f"{self.data}"

    def to_json(self, filename=None, outdir=None):
        """Return the data as a JSON string or save to file.

        EXAMPLES

        >>> from unitpackage.electrochemistry.reference_electrode import ReferenceElectrode
        >>> ref = ReferenceElectrode("Ag/AgCl-sat")
        >>> import json
        >>> json.loads(ref.to_json()) # doctest: +NORMALIZE_WHITESPACE
        {'fullName': 'KCl Saturated silver / silver chloride electrode',
        'entries': [{'value': 0.197, 'standard': 'ECHEMDB-2026', 'approach': 'experimental',
        'unit': 'V', 'vs': 'SHE', 'source': {'isbn': '978-1119334064'}}]}

        """
        import json
        import os

        json_str = json.dumps(self.data, indent=2)
        if filename or outdir:
            if filename is None:
                filename = "reference_electrode.json"
            if outdir:
                os.makedirs(outdir, exist_ok=True)
                filepath = os.path.join(outdir, filename)
            else:
                filepath = filename
            with open(filepath, "w") as f:
                f.write(json_str)
            return None
        return json_str

    @property
    def data(self):
        """
        The data for this electrode

        EXAMPLES::

            >>> from unitpackage.electrochemistry.reference_electrode import ReferenceElectrode
            >>> ref = ReferenceElectrode('Ag/AgCl-sat')
            >>> ref.data # doctest: +NORMALIZE_WHITESPACE
            {'fullName': 'KCl Saturated silver / silver chloride electrode',
            'entries': [{'value': 0.197, 'standard': 'ECHEMDB-2026', 'approach': 'experimental',
            'unit': 'V', 'vs': 'SHE', 'source': {'isbn': '978-1119334064'}}]}

        """
        entries_dicts = []
        for entry in self.entries:
            entry_dict = {
                "value": entry.value,
            }
            if entry.standard is not None:
                entry_dict["standard"] = entry.standard
            entry_dict["approach"] = (
                entry.approach if entry.approach is not None else "unknown"
            )
            if entry.unit is not None:
                entry_dict["unit"] = entry.unit
            if entry.vs is not None:
                entry_dict["vs"] = entry.vs
            if entry.source is not None:
                entry_dict["source"] = entry.source
            if entry.choice is not None:
                entry_dict["choice"] = entry.choice
            if entry.uncertainty is not None:
                entry_dict["uncertainty"] = entry.uncertainty
            if entry.doi is not None:
                entry_dict["doi"] = entry.doi
            if entry.isbn is not None:
                entry_dict["isbn"] = entry.isbn
            entries_dicts.append(entry_dict)

        data_dict = {
            "fullName": self.full_name,
            "entries": entries_dicts,
        }
        if self.alias:
            data_dict["alias"] = self.alias
        if self.temperature_dependence:
            data_dict["temperatureDependence"] = self.temperature_dependence
        return data_dict

    @property
    def standard_value(self):
        """
        The standard value vs SHE of this reference electrode.

        EXAMPLES::

            >>> from unitpackage.electrochemistry.reference_electrode import ReferenceElectrode
            >>> ref = ReferenceElectrode('Ag/AgCl-sat')
            >>> ref.standard_value
            0.197

        """
        return self.standard_data["value"]

    @property
    def standard_data(self):
        """
        The standard reference electrode from the reference electrodes' entries.

        EXAMPLES::

            >>> from unitpackage.electrochemistry.reference_electrode import ReferenceElectrode
            >>> ref = ReferenceElectrode('Ag/AgCl-sat')
            >>> ref.standard_data # doctest: +NORMALIZE_WHITESPACE
            {'value': 0.197, 'standard': 'ECHEMDB-2026', 'approach': 'experimental',
            'unit': 'V', 'vs': 'SHE', 'source': {'isbn': '978-1119334064'}}

        """
        entries = [entry for entry in self.entries if entry.standard]
        if not entries:
            raise KeyError(f"No standard value found in the {self.name}.")
        if len(entries) > 1:
            raise KeyError(
                f"Multiple entries with standard values found in {self.name}."
            )
        entry = entries[0]
        entry_dict = {
            "value": entry.value,
            "standard": entry.standard,
        }
        if entry.approach is not None:
            entry_dict["approach"] = entry.approach
        if entry.unit is not None:
            entry_dict["unit"] = entry.unit
        if entry.vs is not None:
            entry_dict["vs"] = entry.vs
        if entry.source is not None:
            entry_dict["source"] = entry.source
        if entry.choice is not None:
            entry_dict["choice"] = entry.choice
        if entry.uncertainty is not None:
            entry_dict["uncertainty"] = entry.uncertainty
        if entry.doi is not None:
            entry_dict["doi"] = entry.doi
        if entry.isbn is not None:
            entry_dict["isbn"] = entry.isbn
        return entry_dict

    def shift(
        self,
        to=None,
        potential=None,
        ph=None,
    ):
        """
        Determine the shift in potential between the reference electrode
        and another reference electrode.

        The shift can also be determined for a specific potential.
        For conversion from an to the RHE scale, the pH is required.

        EXAMPLES:

        Determine the shift with respect to another reference electrode.::

            >>> from unitpackage.electrochemistry.reference_electrode import ReferenceElectrode
            >>> ref = ReferenceElectrode('Ag/AgCl-sat')
            >>> ref.shift(to="SHE") # doctest: +NORMALIZE_WHITESPACE
            -0.197

        The shift from a given potential of the reference electrode.::

            >>> ref.shift(to="SHE", potential=0.55)
            0.35300000000000004

        The pH has no effect on the shift.::

            >>> ref.shift(to='Ag/AgCl-sat', potential=0.55, ph=7)
            0.55

        For the conversion from and to the RHE scale the pH is required.

        To the RHE scale::

            >>> ref = ReferenceElectrode('SHE')
            >>> ref.shift(to="RHE", ph=7)
            -0.4137

            >>> ref = ReferenceElectrode('Ag/AgCl-sat')
            >>> ref.shift(to="RHE", ph=7)
            -0.6107

            >>> ref = ReferenceElectrode('SHE')
            >>> ref.shift(to="RHE", potential=0.55, ph=7)
            0.13630000000000003

        From the RHE scale::

            >>> ref = ReferenceElectrode('RHE')
            >>> ref.shift(to="SHE", ph=0)
            0.0

            >>> ref = ReferenceElectrode('RHE')
            >>> ref.shift(to="SHE", potential=0.55, ph=0)
            0.55

            >>> ref = ReferenceElectrode('RHE')
            >>> ref.shift(to="SHE", potential=0.55, ph=7)
            0.9637

            >>> ref = ReferenceElectrode('RHE')
            >>> ref.shift(to="Ag/AgCl-sat", potential=0.55, ph=7)
            1.1607

        """

        import logging

        logger = logging.getLogger("unitpackage")

        ref_from = self.name
        ref_to = to

        for ref_name in [ref_from, ref_to]:
            ref_obj = ReferenceElectrode(ref_name)
            if ref_obj.standard_data["approach"] == "generic":
                logger.warning(
                    f"Reference {ref_name} is of type 'generic', i.e., the value is not based on experimental or theoretical values. Consult the details for {ref_name} with `ReferenceElectrode.data`."
                )

        def get_value_vs_she(ref: str) -> float:
            if ref == "RHE":
                if ph is None:
                    raise ValueError("pH must be provided for RHE conversion.")
                return -0.0591 * ph
            return ReferenceElectrode(ref).standard_value

        shift_value = get_value_vs_she(ref_to) - get_value_vs_she(self.name)

        if potential is None:
            return shift_value

        return potential + shift_value


# pylint: disable=invalid-name
def ReferenceElectrode(reference):
    """
    Get a reference electrode object.


    EXAMPLES::

        >>> ref = ReferenceElectrode("SHE")
        >>> ref.name
        'SHE'

        >>> ReferenceElectrode(ref) is ref
        True

    """
    if isinstance(reference, _ReferenceElectrode):
        return reference
    return _reference_electrodes[reference]


_reference_electrodes = {
    "SHE": _ReferenceElectrode(
        name="SHE",
        full_name="Standard hydrogen electrode",
        entries=[
            _ReferenceElectrodeEntry(
                value=0.000,
                standard="ECHEMDB-2026",
                approach="theoretical",
                unit="V",
                vs="SHE",
                source="Definition (zero point).",
            )
        ],
    ),
    "Ag/AgCl": _ReferenceElectrode(
        name="Ag/AgCl",
        full_name="Silver / Silver Chloride reference electrode for which the concentration is not specified.",
        entries=[
            _ReferenceElectrodeEntry(
                value=0.210,
                standard="ECHEMDB-2026",
                approach="generic",
                unit="V",
                vs="SHE",
                choice="Reference value for a generic Ag/AgCl electrode",
            )
        ],
    ),
    "Ag/AgCl-sat": _ReferenceElectrode(
        name="Ag/AgCl-sat",
        full_name="KCl Saturated silver / silver chloride electrode",
        entries=[
            _ReferenceElectrodeEntry(
                value=0.197,
                standard="ECHEMDB-2026",
                approach="experimental",
                unit="V",
                vs="SHE",
                source={"isbn": "978-1119334064"},
            )
        ],
    ),
    "Ag/AgCl-1M": _ReferenceElectrode(
        name="Ag/AgCl-1M",
        full_name="1 M KCL silver / silver chloride electrode",
        entries=[
            _ReferenceElectrodeEntry(
                value=0.22246,
                approach="unknown",
                source={"doi": "https://doi.org/10.1021/ja01333a001"},
                unit="V",
                vs="SHE",
            ),
            _ReferenceElectrodeEntry(
                value=0.22234,
                approach="unknown",
                source={"doi": "https://doi.org/10.6028/jres.053.037"},
                unit="V",
                vs="SHE",
            ),
            _ReferenceElectrodeEntry(
                value=0.22239,
                standard="ECHEMDB-2026",
                approach="unknown",
                source={"doi": "https://doi.org/10.1021/j150506a011"},
                unit="V",
                vs="SHE",
            ),
        ],
    ),
    "CE-sat": _ReferenceElectrode(
        name="CE-sat",
        full_name="Saturated calomel electrode",
        alias="SCE",
        entries=[
            _ReferenceElectrodeEntry(
                value=0.26796,
                standard="ECHEMDB-2026",
                approach="experimental",
                choice="Recommended value in Handbook of Reference Electrodes (DOI: https://doi.org/10.1007/978-3-642-36188-3).",
                unit="V",
                vs="SHE",
                source={
                    "doi": "https://doi.org/10.1007/978-3-642-36188-3",
                    "title": "Handbook of Reference Electrodes",
                },
            )
        ],
    ),
    "CE-1M": _ReferenceElectrode(
        name="CE-1M",
        full_name="1 molar calomel electrode",
        entries=[
            _ReferenceElectrodeEntry(
                value=0.2801,
                approach="unknown",
                source={"isbn": "9780123768568"},
                unit="V",
                vs="SHE",
            ),
            _ReferenceElectrodeEntry(
                value=0.2801,
                standard="ECHEMDB-2026",
                approach="experimental",
                choice="Recommended value in Handbook of Reference Electrodes (DOI: https://doi.org/10.1007/978-3-642-36188-3).",
                unit="V",
                vs="SHE",
                source={"doi": "https://doi.org/10.1051/jcp/1954510590"},
            ),
        ],
    ),
    "CE-0.1M": _ReferenceElectrode(
        name="CE-0.1M",
        full_name="0.1 M calomel electrode",
        entries=[
            _ReferenceElectrodeEntry(
                value=0.3337,
                approach="unknown",
                source={"isbn": "978-1-118-31280-3"},
                unit="V",
                vs="SHE",
            ),
            _ReferenceElectrodeEntry(
                value=0.3337,
                approach="experimental",
                standard="ECHEMDB-2026",
                choice="Recommended value in Handbook of Reference Electrodes (DOI: https://doi.org/10.1007/978-3-642-36188-3).",
                source={"doi": "https://doi.org/10.1051/jcp/1954510590"},
                unit="V",
                vs="SHE",
            ),
        ],
    ),
    "Hg/HgO-0.1M-NaOH": _ReferenceElectrode(
        name="Hg/HgO-0.1M-NaOH",
        full_name="Mercury mercury oxide electrode with internal 0.1 M NaOH solution",
        entries=[
            _ReferenceElectrodeEntry(
                value=0.1487,
                source={"doi": "https://doi.org/10.1021/acscatal.2c05655"},
                uncertainty=0.0015,
                approach="experimental",
                unit="V",
                vs="SHE",
            ),
            _ReferenceElectrodeEntry(
                value=0.1637,
                source={"doi": "https://doi.org/10.1021/acscatal.2c05655"},
                approach="calculated",
                unit="V",
                vs="SHE",
            ),
            _ReferenceElectrodeEntry(
                value=0.1690,
                source={"doi": "https://doi.org/10.1039/CT9119900845"},
                approach="experimental",
                unit="V",
                vs="SHE",
            ),
            _ReferenceElectrodeEntry(
                value=0.1485,
                standard="ECHEMDB-2026",
                approach="experimental",
                uncertainty=0.0018,
                choice="First value in Kawashima et al. (DOI: https://doi.org/10.1021/acscatal.2c05655), which is similar to a second reported value.",
                unit="V",
                vs="SHE",
                source={"doi": "https://doi.org/10.1021/acscatal.2c05655"},
            ),
        ],
    ),
    "Hg/HgO-0.5M-NaOH": _ReferenceElectrode(
        name="Hg/HgO-0.5M-NaOH",
        full_name="Mercury mercury oxide electrode with internal 0.5 M NaOH solution",
        entries=[
            _ReferenceElectrodeEntry(
                value=0.1270,
                source={"doi": "https://doi.org/10.1021/acscatal.2c05655"},
                uncertainty=0.0014,
                approach="experimental",
                unit="V",
                vs="SHE",
            ),
            _ReferenceElectrodeEntry(
                value=0.1254,
                source={"doi": "https://doi.org/10.1021/acscatal.2c05655"},
                approach="calculated",
                unit="V",
                vs="SHE",
            ),
            _ReferenceElectrodeEntry(
                value=0.1280,
                standard="ECHEMDB-2026",
                approach="experimental",
                uncertainty=0.0017,
                choice="First value in Kawashima et al. (DOI: https://doi.org/10.1021/acscatal.2c05655), which is similar to a second reported value.",
                unit="V",
                vs="SHE",
                source={"doi": "https://doi.org/10.1021/acscatal.2c05655"},
            ),
        ],
    ),
    "Hg/HgO-1M-NaOH": _ReferenceElectrode(
        name="Hg/HgO-1M-NaOH",
        full_name="Mercury mercury oxide electrode with internal 1 M NaOH solution",
        entries=[
            _ReferenceElectrodeEntry(
                value=0.1078,
                source="https://doi.org/10.1021/acscatal.2c05655",
                uncertainty=0.0006,
                approach="experimental",
                unit="V",
                vs="SHE",
            ),
            _ReferenceElectrodeEntry(
                value=0.1079,
                source="https://doi.org/10.1021/acscatal.2c05655",
                approach="calculated",
                unit="V",
                vs="SHE",
            ),
            _ReferenceElectrodeEntry(
                value=0.1135,
                source="https://doi.org/10.1039/CT9119900845",
                approach="experimental",
                unit="V",
                vs="SHE",
            ),
            _ReferenceElectrodeEntry(
                value=0.1089,
                standard="ECHEMDB-2026",
                approach="experimental",
                uncertainty=0.0012,
                choice="First value in Kawashima et al. (DOI: https://doi.org/10.1021/acscatal.2c05655), which is similar to a second reported value.",
                unit="V",
                vs="SHE",
                source={"doi": "https://doi.org/10.1021/acscatal.2c05655"},
            ),
        ],
    ),
    "Hg/HgO-0.1M-KOH": _ReferenceElectrode(
        name="Hg/HgO-0.1M-KOH",
        full_name="Mercury mercury oxide electrode with internal 0.1 M KOH solution",
        entries=[
            _ReferenceElectrodeEntry(
                value=0.1414,
                source="https://doi.org/10.1021/acscatal.2c05655",
                uncertainty=0.0027,
                approach="experimental",
                unit="V",
                vs="SHE",
            ),
            _ReferenceElectrodeEntry(
                value=0.1635,
                source="https://doi.org/10.1021/acscatal.2c05655",
                approach="calculated",
                unit="V",
                vs="SHE",
            ),
            _ReferenceElectrodeEntry(
                value=0.1415,
                standard="ECHEMDB-2026",
                approach="experimental",
                uncertainty=0.0012,
                choice="First value in Kawashima et al. (DOI: https://doi.org/10.1021/acscatal.2c05655), which is similar to a second reported value.",
                unit="V",
                vs="SHE",
                source={"doi": "https://doi.org/10.1021/acscatal.2c05655"},
            ),
        ],
    ),
    "Hg/HgO-0.5M-KOH": _ReferenceElectrode(
        name="Hg/HgO-0.5M-KOH",
        full_name="Mercury mercury oxide electrode with internal 0.5 M KOH solution",
        entries=[
            _ReferenceElectrodeEntry(
                value=0.1256,
                source={"doi": "https://doi.org/10.1021/acscatal.2c05655"},
                uncertainty=0.0017,
                approach="experimental",
                unit="V",
                vs="SHE",
            ),
            _ReferenceElectrodeEntry(
                value=0.1241,
                source={"doi": "https://doi.org/10.1021/acscatal.2c05655"},
                approach="calculated",
                unit="V",
                vs="SHE",
            ),
            _ReferenceElectrodeEntry(
                value=0.1100,
                source={"doi": "https://doi.org/10.1039/CT9119900845"},
                approach="experimental",
                unit="V",
                vs="SHE",
            ),
            _ReferenceElectrodeEntry(
                value=0.1267,
                standard="ECHEMDB-2026",
                approach="experimental",
                uncertainty=0.0017,
                choice="First value in Kawashima et al. (DOI: https://doi.org/10.1021/acscatal.2c05655), which is similar to a second reported value.",
                unit="V",
                vs="SHE",
                source={"doi": "https://doi.org/10.1021/acscatal.2c05655"},
            ),
        ],
    ),
    "Hg/HgO-1M-KOH": _ReferenceElectrode(
        name="Hg/HgO-1M-KOH",
        full_name="Mercury mercury oxide electrode with internal 0.5 M NaOH solution",
        entries=[
            _ReferenceElectrodeEntry(
                value=0.1027,
                source={"doi": "https://doi.org/10.1021/acscatal.2c05655"},
                uncertainty=0.0026,
                approach="experimental",
                unit="V",
                vs="SHE",
            ),
            _ReferenceElectrodeEntry(
                value=0.1053,
                source={"doi": "https://doi.org/10.1021/acscatal.2c05655"},
                approach="calculated",
                unit="V",
                vs="SHE",
            ),
            _ReferenceElectrodeEntry(
                value=0.1034,
                standard="ECHEMDB-2026",
                approach="experimental",
                uncertainty=0.0023,
                choice="First value in Kawashima et al. (DOI: https://doi.org/10.1021/acscatal.2c05655), which is similar to a second reported value.",
                unit="V",
                vs="SHE",
                source={"doi": "https://doi.org/10.1021/acscatal.2c05655"},
            ),
        ],
    ),
    "MSE-sat": _ReferenceElectrode(
        name="MSE-sat",
        full_name="Saturated mercury / mercurous sulfate electrode",
        entries=[
            _ReferenceElectrodeEntry(
                value=0.654,
                standard="ECHEMDB-2026",
                approach="generic",
                unit="V",
                vs="SHE",
                source="Internally used reference value at the Institute of Electrochemistry (Ulm University).",
            )
        ],
    ),
    "MSE-0.5M": _ReferenceElectrode(
        name="MSE-0.5M",
        full_name="0.5 M mercury / mercurous sulfate electrode",
        temperature_dependence=[
            {
                "formula": "E = 0.63495 - 781.44E-6 * T - 426,89E-9 * T**2",
                "comment": "E is in V and T in °C. Equation is valid in the range of 0°C to 60°C",
                "source": {"doi": "https://doi.org/10.1021/ja01304a009"},
            }
        ],
        entries=[
            _ReferenceElectrodeEntry(
                value=0.61587,
                source={"doi": "https://doi.org/10.1039/TF9605601172"},
                unit="V",
                vs="SHE",
                approach="unknown",
            ),
            _ReferenceElectrodeEntry(
                value=0.61515,
                source={"doi": "https://doi.org/10.1021/ja01304a009"},
                unit="V",
                vs="SHE",
                approach="unknown",
            ),
            _ReferenceElectrodeEntry(
                value=0.6125,
                source="https://doi.org/10.1039/TF9656102050",
                unit="V",
                vs="SHE",
                approach="unknown",
            ),
            _ReferenceElectrodeEntry(
                value=0.61236,
                source={"doi": "https://doi.org/10.1039/FT9949001875"},
                unit="V",
                vs="SHE",
                approach="unknown",
            ),
            _ReferenceElectrodeEntry(
                value=0.61544,
                source={"doi": "https://doi.org/10.1007/BF00973518"},
                unit="V",
                vs="SHE",
                approach="unknown",
            ),
            _ReferenceElectrodeEntry(
                value=0.61236,
                standard="ECHEMDB-2026",
                approach="experimental",
                choice="Recommended value in Handbook of Reference Electrodes (DOI: https://doi.org/10.1007/978-3-642-36188-3).",
                unit="V",
                vs="SHE",
                source={"doi": "https://doi.org/10.1039/FT9949001875"},
            ),
        ],
    ),
    "RHE": _ReferenceElectrode(
        name="RHE",
        full_name="Reversible hydrogen electrode",
        entries=[
            _ReferenceElectrodeEntry(
                value=0.000,
                approach="theoretical",
                standard="ECHEMDB-2026",
                unit="V",
                vs="SHE",
                source="Nernst equation, 25 °C.",
            )
        ],
    ),
}
