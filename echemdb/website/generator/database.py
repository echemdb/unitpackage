import os.path
import echemdb.data.cv.database
import echemdb.data.local

packages = echemdb.data.local.collect_datapackages(
    os.path.normpath(os.path.join(
        os.path.dirname(__file__),
        '..',
        '..',
        '..',
        'data'))
)

cv = echemdb.data.cv.database.Database(packages)

