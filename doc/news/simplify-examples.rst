**Changed:**

* Changed `Entry.create_examples` to load pre-defined datapackages instead of generating datapackges from SVGs with the `svgdigitizer`.

**Removed:**

* Removed `svgdigitizer` as dependency used in automated tests.
* Removed `Entry._digitize_example`, used to create datapackages for automated test.
*
