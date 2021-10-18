class Database:
    def __init__(self, data_packages):
        self._packages = data_packages

    def __iter__(self):
        from echemdb.data.cv.entry import Entry
        return iter([Entry(package) for package in self._packages])
