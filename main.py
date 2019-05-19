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
    '''
    input: text, type = string
    output: processed text, type = string
    '''
    #experimenting with different text editing strategies
    '''
    print(text)
    print(type(text))
    print("_____")
    print(text.strip('!"#$%&\'()*+-/:;<=>?@[\\]^_`{|}~'))
    print(re.sub(r'\W+', '', text))
    return
    '''

    #return edited text
    return re.sub(r'\W+', '', text)

def parse_layout(layout, page_information):
    '''
    input: page layout, type = layout object | page information, type = ??
    output: information about page [(x,y), "string"]
    '''
    #Function to recursively parse the layout tree.
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
    '''
    input: doc, type = PDF document | interpreter, type ?? | device, type =??
    output: [[page #1 info],....., [page #n info]]
    '''
    #high level function
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


def RepresentsInt(s):
    try:
        int(s)
        return True
    except ValueError:
        return False

def RepresentsFloat(s):
    try:
        float(s)
        return True
    except ValueError:
        return False

def parse_compare(name_arr, index, number_of_values):
    '''
    input: name_arr, type = [["Name", "float"],.....,["Name", "float"]] |
    index, type = [[page #1 info],....., [page #n info]],
    number_of_values, type = int
    output: names and close values, type = [[All names],[All nearby values]]
    '''
    #key terms to search for
    key_name = []
    for name in name_arr:
        key_name.append(name[0])
    #all names
    all_names = []
    #all nearby values
    all_near_values = []
    for page in index:
        names = [] #add string and coordinate
        names_tup = [] #tuple of names
        values = [] #everything else
        values_tup = [] #tuples of values
        for i in range(len(page)):
            if page[i][1].upper() in key_name:
                for x in name_arr:
                    if page[i][1].upper() == x[0]:
                        names.append([page[i], x[1]])
                        names_tup.append(page[i][0])
            else:
                values.append(page[i])
                values_tup.append(page[i][0])

        values_tup = np.array(values_tup)
        #create a cKDTree
        tree = cKDTree(values_tup)
        for i in range(len(names_tup)):
            all_names.append(names[i])
            _, idx = tree.query(names_tup[i], k=number_of_values)
            x = []
            for j in idx:
                if names[i][1] == "int" and RepresentsInt(values[j][1]):
                    x.append(values[j])
                elif names[i][1] == "float" and RepresentsFloat(values[j][1]):
                    x.append(values[j])
            all_near_values.append(x)
    return [all_names, all_near_values]

def main():
    fp = open('Data/test_four.pdf', 'rb')
    parser = PDFParser(fp)
    doc = PDFDocument(parser)

    rsrcmgr = PDFResourceManager()
    laparams = LAParams()
    device = PDFPageAggregator(rsrcmgr, laparams=laparams)
    interpreter = PDFPageInterpreter(rsrcmgr, device)

    index = parse_structure(doc, interpreter, device)

    #print(index[1]) #all data for one page

    name_arr = [["HEIGHT", "float"], ["WIDTH", "float"]]
    name_arr_2 = [["SKU", "float"]]
    name_arr_3 = [["UPC", "float"]]

    all = parse_compare(name_arr_3, index, 30)

    #print all names and nearby values
    for i in range(len(all[0])):
        print(all[0][i])
        print(all[1][i])
        print("------")


main()
