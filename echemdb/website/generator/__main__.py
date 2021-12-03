# ********************************************************************
#  This file is part of echemdb.
#
#        Copyright (C) 2021 Albert Engstfeld
#        Copyright (C) 2021 Johannes Hermann
#        Copyright (C) 2021 Julian Rüth
#        Copyright (C) 2021 Nicolas Hörmann
#
#  echemdb is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  echemdb is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with echemdb. If not, see <https://www.gnu.org/licenses/>.
# ********************************************************************

import os.path
import mkdocs_gen_files
from echemdb.data.legacy.data import make_cvs_dataframe, datadir
from echemdb.data.local import collect_datapackages
from echemdb.website.legacy.make_pages import create_element_pages, create_element_surface_pages, create_systems_pages, render

import echemdb.website.generator.database

def main():
    for entry in echemdb.website.generator.database.cv:
        with mkdocs_gen_files.open(os.path.join("cv", "entries", f"{entry.identifier}.md"), "w") as md:
            md.write(render("pages/cv_entry.md", database=echemdb.website.generator.database.cv, entry=entry))

    data = make_cvs_dataframe(collect_datapackages(datadir))

    create_systems_pages()

    for elementname in list(set(data['electrode material'].values)):
        create_element_pages(elementname)

    for echemdb_id in list(set(data['echemdb-id'].values)):
        with mkdocs_gen_files.open(os.path.join("cv", "echemdb_pages", f"{echemdb_id}.md"), 'w') as out:
            out.write(render("echemdb_id.md", echemdb_id=echemdb_id, cvs=data))

    for tupled in data.groupby(by = ['electrode material', 'surface']).groups:
        create_element_surface_pages(tupled[0], tupled[1])

if __name__ in ["__main__", "<run_path>"]:
    main()
