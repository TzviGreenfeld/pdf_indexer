import os
import sys

from pdfrw import PdfReader, PdfWriter, PdfDict
from PyPDF2 import PdfFileReader, PdfFileMerger, PdfFileWriter
from PyPDF2.generic import RectangleObject
from fpdf import FPDF


def remove_temp_files(filename):
    """
    deletes temporary files
    :param filename: file path to delete
    """
    if os.path.exists(filename):
        os.remove(filename)


class Doc:
    LINE_WIDTH = 200
    LINE_LENGTH = 60
    LINE_HEIGHT = 10
    TEMP_FILE = "__temp__.pdf"

    def __init__(self, files=None, files_dir=None, toc_page=True, links=True, bookmarks=True):

        # init
        if files_dir is None:
            self.files = files
        else:
            self.files = [files_dir + "/" + file_name for file_name in os.listdir(files_dir) if
                          file_name.lower().endswith(".pdf")]

        self.files_data = self.extract_data(self.files)
        if toc_page:
            if links:
                self.toc_cells_loc = []
            self.create_table_of_content()
            self.toc_page = self.TEMP_FILE

        self.merger = self.merge_files()

        self.bookmarked = None
        if bookmarks:
            self.add_bookmarks()

        # self.generated_file = None

    def save(self, output_name):
        remove_temp_files(self.TEMP_FILE)

        if self.bookmarked is not None:
            os.rename(self.bookmarked, output_name)
        else:
            self.merger.write(output_name)
            self.merger.close()

    def extract_data(self, files):
        """
        updates files_data according to self.files
        :return:
        """
        files_data = []
        for name in files:
            with open(name, 'rb') as f:
                curr_file = PdfFileReader(f)
                curr_len = curr_file.numPages

                # get file name without extension and path
                curr_name = name[name.rfind("/") + 1: name.find('.pdf')]
                files_data.append((curr_name, curr_len))
        return files_data

    def create_table_of_content(self):
        """
        generates the toc page according to list of tuples (fileName, fileLength)
        :return:
        """
        table_of_content = []
        pages_nums = []
        index = []
        curr_page_num = 2

        for name_and_len in self.files_data:
            spaces_count = "-" * (self.LINE_LENGTH - len(name_and_len[0]) - len(str(name_and_len[1] + curr_page_num)))
            curr_line = name_and_len[0] + spaces_count + str(curr_page_num)
            index.append((name_and_len[0], curr_page_num))
            pages_nums.append(curr_page_num)
            curr_page_num += name_and_len[1]
            table_of_content.append(curr_line)

        # creating the table of content as temporary file
        pdf = FPDF(format='A4')
        pdf.add_page()
        pdf.set_font("Courier", size=12)  # TODO: fix allignment for non fixed width fonts (split to 2 rects?)

        # write text line by line
        for line_num, line in enumerate(table_of_content):
            rect = [pdf.get_x(), pdf.get_y(), None, None]
            pdf.cell(self.LINE_WIDTH, self.LINE_HEIGHT, txt=line, align="C", ln=2)
            rect[2], rect[3] = pdf.get_x(), pdf.get_y()
            self.toc_cells_loc.append(rect)

        pdf.output(self.TEMP_FILE)

    def merge_files(self, add_toc_page=True):
        """
        merges files and toc if got True argument
        :param add_toc_page: true if table of content page is wanted
        :return: the merged file name
        """
        merger = PdfFileMerger()

        for pdf in self.files:
            merger.append(pdf)

        if add_toc_page:
            merger.merge(0, self.toc_page)

        return merger

    def add_bookmarks(self):
        output = PdfFileWriter()
        temp = "bookmark.pdf"
        self.save(temp)
        with open(temp, 'rb+') as f:
            generated_file = PdfFileReader(temp)  # open input

            for i in range(generated_file.getNumPages()):
                output.addPage(generated_file.getPage(i))  # insert page

            for (name, dest) in self.files_data:
                output.addBookmark(name, dest - 1, parent=None)
            self.bookmarked = temp
            with open(temp, "wb+") as out:
                output.write(out)

        return temp

    # def add_links(self):
    #     output = PdfFileWriter()
    #     with open(self.toc_page, 'rb+') as f:
    #         generated_file = PdfFileReader(f)  # open input
    #         for page in range(generated_file.getNumPages()):
    #             current_page = generated_file.getPage(page)
    #             output.addPage(current_page)
    #         for line_num, name, dest in enumerate(self.files_data):
    #             x1, y1, x2, y2 = self.cells_pos[line_num]
    #             output.addLink(pagenum=0, pagedest=dest,
    #                            rect=RectangleObject([x1, y1, self.LINE_WIDTH, self.LINE_HEIGHT]))
    #
    #             # for (name, dest) in files_data:
    #             # output.addBookmark(name, dest - 1, parent=None)
    #
    #             with open("bookmarked_" + file, "wb+") as out:
    #                 pass
    #             output.write(out)
    #     remove_temp_files(file)
    #     return

    def set_metadata(self, author=None, title=None, subject=None, keywords=None, producer=None, creator=None):
        pdf_reader = PdfReader(self.generated_file)
        metadata = PdfDict(Author=author,
                           Title=title,
                           Subject=subject,
                           Keywords=keywords,
                           Producer=producer,
                           Creator=creator)
        pdf_reader.Info.update(metadata)
        PdfWriter().write(self.generated_file, pdf_reader)


def main(args):
    if len(args) == 1:
        print("No arguments found")
        return

    # get files or folder
    if len(args) == 3:
        # folder
        doc = Doc(files_dir=args[1])
    else:
        # files
        pdf_files = [file_name for file_name in args[:-1] if file_name.lower().endswith(".pdf")]
        doc = Doc(files=pdf_files)

    output_name = args[-1]
    output_name = output_name + ".pdf" if not output_name.endswith(".pdf") else output_name

    doc.save(output_name)


if __name__ == '__main__':
    main(sys.argv)
