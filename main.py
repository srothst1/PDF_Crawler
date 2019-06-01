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
import math

from parser import *
def main():
    fp = open('Data/test_four.pdf', 'rb')
    parser = PDFParser(fp)
    doc = PDFDocument(parser)

    rsrcmgr = PDFResourceManager()
    laparams = LAParams()
    device = PDFPageAggregator(rsrcmgr, laparams=laparams)
    interpreter = PDFPageInterpreter(rsrcmgr, device)

    index = parse_structure(doc, interpreter, device)

    name_arr = []

    num = int(input("please enter the number of keywords: "))

    for i in range(num):
        term = input("please enter the term (ex. HEIGHT): ")
        term = term.upper()
        type = input("please enter the type (ex. float): ")
        name_arr.append([term, type])

    all = parse_compare(name_arr, index, 30)
    all_names = all[0]
    all_values = all[1]

    print("Displaying most relavent data next to indicated term")
    scores = find_score(all_names, all_values)
    for i in range(len(scores)):
        print("Term, type pair")
        print(scores[i])

    print("PDF has been crawled!")

main()
