**Added:**

* Added ``Entry.apply_scaling_factor`` which multiplies a column by a given value and tracks the cumulative scaling factor in the field metadata.
* Added ``EchemdbEntry.scan_rate`` property returning the scan rate as an astropy quantity from ``figureDescription.scanRate``.
* Added ``EchemdbEntry.rescale_scan_rate`` which rescales the current (density) axis by the ratio of a new scan rate to the original one, which is essentially like applying a scaling factor.
