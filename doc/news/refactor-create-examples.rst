**Added:**

* Added ``Entry.create_example(name=None)`` which returns a single example entry. Defaults to ``'alves_2011_electrochemistry_6010_f1a_solid'`` when no name is provided.

**Changed:**

* Changed ``Collection.create_example`` to use ``Collection.from_local`` internally.

**Removed:**

* Removed ``Entry.create_examples``. Use ``Entry.create_example`` instead.
