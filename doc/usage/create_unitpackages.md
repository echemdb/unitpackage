---
jupytext:
  formats: ipynb,md:myst
  text_representation:
    extension: .md
    format_name: myst
    format_version: 0.13
    jupytext_version: 1.14.5
kernelspec:
  display_name: Python 3 (ipykernel)
  language: python
  name: python3
---

# Create unitpackages

For this tutorial we consider the situation where data is generated with a data acquisition device.
The approach to create unitpackages depends on the way data is acquired and which type of is created. Following a few use cases:

* Using a programmatic approach, where you have full control over the data structure during data storage.
* Data is produced by a proprietary software, possibly in a non standard format.

## From CSV after data acquisition

Assume we recorded data which is saved at the end of a measurement to CSV.

```{code-cell} ipython3
import pandas as pd

data = {'t':[1,2,3,4], 'U':[0,5,3,8]}
df = pd.DataFrame(data)
```

```{code-cell} ipython3
outdir = '../files/generated/'
csvname = 'voltage_timeseries.csv'

df.to_csv(outdir + csvname, index=False)
```

```{code-cell} ipython3
from unitpackage.local import create_unitpackage
metadata = {'name': 'Max Doe', 'project': 'echemdb'}
fields = [{'name': 't', 'unit':'s'},{'name':'U', 'unit':'mV'}]

package = create_unitpackage(csvname=csvname, outdir=outdir, fields=fields, metadata=metadata)
package
```

```{code-cell} ipython3

```
