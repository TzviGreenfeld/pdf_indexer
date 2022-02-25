import os
from pdfrw import PdfReader, PdfWriter, PdfDict
from PyPDF2 import PdfFileReader, PdfFileMerger, PdfFileWriter
from PyPDF2.generic import RectangleObject
from fpdf import FPDF


class Doc:

    def __init__(self, files, dir, links=True, bookmarks=True):
        self.LINE_WIDTH = 200
        self.LINE_LENGTH = 60
        self.LINE_HEIGHT = 10

        self.files = files
        self.dir = dir
        self.links = links
        self.bookmarks = bookmarks
        self.files_data = None
        self.toc_cells_loc = []
        self.toc_page = self.create_table_of_content()
        self.merger = self.merge_files()
        self.generated_file = None

    def save(self, output_name):
        self.merger.merge(0, self.toc_page)
        output_name = output_name + ".pdf" if not output_name.endswith(".pdf") else output_name
        self.merger.write(output_name)
        self.merger.close()
        self.generated_file = output_name
        return

    def extract_data(self):
        """
        updates files_data according to self.files
        :return:
        """
        for name in self.files:
            with open(name, 'rb') as f:
                curr_file = PdfFileReader(f)
                curr_len = curr_file.numPages

                # get file name without extension and path
                curr_name = name[name.rfind("/") + 1: name.find('.pdf')]
                self.files_data.append((curr_name, curr_len))
        return

    def create_table_of_content(self):
        """
        generates the toc page according to list of tuples (fileName, fileLength)
        :return:
        """
        tale_of_content = []
        pages_nums = []
        index = []
        curr_page_num = 2

        for name_and_len in self.files_data:
            spaces_count = "-" * (self.LINE_LENGTH - len(name_and_len[0]) - len(str(name_and_len[1] + curr_page_num)))
            curr_line = name_and_len[0] + spaces_count + str(curr_page_num)
            index.append((name_and_len[0], curr_page_num))
            pages_nums.append(curr_page_num)
            curr_page_num += name_and_len[1]
            tale_of_content.append(curr_line)

        # creating the table of content as temporary file
        pdf = FPDF(format='A4')
        pdf.add_page()
        pdf.set_font("Courier", size=12)  # TODO: fix allignment for non fixed width fonts (split to 2 rects?)

        # write text line by line
        for line_num, line in enumerate(tale_of_content):
            rect = [pdf.get_x(), pdf.get_y(), None, None]
            pdf.cell(self.LINE_WIDTH, self.LINE_HEIGHT, txt=line, align="C", ln=2)
            rect[2], rect[3] = pdf.get_x(), pdf.get_y()
            self.toc_cells_loc.append(rect)

        temp_file_name = "__temp_index_file__.pdf"
        pdf.output(temp_file_name)

        self.files_data = index
        return temp_file_name

    def merge_files(self):
        """
        set self.merger PyPdf2.PdfFileMerger object with the concatenated files from self.files
        """
        merger = PdfFileMerger()

        for pdf in self.files:
            merger.append(pdf)
        return merger

    def add_bookmarks(self):
        output = PdfFileWriter()
        with open(self.toc_page, 'rb+') as f:
            generated_file = PdfFileReader(f)  # open input

            for i in range(generated_file.getNumPages()):
                output.addPage(generated_file.getPage(i))  # insert page

            for (name, dest) in self.files_data:
                output.addBookmark(name, dest - 1, parent=None)

            with open("bookmarked_" + self.toc_page, "wb+") as out:
                output.write(out)

        self.remove_temp_files(self.toc_page)
        return

    def add_links(self):
        output = PdfFileWriter()
        with open(self.toc_page, 'rb+') as f:
            generated_file = PdfFileReader(f)  # open input
            for page in range(generated_file.getNumPages()):
                current_page = generated_file.getPage(page)
                output.addPage(current_page)
            for line_num, name, dest in enumerate(self.files_data):
                x1, y1, x2, y2 = self.cells_pos[line_num]
                output.addLink(pagenum=0, pagedest=dest,
                               rect=RectangleObject([x1, y1, self.LINE_WIDTH, self.LINE_HEIGHT]))

                # for (name, dest) in files_data:
                # output.addBookmark(name, dest - 1, parent=None)

                with open("bookmarked_" + file, "wb+") as out:
                    pass
                output.write(out)
        self.remove_temp_files(file)
        return

    def add_title(page, title):
        pass

    def set_metadata(self, _Author = None, _Title = None, _Subject = None, _Keywords = None, _Producer = None, _Creator = None):
        pdf_reader = PdfReader(self.generated_file)
        metadata = PdfDict(Author=_Author,
                           Title=_Title,
                           Subject=_Subject,
                           Keywords=_Keywords,
                           Producer=_Producer,
                           Creator=_Creator)
        pdf_reader.Info.update(metadata)
        PdfWriter().write(self.generated_file, pdf_reader)


    def remove_temp_files(self, filename):
        """
        deletes temporary files
        :param filename: file path to delete
        """
        if os.path.exists(filename):
            os.remove(filename)


