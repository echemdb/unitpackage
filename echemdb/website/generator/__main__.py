import os.path
import mkdocs_gen_files
from echemdb.data.legacy.data import make_cvs_dataframe, collect_datapackages
from echemdb.website.legacy.make_pages import create_element_pages, create_element_surface_pages, create_systems_pages, render

data = make_cvs_dataframe(collect_datapackages())

create_systems_pages()

for elementname in list(set(data['electrode material'].values)):
    create_element_pages(elementname)

for echemdb_id in list(set(data['echemdb-id'].values)):
    with mkdocs_gen_files.open(os.path.join("cv", "echemdb_pages", f"{echemdb_id}.md"), 'w') as out:
        out.write(render("echemdb_id.md", echemdb_id=echemdb_id, cvs=data))

for tupled in data.groupby(by = ['electrode material', 'surface']).groups:
    create_element_surface_pages(tupled[0], tupled[1])
