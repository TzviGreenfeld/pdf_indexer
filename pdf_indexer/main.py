import os
import sys
import pathlib
from PyPDF2 import PdfFileReader, PdfFileMerger, PdfFileWriter
from fpdf import FPDF


# args:
# <file1.pdf> <file2.pdf> ... <filen.pdf> outputFileName.pdf
# or: <folderPath> outputFileName.pdf


# returns list of tuples (fileName, length)
def extract_length(pdf_files):
    names_lengths = []
    for name in pdf_files:
        with open(name, 'rb') as f:
            curr_file = PdfFileReader(f)
            curr_len = curr_file.numPages
            curr_name = name[name.rfind("/") + 1: name.find('.pdf')]
            names_lengths.append((curr_name, curr_len))
    return names_lengths


# generates the index page according to list of tuples (fileName, length)
def create_index_page(names_lengths):
    LINE_LENGTH = 60
    index = []
    curr_page_num = 2
    for filename_length in names_lengths:
        spaces_count = "-" * (LINE_LENGTH - len(filename_length[0]) - len(str(filename_length[1] + curr_page_num)))
        curr_line = filename_length[0] + spaces_count + str(curr_page_num)
        curr_page_num += filename_length[1]
        index.append(curr_line)
    content = "\n".join(index)
    pdf = FPDF(format='A4')
    pdf.add_page()
    pdf.set_font("Courier", size=12)
    pdf.multi_cell(200, 10, txt=content, align="C")
    pdf.output("__temp_index_file__.pdf")
    return "__temp_index_file__.pdf"
    # string tested including hebrew (eng and hebrea causes rtl ltr issue)


def merge_files(pdf_files):
    merger = PdfFileMerger()

    for pdf in pdf_files:
        merger.append(pdf)

    return merger


def main(args):
    if len(args) == 1:
        print("No arguments found")
        return
    # get files or folder
    if len(args) == 3:
        # folder
        pdf_files = [args[1] + "/" + file_name for file_name in os.listdir(args[1]) if
                     file_name.lower().endswith(".pdf")]
    else:
        # files
        pdf_files = [file_name for file_name in args[:-1] if file_name.lower().endswith(".pdf")]

    pdf_files = sorted(pdf_files)
    
    print("Merging order:")
    print("\n".join(pdf_files))
    if input("Reverse order? (y/n)").lower() == 'y':
        pdf_files.reverse()
        print("Reversed.")

    index_page = create_index_page(extract_length(pdf_files))
    merger = merge_files(pdf_files)
    merger.merge(0, index_page)

    output_name = args[-1]
    output_name = output_name + ".pdf" if not output_name.endswith(".pdf") else output_name

    merger.write(output_name)
    merger.close()

    if os.path.exists(index_page):
        os.remove(index_page)


if __name__ == '__main__':
    main(sys.argv)
