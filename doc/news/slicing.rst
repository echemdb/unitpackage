**Added:**

* Added additional methods to `collection.__getitem__()`, allowing for creating new collections from existing collections by providing a list of identifiers (`db["id1","id2"]`), integers (`db[0,2]`) or simply a slice (`db[2:3]`). Additionally, entries can now be selected by their position in the collection (`entry = db[3]`).
