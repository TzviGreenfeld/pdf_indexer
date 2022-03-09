import os
import sys

from pdfrw import PdfReader, PdfWriter, PdfDict
from PyPDF2 import PdfFileReader, PdfFileMerger, PdfFileWriter
from PyPDF2.generic import RectangleObject
from fpdf import FPDF


class Doc:
    LINE_WIDTH = 200
    LINE_LENGTH = 60
    LINE_HEIGHT = 10

    def __init__(self, files=None, files_dir=None, toc_page=True, bookmarks=True):
        self.curr_file = None
        self.temp_files = []
        # init
        if files_dir is None:
            self.files = files
        else:
            self.files = [files_dir + "/" + file_name for file_name in os.listdir(files_dir) if
                          file_name.lower().endswith(".pdf")]

        self.files_data = self.extract_data(self.files)

        if toc_page:
            self.toc_cells_loc = []
            self.toc_page = self.create_table_of_content()
            self.merger = self.merge_files(True)
            self.curr_file = self.save("merged_with_toc.pdf")
            self.add_links()
        else:
            self.merger = self.merge_files(False)
            self.curr_file = self.save("merged.pdf")
            self.temp_files.append("merged.pdf")

        if bookmarks:
            self.add_bookmarks()

    def save(self, output_name):
        if self.curr_file is not None:
            os.rename(self.curr_file, output_name)
        else:
            self.merger.write(output_name)
        return output_name

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
        curr_page_num = 2

        for name, length in self.files_data:
            spaces_count = "-" * (self.LINE_LENGTH - len(name) - len(
                str(length + curr_page_num)))  # change it to depend on the font
            curr_line = name + spaces_count + str(curr_page_num)
            pages_nums.append(curr_page_num)
            curr_page_num += length
            table_of_content.append(curr_line)

        # creating the table of content as temporary file
        pdf = FPDF(format='A4')
        pdf.add_page()
        pdf.set_font("Courier", size=12)  # TODO: fix allignment for non fixed width fonts (split to 2 rects?)

        # write text line by line
        for line in table_of_content:
            rect = [pdf.get_x(), pdf.get_y(), pdf.get_x() + self.LINE_WIDTH, pdf.get_y() + self.LINE_HEIGHT]
            pdf.cell(self.LINE_WIDTH, self.LINE_HEIGHT, txt=line, align="C", ln=2)
            self.toc_cells_loc.append(rect)
        temp = "toc.pdf"
        self.temp_files.append(temp)
        pdf.output(temp)
        return temp

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
            merger.close()
        return merger

    def add_bookmarks(self):
        output = PdfFileWriter()
        temp = "bookmark.pdf"
        self.temp_files.append(temp)
        with open(self.curr_file, 'rb+') as f:
            generated_file = PdfFileReader(temp)  # open input

            for i in range(generated_file.getNumPages()):
                output.addPage(generated_file.getPage(i))  # insert page

            for (name, dest) in self.files_data:
                output.addBookmark(name, dest - 1, parent=None)
            self.curr_file = temp
            with open(temp, "wb+") as out:
                output.write(out)

        return temp

    def add_links(self):
        output = PdfFileWriter()
        with open(self.curr_file, 'rb+') as f:
            generated_file = PdfFileReader(f)  # open input
            for page in range(generated_file.getNumPages()):
                current_page = generated_file.getPage(page)
                output.addPage(current_page)
            for line_num, (name, dest) in enumerate(self.files_data):
                output.addLink(pagenum=0, pagedest=dest,
                               rect=RectangleObject(self.toc_cells_loc[line_num]))

            with open(self.curr_file, "wb+") as out:
                output.write(out)

    # def set_metadata(self, author=None, title=None, subject=None, keywords=None, producer=None, creator=None):
    # pdf_reader = PdfReader(self.generated_file)
    # metadata = PdfDict(Author=author,
    #                    Title=title,
    #                    Subject=subject,
    #                    Keywords=keywords,
    #                    Producer=producer,
    #                    Creator=creator)
    # pdf_reader.Info.update(metadata)
    # PdfWriter().write(self.generated_file, pdf_reader)

    def remove_temp_files(self):
        """
        clean
        """

        # for filename in self.temp_files:
        #     if os.path.exists(filename):
        #         os.remove(filename)


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
    doc.remove_temp_files()


if __name__ == '__main__':
    main(sys.argv)
