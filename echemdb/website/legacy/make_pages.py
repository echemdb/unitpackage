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

import os
import os.path

from echemdb.data.legacy.build_data import TEMPLATE_FOLDERS, ELEMENTS_DATA, TARGET_FOLDERS, DISPLAYED_INFOS, get_plotly_plot

import frontmatter
import pandas as pd
import copy
import mkdocs_gen_files
from echemdb.data.legacy.data import datadir, make_cvs_dataframe
from echemdb.data.local import collect_datapackages

cv_data = make_cvs_dataframe(collect_datapackages(datadir))
grouped_cv_data = cv_data.groupby(by=['electrode material', 'surface'])


def get_filtered_tables(elementname, surface=None):

    ele_data = cv_data.loc[(cv_data['electrode material'] == elementname)]
    if surface != None:
        tupled = (elementname, surface)
        ele_data = grouped_cv_data.get_group(tupled)

    ele_data = create_nice_table_overview(ele_data)
    ele_data = ele_data[ DISPLAYED_INFOS  ]
    ele_list_md_str = ele_data.to_markdown(index=False)

    return ele_list_md_str

def get_echemdb_id_file(echemdb_id):
    target = copy.deepcopy(TARGET_FOLDERS['echemdb_id']).replace('tobesubstituted', echemdb_id)
    targetfile = target
    return targetfile.split('.md')[0]

def get_element_file(elementname):
    target = copy.deepcopy(TARGET_FOLDERS['elements']).replace('tobesubstituted', elementname)
    targetfile = target
    return targetfile.split('.md')[0]

def get_element_surface_file(elementname, surfacename):
    target = copy.deepcopy(TARGET_FOLDERS['element_surface']).replace('tobesubstituted', f'{elementname}-{surfacename}')
    targetfile = target
    return targetfile.split('.md')[0]

def get_page_links( property_propertyvals_dict ):
    if len(property_propertyvals_dict.keys()) == 2:
        elementname, surfacename = property_propertyvals_dict['elementname'], property_propertyvals_dict['surfacename']
        filename = get_element_surface_file(elementname, surfacename)
        ln = f'{elementname}({surfacename})'
    else:
        try:
            elementname = property_propertyvals_dict['elementname']
            filename = get_element_file(elementname)
            ln = f'{elementname}'
        except:
            echemdb_id = property_propertyvals_dict['echemdb_id']
            filename = get_echemdb_id_file(echemdb_id)
            ln = f'{echemdb_id}'

    return f'[{ln}](../../{filename}/)'




def create_nice_table_overview(df):
    dfc = df.copy()
    # TODO: These links are broken, see #4.
    dfc['link'] = "." # dfc['path'].apply(lambda path: f'[:material-file-download:]({path})')
    dfc['echemdb-id'] = "." # dfc['echemdb-id'].apply(lambda echemdb_id: f'[{echemdb_id}](../../../{get_echemdb_id_file(echemdb_id)})')
    # reference????
    return dfc

#### Element Page creation, basic copy paste md template ####
def create_element_pages(elementname):
    print(f"Creating {elementname} page")
    with open(TEMPLATE_FOLDERS['elements']) as f:
        templatemd = frontmatter.load(f)
    templatemd['data']['element'] = elementname
    templatemd['title'] = 'echemdb - {} CV data'.format(elementname)

    with mkdocs_gen_files.open(TARGET_FOLDERS['elements'].replace('tobesubstituted', elementname), 'wb') as f:
        frontmatter.dump(templatemd, f) 

#### Systems Page creation ####
def create_systems_pages():
    print(f"Creating systems page")
    with open(TEMPLATE_FOLDERS['systems']) as f:
        templatemd = frontmatter.load(f)

    with mkdocs_gen_files.open(TARGET_FOLDERS['systems'], 'wb') as f:
        frontmatter.dump(templatemd, f)

#### Element Surface Page creation ####
def create_element_surface_pages(elementname, surfacename):
    print(f"Creating {elementname}  {surfacename} page")
    with open(TEMPLATE_FOLDERS['element_surface']) as f:
        templatemd = frontmatter.load(f)
    templatemd['data']['element'] = elementname
    templatemd['data']['surface'] = surfacename
    templatemd['title'] = f'echemdb - {elementname} {surfacename} surfaces CV data'

    with mkdocs_gen_files.open(TARGET_FOLDERS['elements'].replace('tobesubstituted', f'{elementname}-{surfacename}'), 'wb') as f:
        frontmatter.dump(templatemd, f)

#### Content Creation ####

#### Element Page contents ####
def get_element_page_contents(elementname):
    '''
    creates the contents in markdown for the elements pages

    :param elementname:
    :return: Whatever we want to write/plot for the element

    '''
    ej = ELEMENTS_DATA["elements_data"]

    head = "# {}".format(elementname)
    page_md = [head]

    page_md += ["## Elemental properties"]
    allele_data = pd.read_csv(ej)
    ele_data = allele_data.loc[(allele_data['symbol'] == elementname)]
    ele_data = ele_data[['symbol', 'name', 'atomic mass', 'melting point']]
    ele_properties_md_str = ele_data.to_markdown(index=False)

    page_md += [ele_properties_md_str, ' ']
    page_md += ["## Surface specific CVs"]


    for t in [ tupled for tupled in grouped_cv_data.groups if tupled[0] == elementname]:
        link  = get_page_links({'elementname':t[0], 'surfacename':t[1]})
        local_page_content = f'??? example ' + f'"{link}" \n    '  #+ f'"{t[0]}-{t[1]}" \n    '
        #local_page_content += f'### {link} '  + '\n    '
        ele_list_md_str = get_filtered_tables(t[0], surface=t[1]) # here we could leave away surface, filter differently
        local_page_content += '\n    '.join(ele_list_md_str.split('\n'))
        #local_page_content += '\n    asdfasdfasdfa'
        #print(local_page_content)

        page_md += [local_page_content, '\n ']


    page_md += ["## All experimental CVs"]

    ele_list_md_str = get_filtered_tables(elementname, surface=None)

    page_md += [ele_list_md_str, ' ']
    

    page_md = '\n'.join(page_md)

    return page_md



#### Element surface Page contents ####
def get_element_surface_page_contents(elementname, surfacename):
    '''
    creates the contents in markdown for the elements pages

    :param elementname:
    :return: Whatever we want to write/plot for the element

    '''

    head = f"# {elementname}({surfacename})"
    page_md = [head]

    page_md += ["## Available experimental CVs"]

    ele_list_md_str = get_filtered_tables(elementname, surface=surfacename)

    page_md += [ele_list_md_str, ' ']

    page_md += ["## Plots \n "]

    tupled = (elementname, surfacename)
    ele_data = grouped_cv_data.get_group(tupled)
    #print('ele_data', ele_data.columns)

    paths = ele_data['path'].values
    echemdb_ids = ele_data['echemdb-id'].values
    pl = paths.tolist()
    ech = echemdb_ids.tolist()
    print(pl,ech)
    page_md += [get_plotly_plot(ech, pl)]

    page_md = '\n'.join(page_md)


    return page_md


#### systems contents ####
def get_systems_page_contents():
    '''

    :return:
    '''

    page_md = ["# All available experimental CVs"]

    ele_data = create_nice_table_overview(cv_data)
    ele_data = ele_data[ DISPLAYED_INFOS  ]

    ele_list_md_str = ele_data.to_markdown(index=False)


    page_md += [ele_list_md_str, ' ']
    

    page_md = '\n'.join(page_md)

    return page_md
