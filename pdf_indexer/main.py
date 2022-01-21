import os
import sys

import PyPDF2
from PyPDF2 import PdfFileReader, PdfFileMerger, PdfFileWriter


# args:
# <file1.pdf> <file2.pdf> ... <filen.pdf> outputFileName.pdf
# or: <folderPath> outputFileName.pdf


# returns dictionary {fileName : length}
def extract_length(pdf_files):
    names_lengths = {name.removesuffix(".pdf"): None for name in pdf_files}

    for file in pdf_files:
        curr_file = PdfFileReader(open(file, 'rb'))
        names_lengths[file.removesuffix(".pdf")] = curr_file.numPages
        curr_file.close

    return names_lengths


# generates the index page according dictionary {fileName : length}
def create_index_page(names_lengths):
    LINE_LENGTH = 30
    index = []
    for filename, length in names_lengths.items():
        digits = len(length)
        index.append(f"{filename:<{LINE_LENGTH - digits}}")

    content = "\n".join(index)
    print(content)
    writer = PdfFileWriter()
    #write content
    return



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
    if len(args) == 2:
        # folder
        pdf_files = [file_name for file_name in os.listdir(args[1]) if file_name.lower().endswith(".pdf")]
    else:
        # files
        pdf_files = [file_name for file_name in args[:-1] if file_name.lower().endswith(".pdf")]

    merger = merge_files(pdf_files)

    index_page = create_index_page(extract_length(pdf_files))
    merger.merge(0, index_page)

    output_name = args[-1]
    output_name = output_name + ".pdf" if not output_name.endwith(".pdf") else output_name

    merger.write(output_name)
    merger.close()


if __name__ == '__main__':
    main(sys.argv)
