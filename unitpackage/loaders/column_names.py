r"""Fields describing specific csv data, such as biologic MPT files."""

# ********************************************************************
#  This file is part of unitpackage.
#
#        Copyright (C) 2024-2025 Albert Engstfeld
#        Copyright (C)      2024 Justus Leist
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

biologic_fields = [
    {
        "name": "Ri/Ohm",
        "unit": "Ohm",
        "dimension": "R",
        "description": "apparent resistance",
    },
    {
        "name": "-Im(Z)/Ohm",
        "unit": "Ohm",
        "dimension": "-Im(Z)",
        "description": "-imaginary part of Z",
    },
    {
        "name": "-Im(Zce)/Ohm",
        "unit": "Ohm",
        "dimension": "-Im(Zce)",
        "description": "-imaginary part of Z of CE vs ref",
    },
    {
        "name": "-Im(Zwe-ce)/Ohm",
        "unit": "Ohm",
        "dimension": "-Im(Zwe-ce)",
        "description": "-imaginary part of Z of WE vs CE",
    },
    {
        "name": "(Q-Qo)/C",
        "unit": "C",
        "dimension": "Q",
        "description": "charge from the beginning of the experiment",
    },
    {
        "name": "(Q-Qo)/mA.h",
        "unit": "mA h",
        "dimension": "Q",
        "description": "charge from the beginning of the experiment",
    },
    {
        "name": "<Ece>/V",
        "unit": "V",
        "dimension": "E",
        "description": "averaged potential of CE versus REF",
    },
    {
        "name": "<Ewe>/V",
        "unit": "V",
        "dimension": "E",
        "description": "averaged voltage (WE vs. REF)",
    },
    {
        "name": "<I>/mA",
        "unit": "mA",
        "dimension": "I",
        "description": "average current over the potential step (calculated from I = dQ/dt",
    },
    {
        "name": "|Ece|/V",
        "unit": "V",
        "dimension": "E",
        "description": "module of Ece (Note:Impedance related)",
    },
    {
        "name": "|Energy|/W.h",
        "unit": "W h",
        "dimension": "E",
        "description": "module of Energy (Note:Impedance related)",
    },
    {
        "name": "|Ewe|/V",
        "unit": "V",
        "dimension": "E",
        "description": "module of Ewe (Note:Impedance related",
    },
    {
        "name": "|I|/A",
        "unit": "A",
        "dimension": "I",
        "description": "module of I (Note:Impedance related",
    },
    {
        "name": "|Y|/Ohm-1",
        "unit": "S",
        "dimension": "|Y|",
        "description": "Admittance magnitude (in Ω-1",
    },
    {"name": "|Z|/Ohm", "unit": "Ohm", "dimension": "|Z|", "description": "Phase of Z"},
    {
        "name": "|Zce|/Ohm",
        "unit": "Ohm",
        "dimension": "|Zce|",
        "description": "Phase of Zce",
    },
    {
        "name": "|Zwe-ce|/Ohm",
        "unit": "Ohm",
        "dimension": "|Zwe-ce|",
        "description": "Phase of Zwe-ce",
    },
    {
        "name": "Analog IN 1/V",
        "unit": "V",
        "dimension": "V",
        "description": "Additional analog input 1",
    },
    {
        "name": "Analog IN 2/V",
        "unit": "V",
        "dimension": "V",
        "description": "Additional analog input 2",
    },
    {
        "name": "Analog IN 3/V",
        "unit": "V",
        "dimension": "V",
        "description": "Additional analog input 3 (for VMP only)",
    },
    {
        "name": "Capacitance charge/µF",
        "unit": "uF",
        "dimension": "C",
        "description": "Capacitance charge",
    },
    {
        "name": "Capacitance discharge/µF",
        "unit": "uF",
        "dimension": "C",
        "description": "Capacitance discharge",
    },
    {
        "name": "Capacity/mA.h",
        "unit": "mA h",
        "dimension": "Q",
        "description": "Capacity",
    },
    {
        "name": "charge time/s",
        "unit": "s",
        "dimension": "t",
        "description": "Charge time: time elapsed during each charge (I>0) reset to 0 at the end of each discharge",
    },
    {
        "name": "Conductivity/S.cm-1",
        "unit": "S cm-1",
        "dimension": "sigma",
        "description": "Conductivity",
    },
    {
        "name": "control changes",
        "description": "Control changes, State byte (bit n°5) ",
    },
    {
        "name": "control/mA",
        "unit": "mA",
        "dimension": "I",
        "description": "Ictrl: current control",
    },
    {
        "name": "control/V",
        "unit": "V",
        "dimension": "V",
        "description": "Ectrl: potential control ",
    },
    {
        "name": "control/V/mA",
        "unit": "V mA-1",
        "dimension": "V / I",
        "description": "Ectrl/Ictrl: potential or current control ",
    },
    {
        "name": "counter inc.",
        "description": "Experiment counter value has changed (bit n°8)",
    },
    {
        "name": "Cp-2/µF-2",
        "unit": "uF-2",
        "dimension": "C-2",
        "description": "Inverse of square capacitance calculated using an R/C (parallel) equivalent circuit ",
    },
    {
        "name": "Cp/µF",
        "unit": "uF",
        "dimension": "C",
        "description": "Capacitance calculated using an R/C (parallel) equivalent circuit ",
    },
    {
        "name": "Cs-2/µF-2",
        "unit": "uF-2",
        "dimension": "Cs⁻²",
        "description": "Inverse of square capacitanc calculated using an R+C (series) equivalent circuit",
    },
    {
        "name": "Cs/µF",
        "unit": "uF",
        "dimension": "C",
        "description": "Capacitance calculated using an R+C (series) equivalent circuit",
    },
    {"name": "cycle number", "description": "Cycle number"},
    {
        "name": "cycle time/s",
        "unit": "s",
        "dimension": "t",
        "description": "Cycle time: time elapsed during each cycle",
    },
    {
        "name": "d(Q-Qo)/dE/mA.h/V",
        "unit": "mA h/V",
        "dimension": "d(Q-Qo)/dE",
        "description": "Incremental (or differential) capacity over the potential dE during charge or discharge",
    },
    {
        "name": "dI/dt/mA/s",
        "unit": "mA/s",
        "dimension": "dI/dt",
        "description": "Differential current over time (for potentio technique only) ",
    },
    {
        "name": "discharge time/s",
        "unit": "s",
        "dimension": "t",
        "description": "Discharge time : time elapsed during each discharge (I<0) reset to 0 at the end of each charge",
    },
    {
        "name": "dQ/C",
        "unit": "C",
        "dimension": "dQ",
        "description": "charge increment between two recorded values",
    },
    {
        "name": "dq/mA.h",
        "unit": "mA·h",
        "dimension": "dq",
        "description": "dq: charge on a potential step",
    },
    {
        "name": "dQ/mA.h",
        "unit": "mA·h",
        "dimension": "dQ",
        "description": "dQ: charge on a cycle",
    },
    {
        "name": "Ece/V",
        "unit": "V",
        "dimension": "E",
        "description": "potential control ",
    },
    {
        "name": "Ecell/V",
        "unit": "V",
        "dimension": "U",
        "description": "Ecell: WE versus CE potential",
    },
    {
        "name": "Efficiency/%",
        "unit": "pct",
        "dimension": "Efficiency",
        "description": "Efficiency: Q discharge/Q charge ",
    },
    {
        "name": "Energy charge/W.h",
        "unit": "W h",
        "dimension": "E",
        "description": "Energy charge: E*I*t for I>0 ",
    },
    {
        "name": "Energy discharge/W.h",
        "unit": "W h",
        "dimension": "E",
        "description": "Energy discharge: E*I*t for I<0",
    },
    {
        "name": "Energy/W.h",
        "unit": "W h",
        "dimension": "E",
        "description": "Energy: in CPW calculated by E*I*t",
    },
    {"name": "error", "description": "error"},
    {
        "name": "Ewe-Ece/V",
        "unit": "V",
        "dimension": "U",
        "description": "Ewe-Ece: WE versus CE potential ",
    },
    {
        "name": "Ewe/V",
        "unit": "V",
        "dimension": "E",
        "description": "WE potential versus REF",
    },
    {"name": "freq/Hz", "unit": "Hz", "dimension": "f", "description": "Frequency"},
    {"name": "half cycle", "description": "Half cycle of CV"},
    {"name": "I Range", "description": "The current range"},
    {
        "name": "I/mA",
        "unit": "mA",
        "dimension": "I",
        "description": "Instantaneous current",
    },
    {
        "name": "Im(Y)/Ohm-1",
        "unit": "S",
        "dimension": "Im(Y)",
        "description": "-Im(Y):-imaginary part of Y (in Ω-1)",
    },
    {
        "name": "mode",
        "description": "Mode = Intentio/Potentio/Relax, State byte (bits n°1 and 2) ",
    },
    {"name": "Ns changes", "description": "Changes of Ns, State byte (bit n°6)"},
    {"name": "Ns", "description": ""},
    {"name": "NSD Ewe/%", "unit": "pct", "description": "NSD Ewe"},
    {"name": "NSD I/%", "unit": "pct", "description": "NSD I"},
    {"name": "NSR Ewe/%", "unit": "pct", "description": "NSR Ewe"},
    {"name": "NSR I/%", "unit": "pct", "description": "NSR I"},
    {"name": "ox/red", "description": "ox or red"},
    {
        "name": "P/W",
        "unit": "W",
        "dimension": "P",
        "description": "Power: in CPW, calculated by E*I",
    },
    {
        "name": "Phase(Y)/deg",
        "unit": "deg",
        "dimension": "Phase(Y)",
        "description": "Admittance phase (in degrees)",
    },
    {
        "name": "Phase(Z)/deg",
        "unit": "deg",
        "dimension": "Phase(Z)",
        "description": "Phase of Z",
    },
    {
        "name": "Phase(Zce)/deg",
        "unit": "deg",
        "dimension": "Phase(Zce)",
        "description": "Phase of Zce",
    },
    {
        "name": "Phase(Zwe-ce)/deg",
        "unit": "deg",
        "dimension": "Phase(Zwe-ce)",
        "description": "Phase of Zwe-ce",
    },
    {
        "name": "Q charge/discharge/mA.h",
        "unit": "mA h",
        "dimension": "Q",
        "description": "Q charge/discharge: Q for a charge/discharge cycle reinitialized every cycle",
    },
    {
        "name": "Q charge/mA.h",
        "unit": "mA h",
        "dimension": "Q",
        "description": "Q charge: Q for a charge cycle reinitialized every cycle",
    },
    {
        "name": "Q charge/mA.h/g",
        "unit": "mA h/g",
        "dimension": "Q / m",
        "description": "Q charge: Q for a charge cycle reinitialized every cycle",
    },
    {
        "name": "Q discharge/mA.h",
        "unit": "mA h",
        "dimension": "Q",
        "description": "Q discharge: Q for a discharge cycle reinitialized every cycle",
    },
    {
        "name": "Q discharge/mA.h/g",
        "unit": "mA h / g",
        "dimension": "Q / m",
        "description": "Q discharge: Q for a discharge cycle reinitialized every cycle",
    },
    {"name": "R/Ohm", "unit": "Ohm", "dimension": "R", "description": "Resistance"},
    {"name": "Rcmp/Ohm", "unit": "Ohm", "dimension": "R"},
    {
        "name": "Re(Y)/Ohm-1",
        "unit": "S",
        "dimension": "Re(Y)",
        "description": "Re(Y): real part of Y (in Ω-1)",
    },
    {
        "name": "Re(Z)/Ohm",
        "unit": "Ohm",
        "dimension": "Re(Z)",
        "description": "Re(Z): real part of Z",
    },
    {
        "name": "Re(Zce)/Ohm",
        "unit": "Ohm",
        "dimension": "Re(Zce)",
        "description": "Re(Z): real part of Zce",
    },
    {
        "name": "Re(Zwe-ce)/Ohm",
        "unit": "Ohm",
        "dimension": "Re(Zwe-ce)",
        "description": "Re(Z): real part of Zwe-ce",
    },
    {
        "name": "step time/s",
        "unit": "s",
        "dimension": "t",
        "description": "Step time: time elapsed ",
    },
    {
        "name": "THD Ewe/%",
        "unit": "pct",
        "dimension": "THD Ewe",
        "description": "Total Harmonic Distortion of Ewe",
    },
    {
        "name": "THD I/%",
        "unit": "pct",
        "dimension": "THD I",
        "description": "Total Harmonic Distortion of I",
    },
    {"name": "time/s", "unit": "s", "dimension": "t", "description": "time"},
    {"name": "x", "description": "x: normalized charge "},
    {"name": "z cycle", "description": "z cycle"},
]

biologic_fields_alt_names = {
    "<I>/mA": "I",
    "I/mA": "I",
    "<Ewe>/V": "E",
    "Ewe/V": "E",
    "time/s": "t",
    "Re(Z)/Ohm": "Re(Z)",
    "-Im(Z)/Ohm": "-Im(Z)",
    "freq/Hz": "f",
    "Phase(Z)/deg": "Phase(Z)",
}
