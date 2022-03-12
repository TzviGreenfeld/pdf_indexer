import os
import sys
from tempfile import TemporaryFile

from PyPDF2 import PdfFileWriter, PdfFileReader
from fpdf import FPDF
from pdfrw import PageMerge, PdfReader, PdfWriter, PdfDict, IndirectPdfDict


def is_hebrew(s):
    return any("\u0590" <= c <= "\u05EA" for c in s)


class TableOfContent:
    LINE_LENGTH = 60
    LINE_WIDTH = 180
    LINE_HEIGHT = 10

    def __init__(self, files: list, file_name=None, bookmark=True):
        """"
        will only save file if file_name is not None
        """
        self.pdf = FPDF(format='A4')
        self.pdf.add_font('SansHeb', '', 'IBMPlexSansHebrew-ExtraLight.ttf', uni=True)  # hebrew
        self.files = files
        self.file_len = -1
        self.pages_data = self.extract_data()
        # create_table_of_content also updates self.file_len
        self.index = self.create_table_of_content()

        for i in range(self.file_len):
            self.pdf.add_page()

        self.write_toc_page()

        if file_name is not None:
            self.file_name = file_name
            self.merge()

        if bookmark:
            self.add_bookmarks()
        self.set_metadata()
        return

    def create_table_of_content(self):
        curr_page_num = 2
        index = {}
        for (file_name, file_len) in self.pages_data:
            index.update({file_name: curr_page_num})
            curr_page_num += file_len

        self.file_len = curr_page_num - 1
        return index

    def extract_data(self):
        files_data = []
        for file_name in self.files:
            curr_len = len(PdfReader(fname=file_name).pages)
            # get file name without extension and path
            curr_name = file_name[file_name.rfind("/") + 1: file_name.find('.pdf')]
            files_data.append((curr_name, curr_len))
        return files_data

    def write_toc_page(self):

        def dash(f_name, page, link):
            # adds dashed line between the
            x1 = self.pdf.get_string_width(f_name) + self.pdf.l_margin + 5
            y = self.pdf.get_y() + self.LINE_HEIGHT / 2
            x2 = self.LINE_WIDTH - self.pdf.get_string_width(page) + self.pdf.r_margin - 5
            self.pdf.link(x1, y, x2 - x1, self.LINE_HEIGHT / 3, link)
            self.pdf.dashed_line(x1, y, x2, y)
            return

        def write_hebrew(f_name, link):
            width = "_"*len(f_name)
            self.pdf.set_font("SansHeb", size=12)  # hebrew
            self.pdf.cell(self.LINE_WIDTH / 2, self.LINE_HEIGHT, txt=f_name[::-1], align="L", ln=0, link=link,
                          border=0, fill=0)
            self.pdf.set_font("Courier", size=18)
            return width

        # links setup
        links = []
        for entry in self.index.items():
            filename, page_num = entry
            self.pdf.page = page_num
            links.append(self.pdf.add_link())

        # page title
        self.pdf.page = 1
        self.pdf.set_font("Arial", size=30)
        self.pdf.cell(self.LINE_WIDTH, 3 * self.LINE_HEIGHT, txt="Table of content", align="C", ln=1)

        # write text line by line setup
        self.pdf.set_font("Courier", size=18)
        for curr_link_index, entry in enumerate(self.index.items()):
            filename, page_num = entry

            # write toc text to pdf with links
            curr_link = links[curr_link_index]
            self.pdf.set_link(curr_link, y=0.0, page=page_num)

            if is_hebrew(filename):
                w = write_hebrew(filename, curr_link)
                dash(w, str(page_num), curr_link)
            else:
                self.pdf.cell(self.LINE_WIDTH / 2, self.LINE_HEIGHT, txt=filename, align="L", ln=0, link=curr_link,
                              border=0, fill=0)
                dash(filename, str(page_num), curr_link)

            self.pdf.cell(self.LINE_WIDTH / 2, self.LINE_HEIGHT, txt=str(page_num), align="R", ln=1, link=curr_link,
                          border=0, fill=0)

        # credit testing
        # credit = "created by tzvigr"
        # self.pdf.set_font("helvetica", size=5)
        # w = self.pdf.get_string_width(credit)
        # self.pdf.set_text_color(230)
        # self.pdf.set_x(self.pdf.l_margin)
        # self.pdf.set_y(self.pdf.h )
        # self.pdf.cell(w, self.LINE_HEIGHT, txt=credit, align="L")

        return

    def save(self):
        self.pdf.page = self.file_len
        self.pdf.output(self.file_name)
        return

    def merge(self):
        writer = PdfWriter()
        for path in self.files:
            reader = PdfReader(path)
            writer.addpages(reader.pages)

        self.save()
        # open generated file with pdfrw
        temp_reader = PdfReader(self.file_name)
        generated_toc_file = PdfWriter()
        generated_toc_file.addpages(temp_reader.pages)

        # take a page from merged files and paste it on the generated file
        for page_num, page in enumerate(writer.pagearray):
            # page = PdfReader("merged.pdf").pages[0]
            PageMerge(generated_toc_file.pagearray[page_num + 1]).add(page, prepend=True).render()

        # save output
        generated_toc_file.write(self.file_name)
        return

    def add_bookmarks(self):
        temp = "__temp__.pdf"
        output = PdfFileWriter()
        if os.path.exists(self.file_name):
            os.rename(self.file_name, temp)
        with open(temp, 'rb+') as f:
            file = PdfFileReader(f)  # open input

            for i in range(file.getNumPages()):
                output.addPage(file.getPage(i))  # insert page

            for (name, dest) in self.index.items():
                output.addBookmark(name, dest - 1, parent=None)

            with open(self.file_name, "wb+") as out:
                output.write(out)
        os.remove(temp)
        return

    def set_metadata(self):
        creator = "https://github.com/TzviGreenfeld/pdf_indexer"
        title = self.file_name[:str(self.file_name).find(".pdf")]
        pdf_reader = PdfReader(self.file_name)
        metadata = PdfDict(Author=None,
                           Title=title,
                           Subject=None,
                           Keywords=None,
                           Producer="",
                           Creator=creator)
        pdf_reader.Info.update(metadata)
        PdfWriter().write(self.file_name, pdf_reader)


# if __name__ == '__main__':
#     folder = "sample/"
#     _files = [os.path.join(folder, file) for file in os.listdir(folder)]
#     name = "out.pdf"
#     toc = TableOfContent(_files, name)
#     toc.add_bookmarks()

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

    # # sort files
    # pdf_files = sorted(pdf_files)
    #
    # print("Merging order:")
    # print("\n".join(pdf_files))
    # if input("Reverse order? (y/n)\t").lower() == 'y':
    #     pdf_files.reverse()
    #     print("Reversed.")

    output_name = args[-1]
    output_name = output_name + ".pdf" if not output_name.endswith(".pdf") else output_name

    toc = TableOfContent(pdf_files, output_name)


if __name__ == '__main__':
    main(sys.argv)
