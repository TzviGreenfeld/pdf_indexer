import os
import sys
from PyPDF2 import PdfFileReader, PdfFileMerger, PdfFileWriter
from fpdf import FPDF

# args:
# <file1.pdf> <file2.pdf> ... <filen.pdf> outputFileName.pdf
# or: <folderPath> outputFileName.pdf

LINE_LENGTH = 60
LINE_WIDTH = 200
LINE_HEIGHT = 10


def remove_temp_files(filename):
    """
    deletes temporary files
    :param filename: file path to delete
    """
    if os.path.exists(filename):
        os.remove(filename)


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
    tale_of_content = []
    pages_nums = []
    index = []
    curr_page_num = 2

    for name_and_len in files_data:
        spaces_count = "-" * (LINE_LENGTH - len(name_and_len[0]) - len(str(name_and_len[1] + curr_page_num)))
        curr_line = name_and_len[0] + spaces_count + str(curr_page_num)
        index.append((name_and_len[0], curr_page_num))
        pages_nums.append(curr_page_num)
        curr_page_num += name_and_len[1]
        tale_of_content.append(curr_line)

    # creating the table of content as temporary file
    pdf = FPDF(format='A4')

    pdf.set_font("Courier", size=12) # TODO: fix allignment for non fixed width fonts (split to 2 rects?)

    # write text line by line
    for line_num, line in enumerate(tale_of_content):
        pdf.cell(LINE_WIDTH, LINE_HEIGHT, txt=line, align="C", ln=2)

    temp_file_name = "__temp_index_file__.pdf"
    pdf.output(temp_file_name)

    return temp_file_name, index


def merge_files(pdf_files):
    """
    :param pdf_files: list of pdf file names to merge
    :return: PyPdf2.PdfFileMerger object with the concatenated files
    """
    merger = PdfFileMerger()

    for pdf in pdf_files:
        merger.append(pdf)

    return merger


def add_bookmarks(file, files_data):
    output = PdfFileWriter()
    with open(file, 'rb+') as f:
        generated_file = PdfFileReader(f)  # open input

        for i in range(generated_file.getNumPages()):
            output.addPage(generated_file.getPage(i))  # insert page

        for (name, dest) in files_data:
            output.addBookmark(name, dest - 1, parent=None)

        with open("bookmarked_" + file, "wb+") as out:
            output.write(out)

    remove_temp_files(file)
    return


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
    if input("Reverse order? (y/n)\t").lower() == 'y':
        pdf_files.reverse()
        print("Reversed.") 

    # init
    table_of_content, index = create_table_of_content(extract_data(pdf_files))
    merger = merge_files(pdf_files)
    merger.merge(0, table_of_content)

    # save and exit:
    output_name = args[-1]
    output_name = output_name + ".pdf" if not output_name.endswith(".pdf") else output_name
    merger.write(output_name)
    merger.close()

    # add bookmarks?
    # TODO: implement user chioce
    if True:
        add_bookmarks(output_name, index)

    remove_temp_files(table_of_content)
    return


if __name__ == '__main__':
    main(sys.argv)
