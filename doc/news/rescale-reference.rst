**Added:**

* Added `unitpackage.electrochemistry.reference_electrodes` with contains reference electrode data and a dataclass to interact with the data, including functions to shift the potentials between different reference scales.
* Added `Entry.add_offset` which allows shifting the values by a certain offset and tracking the information in the fields description.
* Added `EchmdbEntry.rescale_reference` which allows shifting the potential scale onto another potential scale known to `unitpackage.electrochemistry.reference_electrodes`.
