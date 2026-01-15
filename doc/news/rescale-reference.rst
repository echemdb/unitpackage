**Added:**

* Added `unitpackage.electrochemistry.reference_electrodes` which contains reference electrode data and a dataclass to interact with the data (`_reference_electrodes`), and a `ReferenceElectrode` object, which determining the shift of the potential between different reference scales.
* Added `Entry.add_offset` which allows shifting the values of a specified column of the entry by a certain offset and tracking the information in the fields description.
* Added `EchmdbEntry.rescale_reference` which allows shifting the potential scale onto another potential scale known to `unitpackage.electrochemistry._reference_electrodes`.
