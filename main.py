import os
import sys
from PyPDF2 import PdfFileReader, PdfFileMerger
from fpdf import FPDF


# args:
# <file1.pdf> <file2.pdf> ... <filen.pdf> outputFileName.pdf
# or: <folderPath> outputFileName.pdf


# returns list of tuples (fileName, fileLength)
def extract_data(pdf_files):
    files_data = []
    for name in pdf_files:
        with open(name, 'rb') as f:
            curr_file = PdfFileReader(f)
            curr_len = curr_file.numPages

            # get file name without extension and path
            curr_name = name[name.rfind("/") + 1: name.find('.pdf')]
            files_data.append((curr_name, curr_len))
    return files_data


# generates the index page according to list of tuples (fileName, fileLength)
def create_table_of_content(files_data):
    LINE_LENGTH = 60
    index = []
    pages_nums = []
    curr_page_num = 2

    for filename_length in files_data:
        spaces_count = "-" * (LINE_LENGTH - len(filename_length[0]) - len(str(filename_length[1] + curr_page_num)))
        curr_line = filename_length[0] + spaces_count + str(curr_page_num)
        curr_page_num += filename_length[1]
        pages_nums.append(curr_page_num)
        index.append(curr_line)

    # creating the table of content as temporary file
    pdf = FPDF(format='A4')
    pdf.add_page()
    pdf.set_font("Courier", size=12)

    # write text line by line
    for line_num, line in enumerate(index):
        pdf.cell(200, 10, txt=line, align="C", ln=line_num + 1)

    temp_file_name = "__temp_index_file__.pdf"
    pdf.output(temp_file_name)
    return temp_file_name


def merge_files(pdf_files):
    merger = PdfFileMerger()

    for pdf in pdf_files:
        merger.append(pdf)

    return merger


def add_links(file, rectangles_and_dest):
    # link = pdf.add_link()
    # pdf.set_link(link, page=pages_nums[line_num]) // this page num dosent exists yet, need to change program flow
    pass


def add_bookmarks(file, files_data):
    pass


def add_title(page, title):
    pass


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
    # if input("Reverse order? (y/n)\t").lower() == 'y':
    #     pdf_files.reverse()
    #     print("Reversed.") // commented for testing

    # init
    index_page = create_table_of_content(extract_data(pdf_files))
    merger = merge_files(pdf_files)
    merger.merge(0, index_page)

    # save and exit:
    output_name = args[-1]
    output_name = output_name + ".pdf" if not output_name.endswith(".pdf") else output_name

    merger.write(output_name)
    merger.close()

    # clean temp files
    if os.path.exists(index_page):
        os.remove(index_page)

    return


def remove_temp_files():
    pass


if __name__ == '__main__':
    main(sys.argv)
