#Sam Rothstein
#5/18/19
from pdfminer.pdfdocument import PDFDocument
from pdfminer.pdfpage import PDFPage
from pdfminer.pdfparser import PDFParser
from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.converter import PDFPageAggregator
from pdfminer.layout import LAParams, LTTextBox, LTTextLine, LTFigure
import re

from scipy.spatial import cKDTree
import numpy as np


def alph_num(text):
    return re.sub(r'\W+', '', text)

def parse_layout(layout, page_information):
    """Function to recursively parse the layout tree."""
    for lt_obj in layout:
        if isinstance(lt_obj, LTTextLine):
            text = alph_num(lt_obj.get_text())
            x = (lt_obj.bbox[0] + lt_obj.bbox[2])/2
            y = (lt_obj.bbox[1] + lt_obj.bbox[3])/2
            location = (x,y)
            text_info = [ location, text ]
            page_information.append(text_info)
        elif isinstance(lt_obj, LTFigure):
            parse_layout(lt_obj, page_information)  # Recursive
        elif isinstance(lt_obj, LTTextBox):
            parse_layout(lt_obj, page_information)  # Recursive
    return page_information

def parse_structure(doc, interpreter, device):
    page_number = 1
    general_index = []
    for page in PDFPage.create_pages(doc):
        interpreter.process_page(page)
        layout = device.get_result()
        page_information = []
        page_n_values = parse_layout(layout, page_information)
        #info = [page_number, page_n_values]
        info = page_n_values
        general_index.append(info)
        page_number += 1
    return general_index



#keep things that are the right type

def parse_compare(name_arr, index):
    key_name = []
    for name in name_arr:
        key_name.append(name[0])

    all_names = []
    all_near_values = []

    for page in index:
        names = [] #add string and coordinate
        names_tup = []
        values = [] #everything else
        values_tup = []
        for i in range(len(page)):
            if page[i][1].upper() in key_name:
                names.append(page[i])
                names_tup.append(page[i][0])
            else:
                values.append(page[i])
                values_tup.append(page[i][0])

        values_tup = np.array(values_tup)
        tree = cKDTree(values_tup)

        for i in range(len(names_tup)):
            all_names.append(names[i])
            _, idx = tree.query(names_tup[i], k=20)
            x = []
            for i in idx:
                #print(values[i])
                x.append(values[i])
            all_near_values.append(x)

    return [all_names, all_near_values]


def main():
    fp = open('test_four.pdf', 'rb')
    parser = PDFParser(fp)
    doc = PDFDocument(parser)

    rsrcmgr = PDFResourceManager()
    laparams = LAParams()
    device = PDFPageAggregator(rsrcmgr, laparams=laparams)
    interpreter = PDFPageInterpreter(rsrcmgr, device)

    index = parse_structure(doc, interpreter, device)

    name_arr = [["HEIGHT", "float"], ["WIDTH", "float"]]

    all = parse_compare(name_arr, index)

    print(all[0][0])
    print(all[1][0])


main()
