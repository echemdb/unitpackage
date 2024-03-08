import unitpackage.remote

import unitpackage.local

from unitpackage.collection import Collection



def from_remote(data=None, url=None, outdir=None):
    return Collection(unitpackage.remote.collect_datapackages(data=data or "data", url=url or unitpackage.remote.ECHEMDB_DATABASE_URL, outdir=outdir))

def from_local(data):
    return Collection(unitpackage.local.collect_datapackages(data=data))
