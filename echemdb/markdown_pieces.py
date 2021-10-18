from mdutils.mdutils import MdUtils
import pandas as pd, numpy as np
from matplotlib.cm import jet_r
from matplotlib import colors
from .make_pages import get_page_links, cv_data

# mdFile = MdUtils(file_name='Example_Markdown',title='Markdown File Example')
# mtext = mdFile.new_inline_image(text='snow trees', path='./doc/source/images/photo-of-snow-covered-trees.jpg'))
# mdtext = mdFile.new_table(columns, rows, text, text_align='center', marker='') # text is flattened array

mdFile = MdUtils(file_name='Example_Markdown',title='Markdown File Example')


def sometest(s):
    ns = '| A | B ' \
         '| \n | ------- | ----------- ' \
         '| \n | H  | T       ' \
         '| \n | P  | T       |'

    return ns



def restructure_array(listarray):
    alllines = []
    for line in listarray:
        alllines.extend(line)

    return alllines


def get_table(filename):
    if filename.split(".")[-1] == 'csv':
        columns, rows, text =  shapedlistfrom_csv(filename)
        return mdFile.new_table(columns, rows, text, text_align='center', marker='')  # text is flattened array

def shapedlistfrom_csv(filename):
    df = pd.read_csv(filename)
    rows, columns = df.shape
    rows+=1
    listed = df.columns.tolist()
    for r in df.iterrows():
        listed.extend(r[1].astype(str).tolist())
    return columns, rows, listed



def shapedlistfrom_json(filename):
    return None


def make_element_linkbutton(elementname):
    return '[{}]'.format(elementname) + '(  # ){ .md-button }'


def get_periodic_table():
    edata = './data/elements.csv'
    df = pd.read_csv(edata)
    columns = 18
    rows = 7
    table_list = [ '' for i in range(columns*rows)]
    grh = (np.arange(8) +1).astype(str).tolist()
    d = [ 'd' + k for k in (np.arange(10) +1).astype(str).tolist()]
    header = grh[:2] + d + grh[2:]
    table_list[:columns] = header

    for d in df.iterrows():
        data = d[1]
        per = d[1]['period']
        gr = d[1]['group']
        element = d[1]['symbol']
        if per != "La":
            x, y = int(gr) -1, int(per)
            pos = y*18 + x


            table_list[pos] = make_element_linkbutton(element)

    return mdFile.new_table(columns, rows, table_list, text_align='center', marker='')


def make_element_link(elementname):
    if elementname in cv_data['electrode material'].values:
        link = get_page_links({'elementname': elementname})

        return '[**{}**]'.format(elementname) + "(" + link.split("(")[1]
    else:
        return '**{}**'.format(elementname)

def make_span(elementname, elecolor):
    return '<span class="a" style="background-color:{}"> '.format(elecolor)  + make_element_link(elementname) + ' </span>'


def get_normed_colormap(inarray):
    norm = colors.Normalize(inarray.min(), inarray.max())
    jj = jet_r(norm(inarray))

    cl = [ colors.to_hex(c) for c in jj]
    return cl




def get_periodic_table_span():
    edata = './data/elements.csv'
    df = pd.read_csv(edata)
    columns = 18
    rows = 6
    table_list = [ '<span class="b"> </span>' for i in range(columns*rows)]

    arr = df.electronegativity.values
    arr = np.nan_to_num(arr)
    nch = get_normed_colormap(arr)
    count=0

    for d in df.iterrows():
        count +=1
        color = nch[count-1]
        data = d[1]
        per = d[1]['period']
        gr = d[1]['group']
        element = d[1]['symbol']
        if per != "La":
            x, y = int(gr) -1, int(per)-1
            pos = y*18 + x

            table_list[pos] = make_span(element, color)

    outer = '<div markdown = "1" style="width: 40rem">'
    for r in range(rows):
        for c in range(columns):
            pos = r * 18 + c
            outer += '\n' + table_list[pos]
        outer += '\n'

    outer += '</div>'

    return outer