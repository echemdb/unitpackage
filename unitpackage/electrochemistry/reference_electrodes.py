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

from unitpackage.electrochemistry.reference_electrode_data import (
    REFERENCE_ELECTRODE_DATA,
)

logger = logging.getLogger("unitpackage")


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
