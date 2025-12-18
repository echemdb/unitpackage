r"""
This module contains the :class: `ReferenceElectrode` to explore data for tabulated reference electrodes
and determine the shift between different potential scales.


EXAMPLES::

    >>> from unitpackage.electrochemistry.reference_electrode import ReferenceElectrode
    >>> ref = ReferenceElectrode("Ag/AgCl-sat")#
    >>> ref # doctest: +NORMALIZE_WHITESPACE
    {'fullName': 'KCl Saturated silver / silver chloride electrode',
    'entries': [{'value': 0.197, 'preferred': True, 'type': 'experimental',
    'unit': 'V', 'vs': 'SHE', 'source': {'isbn': '978-1119334064'}}]}

    >>> ref.shift(to="SHE", potential=0.55)
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

logger = logging.getLogger("unitpackage")


class ReferenceElectrode:  # pylint: disable=too-many-instance-attributes
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

    def __init__(self, name):
        self.name = name

    def __repr__(self):
        """String representation of the ReferenceElectrode.

        EXAMPLES

        >>> from unitpackage.electrochemistry.reference_electrode import ReferenceElectrode
        >>> ref = ReferenceElectrode("Ag/AgCl-sat") # doctest: +NORMALIZE_WHITESPACE

        """
        return f"{self.data}"

    @property
    def data(self):
        """
        The data to that electrode

        EXAMPLES::

            >>> from unitpackage.electrochemistry.reference_electrode import ReferenceElectrode
            >>> ref = ReferenceElectrode('Ag/AgCl-sat')
            >>> ref.data # doctest: +NORMALIZE_WHITESPACE
            {'fullName': 'KCl Saturated silver / silver chloride electrode',
            'entries': [{'value': 0.197, 'preferred': True, 'type': 'experimental',
            'unit': 'V', 'vs': 'SHE', 'source': {'isbn': '978-1119334064'}}]}

        """

        from unitpackage.electrochemistry.reference_electrode_data import (
            REFERENCE_ELECTRODE_DATA,
        )

        return REFERENCE_ELECTRODE_DATA[self.name]

    @property
    def preferred_value(self):
        """
        The preferred value vs SHE of this reference electrode.

        EXAMPLES::

            >>> from unitpackage.electrochemistry.reference_electrode import ReferenceElectrode
            >>> ref = ReferenceElectrode('Ag/AgCl-sat')
            >>> ref.preferred_value
            0.197

        """
        return self.preferred_data["value"]

    @property
    def preferred_data(self):
        """
        The preferred reference electrode from the reference electrodes' entries.

        EXAMPLES::

            >>> from unitpackage.electrochemistry.reference_electrode import ReferenceElectrode
            >>> ref = ReferenceElectrode('Ag/AgCl-sat')
            >>> ref.preferred_data # doctest: +NORMALIZE_WHITESPACE
            {'value': 0.197, 'preferred': True, 'type': 'experimental',
            'unit': 'V', 'vs': 'SHE', 'source': {'isbn': '978-1119334064'}}

        """
        entries = [
            entry for entry in self.data["entries"] if "preferred" in entry.keys()
        ]

        if not entries:
            raise KeyError(f"No preferred value found in the {self.name}.")

        if len(entries) > 1:
            raise KeyError(
                f"Multiple entries with preferred values found in {self.name}."
            )

        return entries[0]

    def shift(
        self,
        to: str | None = None,
        potential: float | None = None,
        ph: float | None = None,
    ):
        """
        Determine the shift in potential between the reference electrode and another reference electrode.

        The shift can also be determined for a specific potential. For conversion from an to the RHE scale, the pH is required.

        Parameters
        ----------
        to : str
            The target reference scale.
        potential : float, Quantity, or None
            Potential vs. `ref_from`. If None, returns only the shift.
        pH : float, optional
            Required if RHE is involved.

        Returns
        -------
        float
            Converted potential (if `potential` provided) or shift (if not).

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

        ref_from = self.name
        ref_to = to

        for ref in [ref_from, ref_to]:
            if ReferenceElectrode(ref).preferred_data["type"] == "generic":
                logger.warning(
                    f"""Reference {ref.name} is of type "generic", i.e., the value is not based on experimental or theoretical values. Consult the details for {ref} with `ReferenceElectrodes.data."""
                )

        def get_value_vs_she(ref: str) -> float:
            if ref == "RHE":
                if ph is None:
                    raise ValueError("pH must be provided for RHE conversion.")
                return -0.0591 * ph
            return ReferenceElectrode(ref).preferred_value

        shift = get_value_vs_she(ref_to) - get_value_vs_she(self.name)

        if potential is None:
            return shift

        return potential + shift
