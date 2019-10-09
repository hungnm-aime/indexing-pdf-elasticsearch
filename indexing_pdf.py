import os
from utils.get_paths import PDF_PATH
from tika import parser

# import libraries to help read and create PDF
import PyPDF2
from fpdf import FPDF
import base64
import json
# import the Elasticsearch low-level client library
from elasticsearch import Elasticsearch

# create a new client instance of Elasticsearch
elastic_client = Elasticsearch(hosts=["localhost"])
# create a new PDF object with FPDF
pdf = FPDF()


def get_pdfs(path):
    files = []
    for r, d, f in os.walk(path):
        for file in f:
            if '.pdf' in file:
                files.append(os.path.join(r, file))
    return files


def index_pdf_2_es(path):
    # get the PDF path and read the file
    read_pdf = PyPDF2.PdfFileReader(path, strict=False)
    print(read_pdf)

    # get the read object's meta info
    pdf_meta = read_pdf.getDocumentInfo()

    # get the page numbers
    num = read_pdf.getNumPages()
    print("PDF pages:", num)

    # create a dictionary object for page data
    all_pages = {}

    # put meta data into a dict key
    all_pages["meta"] = {}

    # Use 'iteritems()` instead of 'items()' for Python 2
    for meta, value in pdf_meta.items():
        print(meta, value)
        all_pages["meta"][meta] = value

    # iterate the page numbers
    for page in range(num):
        data = read_pdf.getPage(page)
        # page_mode = read_pdf.getPageMode()

        # extract the page's text
        page_text = data.extractText()

        # put the text data into the dict
        all_pages[page] = page_text
        print("page: ", page)
        print(page_text)

    # create a JSON string from the dictionary
    json_data = json.dumps(all_pages)
    print("\nJSON:", json_data)
    bytes_string = bytes(json_data, 'utf-8')
    print("\nbytes_string:", bytes_string)

    # convert bytes to base64 encoded string
    encoded_pdf = base64.b64encode(bytes_string)
    encoded_pdf = str(encoded_pdf)
    print("\nbase64:", encoded_pdf)

    body_doc = {"data": encoded_pdf}

    # call the index() method to index the data, if no pass id then id automatically generated
    # result = elastic_client.index(index="pdf", doc_type="_doc",id=112,  body=body_doc)
    # print(result)
    # return encoded_pdf


# index_pdf_2_es('/Users/manhhung/Documents/workspace/aime/es/pdf_files/1.pdf')

# for file in get_pdfs(PDF_PATH):
#     index_pdf_2_es(file)


def parse_tika(path):

    # Parse data from file
    file_data = parser.from_file(path)
    # Get files text content
    text = file_data['content']
    print(text)


parse_tika('/Users/manhhung/Documents/workspace/aime/es/pdf_files/3.pdf')