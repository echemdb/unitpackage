"""
This file contains electrochemical reference electrode data.

TODO:: Add description of certain sources, etc

# An overview and particularities of reference electrodes can be inferred from
# Inzelt et al., Handbook of Reference Electrodes, Springer, 2013.
# https://doi.org/10.1007/978-3-642-36188-3"
# Many values below can found in that source. Nevertheless, the DOIs to the original works are given.

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
