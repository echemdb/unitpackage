import os.path
import mkdocs_gen_files
from echemdb.data.legacy.data import make_cvs_dataframe, datadir
from echemdb.data.local import collect_datapackages
from echemdb.website.legacy.make_pages import create_element_pages, create_element_surface_pages, create_systems_pages, render

import echemdb.website.generator.database

for entry in echemdb.website.generator.database.cv:
    with mkdocs_gen_files.open(os.path.join("cv", "entries", f"{entry.identifier}.md"), "w") as md:
        md.write(render("cv_entry.md", database=echemdb.website.generator.database.cv, entry=entry))

data = make_cvs_dataframe(collect_datapackages(datadir))

create_systems_pages()

for elementname in list(set(data['electrode material'].values)):
    create_element_pages(elementname)

for echemdb_id in list(set(data['echemdb-id'].values)):
    with mkdocs_gen_files.open(os.path.join("cv", "echemdb_pages", f"{echemdb_id}.md"), 'w') as out:
        out.write(render("echemdb_id.md", echemdb_id=echemdb_id, cvs=data))

for tupled in data.groupby(by = ['electrode material', 'surface']).groups:
    create_element_surface_pages(tupled[0], tupled[1])
